#coding: utf-8
#author zwei
#email suifeng20@hotmail.com

import os
import sys
import errno
import inspect

from six import moves
from weibo import version
from weibo.common import exception

_BINFILE = version.OBJECT_CONF

def _normalize_group_name(group_name):
    if group_name == 'DEFAULT':
        return group_name
    return group_name.lower()

def _get_binary_name():
    return os.path.basename(inspect.stack()[-1][1])

def _fixpath(p):
    """Apply tilde expansion and absolutization to a path."""
    return os.path.abspath(os.path.expanduser(p))

def _get_config_dirs(project=None):
    """ ~/.foo.conf
        ~/.foo/foo.conf
        /etc/foo.conf
        /etc/foo/foo.conf
    """
    cfg_dirs = [
        _fixpath(os.path.join('~', '.' + project)) if project else None,
        _fixpath('~'),
        os.path.join('/etc', project) if project else None,
        '/etc'
    ]
    return cfg_dirs


def _find_default_config(project=None, exten='.conf'):
    """ ~/.foo.conf
        ~/.foo/foo.conf
        /etc/foo.conf
        /etc/foo/foo.conf
    """
    config_files = []
    if project is None:
        project = _get_binary_name()
    default_dirs = _get_config_dirs(project)
    for pdir in default_dirs:
        tempfile = os.path.join(pdir, project + exten)
        if os.path.exists(tempfile):
            config_files.append(tempfile)
    return config_files


def find_config_files(pdir=None, pfile=None, exten='.conf'):
    global _BINFILE
    config_files = []
    confdir = os.path.expanduser('~/.')
    binfile = _get_binary_name() + exten
    if not _BINFILE:
        _BINFILE = binfile
    pdir = pdir or confdir
    if not os.path.exists(pdir):
        os.mkdir(pdir, 0o755)
    if pfile is None:
        pfile = os.path.join(confdir, binfile)
    if os.path.exists(pfile):
        config_files.append(pfile)
    config_files.extend(_find_default_config())
    return list(moves.filter(bool, config_files))


class ParseError(Exception):
    def __init__(self, message, lineno, line):
        self.msg = message
        self.line = line
        self.lineno = lineno

    def __str__(self):
        return 'at line %d, %s: %r' % (self.lineno, self.msg, self.line)

class BaseParser(object):
    lineno = 0
    parse_exc = ParseError

    def _assignment(self, key, value):
        self.assignment(key, value)
        return None, []

    def _get_section(self, line):
        if not line.endswith(']'):
            return self.error_no_section_end_bracket(line)
        if len(line) <= 2:
            return self.error_no_section_name(line)
        return line[1:-1]

    def _split_key_value(self, line):
        colon = line.find(':')
        equal = line.find('=')
        if colon < 0 and equal < 0:
            return self.error_invalid_assignment(line)

        if colon < 0 or (equal >= 0 and equal < colon):
            key, value = line[:equal], line[equal + 1:]
        else:
            key, value = line[:colon], line[colon + 1:]

        value = value.strip()
        if value and value[0] == value[-1] and value.startswith(("\"", "'")):
            value = value[1:-1]

        return key.strip(), [value]

    def parse(self, lineiter):
        key = None
        value = []

        for line in lineiter:
            self.lineno += 1

            line = line.rstrip()
            if not line:
                # Blank line, ends multi-line values
                if key:
                    key, value = self._assignment(key, value)
                continue
            elif line.startswith((' ', '\t')):
                # Continuation of previous assignment
                if key is None:
                    self.error_unexpected_continuation(line)
                else:
                    value.append(line.lstrip())
                continue

            if key:
                # Flush previous assignment, if any
                key, value = self._assignment(key, value)

            if line.startswith('['):
                # Section start
                section = self._get_section(line)
                if section:
                    self.new_section(section)
            elif line.startswith(('#', ';')):
                self.comment(line[1:].lstrip())
            else:
                key, value = self._split_key_value(line)
                if not key:
                    return self.error_empty_key(line)
        if key:
            # Flush previous assignment, if any
            self._assignment(key, value)

    def assignment(self, key, value):
        """Called when a full assignment is parsed."""
        raise NotImplementedError()

    def new_section(self, section):
        """Called when a new section is started."""
        raise NotImplementedError()

    def comment(self, comment):
        """Called when a comment is parsed."""
        pass

    def error_empty_key(self, line):
        raise self.parse_exc('Key cannot be empty', self.lineno, line)

    def error_no_section_end_bracket(self, line):
        raise self.parse_exc('Invalid section (must end with ])',
                             self.lineno, line)

    def error_unexpected_continuation(self, line):
        raise self.parse_exc('Unexpected continuation line',
                             self.lineno, line)

    def error_no_section_name(self, line):
        raise self.parse_exc('Empty section name', self.lineno, line)

