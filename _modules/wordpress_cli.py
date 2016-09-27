# -*- coding: utf-8 -*-

# FIXME None of the methods below check prerequisites; for instance, whether WP-CLI is installed!
# TODO Is the 'path' argument necessary for WP-CLI if we are setting the CWD?
# TODO Add support for other WP-CLI arguments/flags

import os

from salt.exceptions import CommandExecutionError, SaltInvocationError


__virtualname__ = 'wordpress'


def __virtual__():
    """
    Only load the module if WP-CLI is installed; used by most of the methods

    The state that installs WP-CLI should have the following line added:
    - reload_modules: true
    :return:
    """
    # REFINE Fix the formatting in the above docstring
    if 'wordpress.check_cli_installed' in __salt__ and __salt__['wordpress.check_cli_installed']():
        return __virtualname__
    # REFINE Can this message be different from the 'main' module file?
    return False, 'The wordpress execution module cannot be loaded: PHP is not installed'


def _run_command(cmd, cwd, runas):
    """
    A shorthand for executing a command.
    Ideally, this will be inlined by the runtime to avoid overhead.
    :param cmd:
    :param cwd:
    :param runas:
    :return:
    """
    # TODO Determine if this will actually be optimized away at runtime
    # Doubtful, due to Python's ability to alter code definitions;
    # may be possible with a decorator of some sort
    # FIXME Inline this code, replacing with the appropriate cmd call
    # While Python code optimizations and decorators are interesting,
    # many of our methods only need the return code; no point in dumping everything!
    return __salt__['cmd.run_all'](cmd=cmd, cwd=cwd, runas=runas, python_shell=False)


def _parse_status(command_stdout):
    # Splits command results into a dict
    # Rather overbuilt given that we only care about the 'Status' line
    # Based off of https://stackoverflow.com/a/16175368

    ret = {}
    for row in command_stdout.splitlines():
        if ': ' in row:
            key, value = row.split(': ')
            ret[key.strip()] = value.strip()

    return ret


def check_wp_downloaded(site_path):
    # This is based off of the behavior in WP-CLI
    # TODO Test that ``site_path`` is defined!
    test_full_path = os.path.join(site_path, 'wp-load.php')
    return os.path.isfile(test_full_path)


def download_wordpress(site_path, user):
    # TODO Extend this to allow use of alternate sources

    if check_wp_downloaded(site_path):
        raise CommandExecutionError('Wordpress is already downloaded at {0}'.format(site_path))

    ret = {}
    command = 'wp core download --path="{0}"'.format(site_path)

    try:
        cmd_result = _run_command(cmd=command, cwd=site_path, runas=user)
    except Exception as e:
        return e

    ret['Name'] = 'WordPress Download Package'
    ret['Path'] = site_path

    ret['Result'] = cmd_result

    return ret


def check_site_configured(site_path):
    # TODO This does not check the actual configuration values
    # Compare with the behavior of the apache.config state
    # Balance duplicated effort with external dependencies in terms of WP-CLI

    # TODO This does not validate ``site_path``

    test_full_path = os.path.join(site_path, 'wp-config.php')
    return os.path.isfile(test_full_path)


# noinspection SpellCheckingInspection
def config_site(site_path, config, user):
    keys = {'dbname', 'dbuser', 'dbpass', 'dbhost'}

    if not all(k in config for k in keys):
        raise SaltInvocationError('The config must specify all of '
                                  '"dbname", "dbuser", "dbpass", and "dbhost"')

    # REFINE Can we parse ``config`` into named variables?  The repeated references bother me.
    # Alternatively, since we don't need to handle the same flexibility as ``apache.config``,
    # this could just use individual named parameters rather than a dictionary...
    # However, individual parameters may make states more cluttered; check SaltStack idiomatic method

    if check_site_configured(site_path):
        raise CommandExecutionError('Site at path \'{0}\' is already configured'.format(site_path))

    ret = {}
    # FIXME This is liable to result in the passwords being written to plaintext logs
    command = 'wp core config --dbname="{0}" --dbuser="{1}" --dbpass="{2}" --dbhost="{3}" --path="{4}"' \
        .format(config['dbname'], config['dbuser'], config['dbpass'], config['dbhost'], site_path)

    try:
        cmd_result = _run_command(command, site_path, user)
    except Exception as e:
        return e

    ret['Name'] = 'WordPress Site Configure'
    ret['Path'] = config['path']

    ret['Result'] = cmd_result

    return ret


