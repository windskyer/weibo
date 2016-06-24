#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2016
# author: zwei
'''
Crawler same weibo info
'''
import os
import sys
import argparse

possible_topdir = os.path.normpath(os.path.join(os.path.abspath(__file__),
                                                os.pardir,
                                                os.pardir,
                                                os.pardir))
if os.path.exists(os.path.join(possible_topdir,
                               "weibo",
                               "__init__.py")):
    sys.path.insert(0, possible_topdir)

from weibo import service
from weibo import simu
from weibo import version
from weibo import download
from weibo import userdata
from weibo import exception
from weibo.db import migration
from weibo.db import api as session
from weibo.common import cfg
from weibo.common.gettextutils import _
from weibo.common import log as logging

CONF = cfg.CONF
dev_conf = os.path.join(possible_topdir,
                        'etc',
                        'weibo.conf')


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ArgumentParser, self).__init__(*args, **kwargs)

    def error(self, message):
        """error(message: string)

        Prints a usage message incorporating the message to stderr and
        exits.
        """
        self.print_usage(sys.stderr)
        # FIXME(lzyeval): if changes occur in argparse.ArgParser._check_value
        choose_from = ' (choose from'
        progparts = self.prog.partition(' ')
        self.exit(2, "error: %(errmsg)s\nTry '%(mainp)s help %(subp)s'"
                  " for more information.\n" %
                  {'errmsg': message.split(choose_from)[0],
                   'mainp': progparts[0],
                   'subp': progparts[2]})


def config_file(prog='weibo', description=None):
    _oparser = ArgumentParser(prog=prog,
                              description=description,
                              add_help=False,
                              epilog='See "weibo help subcommand" '
                              'for help on a specific command.',
                              )
    _oparser.add_argument('-h', '--help',
                          action='store_true',
                          help=argparse.SUPPRESS)

    _oparser.add_argument('-V', '--version',
                          action='version',
                          version=version.VERSION,
                          )

    _oparser.add_argument('-d', '--debug',
                          action='store_true',
                          help="Print debugging output")

    _oparser.add_argument('--config-file',
                          nargs='?',
                          help='Path to a config file to use. Multiple config '
                          'files can be specified, with values in later '
                          'files taking precedence. The default files ',
                          )
    _oparser.add_argument('--config_file',
                          help=argparse.SUPPRESS,
                          )
    return _oparser.parse_args()

args = config_file()

if os.path.exists(dev_conf):
    CONF(dev_conf)
else:
    if args.config_file:
        if os.path.exists(args.config_file):
            CONF(args.config_file)
        else:
            CONF()
    else:
        CONF()
#logging.setup('weibo')


def db_sync(version=None):
    """Sync the database up to the most recent version."""
    return migration.db_sync(version)


def db_version(self):
    """Print the current database version."""
    print migration.db_version()


def client():
    # API 参考 http://open.weibo.com/wiki/%E5%BE%AE%E5%8D%9AAPI
    # 使用参考 https://github.com/lxyu/weibo
    udata = userdata.Userdata()
    udata.save_all_users()


def login():
    # 首先登入
    # import pdb;pdb.set_trace()
    simu.Simu.check_login()

    # 模拟登陆的功能扩展待完善
    simulogin = simu.Simu()

    try:
        simulogin.detail()
    except exception.DetailNotFound:
        simu.Simu.reset_login()
        simulogin = simu.Simu()
        simulogin.detail()
    simulogin.save_all_data()


def pweibo():
    config_file()


def pmain():
    login()


def amain():
    client()


def dbmain():
    db_sync()


def dnmain():
    download.main()


def test():
    launcher = service.get_launcher()
    LOG = logging.getLogger(__name__)
    service_started = False

    if isinstance(CONF.enable_multiusers, list):
        for backend in CONF.enable_multiusers:
            backend_host = getattr(CONF, backend).backend_host
            host = "%s@%s" % (backend_host or CONF.host, backend)
            try:
                server = service.Service.create(host=host,
                                                service_name=backend,
                                                binary='weibo')
            except Exception:
                msg = _('weibo service %s failed to start.') % host
                LOG.exception(msg)
            else:
                # Dispose of the whole DB connection pool here before
                # starting another process.  Otherwise we run into cases where
                # child processes share DB connections which results in errors.
                session.dispose_engine()
                launcher.launch_service(server)
                service_started = True
    else:
        server = service.Service.create(binary='weibo')
        launcher.launch_service(server)
        service_started = True

    if not service_started:
        msg = _('No volume service(s) started successfully, terminating.')
        LOG.error(msg)
        sys.exit(1)

    launcher.wait()

if __name__ == '__main__':
    dbmain()
