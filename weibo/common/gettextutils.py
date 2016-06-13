# author leidong

"""
gettext for common modules.

Usual usage in an common module:

    from auth_login.common.gettextutils import _
"""

import gettext
import six


#mes = gettext.bindtextdomain('messages')
#_t = gettext.translation(mes)
_t = gettext

def _(msg):
    if six.PY2:
        return _t.gettext(msg)
    return _t.ugettext(msg)