def check_site_installed(site_path, user):
    # TODO Determine what validations to perform on our parameters

    command = 'wp core is-installed --path="{0}"'.format(site_path)

    # TODO Determine how to handle exceptions in command processing
    # That is, we currently treat this as returning a boolean value,
    # but other values may be coerced and cause undesired behavior.
    try:
        cmd_result = _run_command(command, site_path, user)
    except Exception as e:
        return e

    # WP-CLI exits with status 0 if installed, otherwise status 1
    return cmd_result['retcode'] == 0


def install_site(site_url,
                 site_title,
                 admin_user,
                 admin_password,
                 admin_email,
                 site_path,
                 user):
    # TODO Validate the input parameters

    if check_site_installed(site_path, user):
        raise CommandExecutionError('Site at path \'{0}\' is already installed'.format(site_path))

    ret = {}
    # FIXME This is liable to result in the passwords being written to plaintext logs
    command = ('wp core install --url="{0}" --title="{1}" '
               '--admin-user="{2}" --admin-password="{3}" '
               '--admin-email="{4}" --path="{5}"') \
        .format(site_url, site_title,
                admin_user, admin_password,
                admin_email, site_path)

    try:
        cmd_result = _run_command(command, site_path, user)
    except Exception as e:
        return e

    ret['Name'] = 'Wordpress Site Install'
    ret['Path'] = site_path

    ret['Result'] = cmd_result

    return ret


def check_plugin_installed(plugin_name, site_path, user):
    # TODO Validate the input parameters

    command = 'wp plugin is-installed "{0}" --path="{1}"' \
        .format(plugin_name, site_path)

    # TODO Determine how to handle exceptions in command processing
    # That is, we currently treat this as returning a boolean value,
    # but other values may be coerced and cause undesired behavior.
    try:
        cmd_result = _run_command(command, site_path, user)
    except Exception as e:
        return e

    # WP-CLI exits with status 0 if installed, otherwise status 1
    return cmd_result['retcode'] == 0


def install_plugin(plugin_name, site_path, user):
    # Note that WP-CLI appears to just perform file system manipulation,
    # so a symlink should be used instead for a development environment.
    # That said, plugins may need to be deactivated and reactivated to
    # work correctly when changed.  For now, this is up to the plugin
    # developer to handle correctly in their environment.
    # TODO Validate the input parameters

    if check_plugin_installed(plugin_name, site_path, user):
        raise CommandExecutionError('Plugin \'{0}\' is already installed for site at path \'{1}\''
                                    .format(plugin_name, site_path))

    ret = {}
    command = 'wp plugin install "{0}" --path="{1}"' \
        .format(plugin_name, site_path)

    try:
        cmd_result = _run_command(command, site_path, user)
    except Exception as e:
        return e

    ret['Name'] = 'WordPress Plugin Install'
    ret['Path'] = site_path

    ret['Result'] = cmd_result

    return ret


def check_plugin_enabled(plugin_name, site_path, user):
    # TODO Validate the input parameters

    command = 'wp plugin status "{0}" --path="{1}"' \
        .format(plugin_name, site_path)

    # TODO Determine how to handle exceptions in command processing
    # That is, we currently treat this as returning a boolean value,
    # but other values may be coerced and cause undesired behavior.
    try:
        cmd_result = _run_command(command, site_path, user)
    except Exception as e:
        return e

    parsed = _parse_status(cmd_result['stdout'])

    return 'Status' in parsed and parsed['Status'] == 'Active'


