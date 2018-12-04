#!/usr/bin/env python

from    __future__ import print_function
import  os, re

def ssh_bool(s):
    ''' Parse an ssh_config-style boolean value.

        This isn't really defined anywhere, as far as I can tell
        (the manpages just use `yes` and `no`, though I'm sure that
        `true` and `false` are allowed), so I just pick a reasonable
        range of words that cannot be confused with some other kind
        of value (e.g., I don't accept 0 as false).
    '''
    if s is True :                      return True
    if s is False:                      return False
    if s.lower() in ('yes', 'true'):    return True
    if s.lower() in ('no', 'false'):    return False
    raise Config.ConfigError('Invalid boolean value: {}'.format(s))

class Compartment():
    ' The configuration for a single compartment. '

    def __init__(self, name):
        self.name = name
        self.keyfiles = []
        self._confirm = None

    def confirm(self):
        ' Do we request confirmation when loading key into agent? '
        if self._confirm is None:
            return True             # unset
        return self._confirm

    def set_confirm(self, value):
        ''' Set confirm value if not already set.
            This accepts bool or an ssh_config-syntax string value.
        '''
        b = ssh_bool(value)
        if self._confirm is None:
            self._confirm = b

class Config():
    ' The compartments and other configuration read from the config file. '

    class ConfigError(RuntimeError):
        pass

    @staticmethod
    def load(input):
        parser = re.compile(r'(?:\s*)(\w+)(?:\s*=\s*|\s+)(.+)')
        conf = Config()
        compartments = conf.compartments
        curname = None
        for line in input:
            match = parser.match(line)
            if not match: continue
            key = match.group(1).lower(); value = match.group(2)
            if key == 'ck_compartment':
                curname = value
                compartments.setdefault(curname, Compartment(curname))
                continue
            if key == 'ck_keyfile':
                compartments[curname].keyfiles.append(value)
                continue
            if key == 'ck_confirm':
                compartments[curname].set_confirm(value)
                continue
            if key == 'ck_host' or key == 'ck_compartmentname':
                #   Currently unimplemented.
                curname = None
                continue
            if key.startswith('ck_'):
                raise Config.ConfigError(
                    'Unknown config parameter: {}'.format(key))
            # All non-CK parameters are ignored.
        return conf

    def __init__(self):
        self.compartments = {}

if __name__ == '__main__':
    with open(os.path.expanduser('~/.ssh/ckssh_config')) as f:
        conf = Config.load(f)
    print(sorted(conf.compartments.keys()))
