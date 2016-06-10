""" SAMO version info """
from pbr import version as pbr_version

OBJECT="weibo"
OBJECT_CONF="weibo.conf"
VERSION = 1.0
INIT_VERSION = 0

WEIBO_PACKAGE = None  # OS distro weibo version suffix

loaded = False
version_info = pbr_version.VersionInfo('weibo')
version_string = version_info.version_string
