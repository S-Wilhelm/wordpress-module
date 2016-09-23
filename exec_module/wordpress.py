# -*- coding: utf-8 -*-

# TODO Determine how to handle sites in the root of the web directory (main concern is permissions)

import salt.utils


__virtualname__ = 'wordpress'


def __virtual__():
    """
    Only load the module if PHP is installed; needed for WP-CLI
    :return:
    """
    # For system-wide packages, Salt will automatically reload the modules
    if salt.utils.which('php'):
        return __virtualname__
    return False, 'The wordpress execution module cannot be loaded: PHP is not installed'


def check_cli_installed():
    return salt.utils.which('wp')


def install_wp_cli(source, checksum, user, group):
    # REFINE Do we need any additional logic here?
    # The formula used file.managed to download the PHAR file with appropriate permissions
    ret = __states__['file.managed'](name='/usr/local/bin/wp', source=source, source_hash=checksum, user=user,
                                     group=group, mode=740)
    return ret