def enable_plugin(plugin_name, site_path, user):
    # TODO Validate the input parameters

    if check_plugin_enabled(plugin_name, site_path, user):
        raise CommandExecutionError('Plugin \'{0}\' is already enabled for site at path \'{1}\''
                                    .format(plugin_name, site_path))

    ret = {}
    command = 'wp plugin activate "{0}" --path="{1}"' \
        .format(plugin_name, site_path)

    try:
        cmd_result = _run_command(command, site_path, user)
    except Exception as e:
        return e

    ret['Name'] = 'WordPress Plugin Enable'
    ret['Path'] = site_path

    ret['Result'] = cmd_result

    return ret


def disable_plugin(plugin_name, site_path, user):
    # TODO Validate the input parameters

    if check_plugin_enabled(plugin_name, site_path, user):
        raise CommandExecutionError('Plugin \'{0}\' is already disabled for site at path \'{1}\''
                                    .format(plugin_name, site_path))

    ret = {}
    command = 'wp plugin deactivate "{0}" --path="{1}"' \
        .format(plugin_name, site_path)

    try:
        cmd_result = _run_command(command, site_path, user)
    except Exception as e:
        return e

    ret['Name'] = 'WordPress Plugin Disable'
    ret['Path'] = site_path

    ret['Result'] = cmd_result

    return ret


def check_theme_installed(theme_name, site_path, user):
    # TODO Validate the input parameters

    command = 'wp theme is-installed "{0}" --path="{1}"' \
        .format(theme_name, site_path)

    # TODO Determine how to handle exceptions in command processing
    # That is, we currently treat this as returning a boolean value,
    # but other values may be coerced and cause undesired behavior.
    try:
        cmd_result = _run_command(command, site_path, user)
    except Exception as e:
        return e

    # WP-CLI exits with status 0 if installed, otherwise status 1
    return cmd_result['retcode'] == 0


def install_theme(theme_name, site_path, user):
    # Note that WP-CLI appears to just perform file system manipulation,
    # so a symlink should be used instead for a development environment.
    # That said, themes may need to be deactivated and reactivated to
    # work correctly when changed.  For now, this is up to the theme
    # developer to handle correctly in their environment.
    # TODO Validate the input parameters

    if check_theme_installed(theme_name, site_path, user):
        raise CommandExecutionError('Theme \'{0}\' is already installed for site at path \'{1}\''
                                    .format(theme_name, site_path))

    ret = {}
    command = 'wp theme install "{0}" --path="{1}"' \
        .format(theme_name, site_path)

    try:
        cmd_result = _run_command(command, site_path, user)
    except Exception as e:
        return e

    ret['Name'] = 'WordPress Theme Install'
    ret['Path'] = site_path

    ret['Result'] = cmd_result

    return ret


def check_theme_enabled(theme_name, site_path, user):
    # TODO Validate the input parameters

    command = 'wp theme status "{0}" --path="{1}"' \
        .format(theme_name, site_path)

    # TODO Determine how to handle exceptions in command processing
    # That is, we currently treat this as returning a boolean value,
    # but other values may be coerced and cause undesired behavior.
    try:
        cmd_result = _run_command(command, site_path, user)
    except Exception as e:
        return e

    parsed = _parse_status(cmd_result['stdout'])

    return 'Status' in parsed and parsed['Status'] == 'Active'


def enable_theme(theme_name, site_path, user):
    # TODO Validate the input parameters

    if check_theme_enabled(theme_name, site_path, user):
        raise CommandExecutionError('Theme \'{0}\' is already enabled for site at path \'{1}\''
                                    .format(theme_name, site_path))

    ret = {}
    command = 'wp theme activate "{0}" --path="{1}"' \
        .format(theme_name, site_path)

    try:
        cmd_result = _run_command(command, site_path, user)
    except Exception as e:
        return e

    ret['Name'] = 'WordPress Theme Enable'
    ret['Path'] = site_path

    ret['Result'] = cmd_result

    return ret