class ConfigParser(BaseParser):
    def __init__(self, filename, sections):
        super(ConfigParser, self).__init__()
        self.filename = filename
        self.sections = sections
        self._normalized = None
        self.section = None

    def _add_normalized(self, normalized):
        self._normalized = normalized

    def parse(self):
        with open(self.filename) as f:
            return super(ConfigParser, self).parse(f)

    def new_section(self, section):
        self.section = section
        self.sections.setdefault(self.section, {})

        if self._normalized is not None:
            self._normalized.setdefault(_normalize_group_name(self.section),{})

    def assignment(self, key, value):
        if not self.section:
            raise self.error_no_section()

        value = '\n'.join(value)

        def append(sections, section):
            sections[section].setdefault(key, [])
            sections[section][key].append(value)

        append(self.sections, self.section)
        if self._normalized is not None:
            append(self._normalized, _normalize_group_name(self.section))

    def parse_exc(self, msg, lineno, line=None):
        return ParseError(msg, lineno, line, self.filename)

    def error_no_section(self):
        return self.parse_exc('Section must be started before assignment',
                              self.lineno)

    @classmethod
    def _parse_file(cls, config_file, namespace):
        """Parse a config file and store any values in the namespace.

        :raises: ConfigFileParseError, ConfigFileValueError
        """
        config_file = _fixpath(config_file)

        sections = {}
        normalized = {}
        parser = cls(config_file, sections)
        parser._add_normalized(normalized)

        try:
            parser.parse()
        except ParseError as pe:
            raise exception.ConfigFileParseError(pe.filename, str(pe))
        except IOError as err:
            if err.errno == errno.ENOENT:
                #namespace._file_not_found(config_file)
                return
            if err.errno == errno.EACCES:
                #namespace._file_permission_denied(config_file)
                return
            raise

        namespace._add_parsed_config_file(sections, normalized)

class _SubNamespace(object):
    def __init__(self, group):
        self.group = group
        self.keys = []

    def setattr(self, key, value):
        self.keys.append(key)
        setattr(self, key, value)

    def getattr(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise NoSuchOptError(key=key)

    def __getattribute__(self, k):
        return object.__getattribute__(self, k)

    def __setattr__(self, k, v):
        self.__dict__[k] = v

    def __getattr__(self, k):
        return self.__getitem__(k)

    def __getitem__(self, k):
        v = self.__dict__.get(k)
        if isinstance(v, list) and len(v) < 2:
            v = ''.join(v)
        return v

    def __str__(self):
        return "<Sections [%s] all opts [%s]>" % (self.group,
                                                  ','.join(self.keys))

    def __repr__(self):
        return self.__str__()

class _Namespace(_SubNamespace):
    def __init__(self):
        self.all_groups = []
        self.groups = []
        self.opts = {}
        self.namespaces = {}
        self.sections = {}

    @property
    def prase_sections(self):
        for group in self.groups:
            self.setattr(group)
            if group == "DEFAULT":
                self.set_default_opts()

        for group in self.groups:
            section = self.sections[group]
            sub = self.namespaces[group]
            for k, v in section.items():
                v = self.set_list_and_bool_opts(v)
                sub.setattr(k, v)

    def set_list_and_bool_opts(self, v):
        if (len(v) < 2):
            value_list = v[0].split(',')
            if len(value_list) > 1:
                value_lists = []
                for value_l in value_list:
                    value_l_str = value_l.strip()
                    if value_l_str:
                        value_lists.append(value_l_str)

                    if len(value_lists):
                        value = value_lists
            else:
                subvalue = ''.join(v)
                if subvalue == "True" or subvalue == "true":
                    subvalue = True
                if subvalue == "False" or subvalue == "false":
                    subvalue = False
                value = subvalue
            return value
        return v

    def set_default_opts(self):
        for key, value in self.sections.get("DEFAULT").items():
            value = self.set_list_and_bool_opts(value)
            setattr(self, key, value)

    def setattr(self, group):
        if group not in self.namespaces.keys():
            sub = _SubNamespace(group)
            self.namespaces.setdefault(group, sub)
            return setattr(self, group, sub)

    def _add_parsed_sections(self, sections):
        self.sections = sections
        for g in sections.keys():
            self.all_groups.append(g if g not in self.groups else None)
        self.all_groups=(filter(bool, self.all_groups))
        self.groups = sections.keys()
        self.prase_sections

    def _add_parsed_normalized(self, normalized):
        pass

    def _add_parsed_config_file(self, sections, normalized):
        self._add_parsed_sections(sections)
        self._add_parsed_normalized(normalized)

    def __setitem__(self, key, value, group=None):
        if group is None:
            self.set_default_opts(key, value)
        if group in self.namespaces.keys():
            sub = self.namespcaces[group]
            sub.setattr(key, value)

    def __getitem__(self, k):
        v = self.__dict__.get(k)
        if isinstance(v, list) and len(v) < 2:
            v = ''.join(v)
        return v

    def __str__(self):
        return "Namespace all [%s] Group" % ','.join(self.all_groups)

class ConfigOpts(object):
    def __init__(self):
        """Construct a ConfigOpts object."""
        self.groups = []
        self._opts = {}
        self.namespace = _Namespace()
        self.config_files = []

    def __call__(self, dev_file=None, project=None, prog=None):
        config_files = find_config_files(project, prog)
        if dev_file is not None:
            config_files.append(dev_file)
        if len(config_files) < 1:
            raise exception.LogConfigError(binfile=_BINFILE)
        for config_file in config_files:
            ConfigParser._parse_file(config_file, self.namespace)

        self.groups = self.namespace.all_groups

    def __getattr__(self, name):
        try:
            return self.namespace[name]
        except Exception:
            raise exception.NoSuchOptError(key=name)
    def __getitem__(self, k):
        return self.__getattr__(k)

CONF = ConfigOpts()

if __name__ == '__main__':
    CONF('weibo.confbak')
    print(CONF.enable_multitargets)
    print(CONF.DEFAULT.enable_multitargets)
    print(CONF.t1.nickname)
    print(CONF['t1'].nickname)
