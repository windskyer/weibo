"""Generic Weibo base class for all workers that run on hosts."""
import os
import random

from weibo import exception
from weibo import version
from weibo.common import cfg
from weibo.common import service
from weibo.db import api as db
from weibo.common.gettextutils import _, _LW
from weibo.common import log as logging
from weibo.common import importutils

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

# NOTE(geekinutah): By default drivers wait 5 seconds before reporting
INITIAL_REPORTING_DELAY = 5


class Service(service.Service):
    """Service object for binaries running on hosts.

    A service takes a manager and enables rpc by listening to queues based
    on topic. It also periodically runs tasks on the manager and reports
    it state to the database services table."""

    def __init__(self, host, binary, topic, manager, report_interval=None,
                 periodic_interval=None, periodic_fuzzy_delay=None,
                 periodic_enable=False, periodic_interval_max=None,
                 *args, **kwargs):
        super(Service, self).__init__()
        self.host = host
        self.binary = binary
        self.topic = topic
        self.manager_class_name = manager
        manager_class = importutils.import_class(self.manager_class_name)
        self.manager = manager_class(host=self.host, *args, **kwargs)
        self.report_interval = report_interval
        self.periodic_enable = periodic_enable
        self.periodic_fuzzy_delay = periodic_fuzzy_delay
        self.periodic_interval_max = periodic_interval_max
        self.saved_args, self.saved_kwargs = args, kwargs
        self.backdoor_port = None
        self.report_interval = report_interval

    def start(self):
        version_string = version.version_string()
        LOG.audit(_('Starting %(topic)s node (version %(version_string)s)'),
                  {'topic': self.topic, 'version_string': version_string})
        self.model_disconnected = False
        try:
            service_ref = db.service_get_by_args(ctxt,
                                                 self.host,
                                                 self.binary)
            self.service_id = service_ref['id']
        except exception.NotFound:
            self._create_service_ref(ctxt)

        # self.conn = rpc.create_connection(new=True)
        LOG.debug(_("Creating Consumer connection for Service %s") %
                  self.topic)

        if self.report_interval:
            self.tg.add_timer(self.report_interval,
                              self.report_state,
                              initial_delay=INITIAL_REPORTING_DELAY)

        if self.periodic_enable:
            if self.periodic_fuzzy_delay:
                initial_delay = random.randint(0, self.periodic_fuzzy_delay)
            else:
                initial_delay = None

            self.tg.add_dynamic_timer(self.periodic_tasks,
                                      initial_delay=initial_delay,
                                      periodic_interval_max=
                                      self.periodic_interval_max)

    def _create_service_ref(self):
        service_ref = db.service_create({'host': self.host,
                                         'binary': self.binary,
                                         'topic': self.topic,
                                         'report_count': 0,
                                         })
        self.service_id = service_ref['id']

    def __getattr__(self, key):
        manager = self.__dict__.get('manager', None)
        return getattr(manager, key)

    @classmethod
    def create(cls, host=None, binary=None, topic=None, manager=None,
               report_interval=None, periodic_enable=None,
               periodic_fuzzy_delay=None, periodic_interval_max=None):
        """Instantiates class and passes back application object.

        :param host: defaults to CONF.host
        :param binary: defaults to basename of executable
        :param topic: defaults to bin_name - 'nova-' part
        :param manager: defaults to CONF.<topic>_manager
        :param report_interval: defaults to CONF.report_interval
        :param periodic_enable: defaults to CONF.periodic_enable
        :param periodic_fuzzy_delay: defaults to CONF.periodic_fuzzy_delay
        :param periodic_interval_max: if set, the max time to wait between runs

        """
        if not host:
            host = CONF.host
        if not binary:
            binary = os.path.basename(sys.argv[0])
        if not topic:
            topic = binary.rpartition('weibo-')[2]
        if not manager:
            manager_cls = ('%s_manager' %
                           binary.rpartition('weibo-')[2])
            manager = CONF[manager_cls]
        if report_interval is None:
            report_interval = CONF.report_interval
        if periodic_enable is None:
            periodic_enable = CONF.periodic_enable
        if periodic_fuzzy_delay is None:
            periodic_fuzzy_delay = CONF.periodic_fuzzy_delay

        service_obj = cls(host, binary, topic, manager,
                          report_interval=report_interval,
                          periodic_enable=periodic_enable,
                          periodic_fuzzy_delay=periodic_fuzzy_delay,
                          periodic_interval_max=periodic_interval_max)

        return service_obj

    def kill(self):
        """Destroy the service object in the datastore."""
        self.stop()
        try:
            self.service_ref.destroy()
        except exception.NotFound:
            LOG.warning(_LW('Service killed that has no database entry'))

    def stop(self):
        super(Service, self).stop()

    def periodic_tasks(self, raise_on_error=False):
        """Tasks to be run at a periodic interval."""
        return self.manager.periodic_tasks(ctxt, raise_on_error=raise_on_error)

    def report_state(self):
        """Update the state of this service in the datastore."""
        state_catalog = {}
        try:
            try:
                service_ref = db.service_get(self.service_id)
            except exception.NotFound:
                LOG.debug(_('The service database object disappeared, '
                            'Recreating it.'))
                self._create_service_ref()
                service_ref = db.service_get(self.service_id)

            state_catalog['report_count'] = service_ref['report_count'] + 1

            db.service_update(self.service_id, state_catalog)

            # TODO(termie): make this pattern be more elegant.
            if getattr(self, 'model_disconnected', False):
                self.model_disconnected = False
                LOG.error(_('Recovered model server connection!'))

        # TODO(vish): this should probably only catch connection errors
        except Exception:  # pylint: disable=W0702
            if not getattr(self, 'model_disconnected', False):
                self.model_disconnected = True
                LOG.exception(_('model server went away'))


def process_launcher():
    return service.ProcessLauncher(CONF)

# NOTE(vish): the global launcher is to maintain the existing
#             functionality of calling service.serve +
#             service.wait
_launcher = None


def serve(server, workers=None):
    global _launcher
    if _launcher:
        raise RuntimeError(_('serve() can only be called once'))

    _launcher = service.launch(CONF, server, workers=workers)


def wait():
    try:
        _launcher.wait()
    except KeyboardInterrupt:
        _launcher.stop()


class Launcher(object):
    def __init__(self):
        self.launch_service = serve
        self.wait = wait


def get_launcher():
    # Note(lpetrut): ProcessLauncher uses green pipes which fail on Windows
    # due to missing support of non-blocking I/O pipes. For this reason, the
    # service must be spawned differently on Windows, using the ServiceLauncher
    # class instead.
    if os.name == 'nt':
        return Launcher()
    else:
        return process_launcher()
