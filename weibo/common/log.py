#author zwei
#email suifeng20@hotmail.com

import logging

def setup(conf, product_name, version='unknown'):
    """ Setup logging for the current product"""
    if conf.log_config_append:
        pass
    else:
        _setup_logging_from_conf(conf, product_name, version)


class BaseLoggerAdapter(logging.LoggerAdapter):
    pass

def _setup_logging_from_conf(conf, project, version):
    log_root = getLogger(None).logger
    for handler in log_root.handlers:
        log_root.removeHandler(handler)

    logpath  = _get_log_file_path(conf)
    if logpath:
        pass


_loggers = {}
def getLogger(name=None, project="unknown", version="unknown"):
    """ Build a logger with the given name.
    param name: The name for the logger . eg: ``'__name__'``.
    type name: string
    param project: eg: ``'loginserver'``
    type project: string
    param version: eg: ``'2016.2.1'``
    type version: string
    """
    if name not in _loggers:
        _loggers[name] = BaseLoggerAdapter(logging.getLogger(name),
                                           {'project': project,
                                            'version': version})
    return _loggers[name]
