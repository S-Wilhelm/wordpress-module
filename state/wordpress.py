# -*- coding: utf-8 -*-

import salt.exceptions

import salt.utils


def __virtual__():
    """
    Only load the module if PHP is installed; needed for WP-CLI
    :return:
    """
    if salt.utils.which('php'):
        return 'wordpress'
    return False, 'The wordpress state module cannot be loaded: PHP is not installed'


def cli_installed(name,
                  source='https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar',
                  checksum='https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar.sha512',
                  user='www-data',
                  group='www-data'):
    """
    Enforce installation of WP-CLI

    This state module checks that the WP-CLI tool is installed, which is needed for the other
    wordpress_* states.  It does not currently ensure the ownership of the file, nor the version.

    :param name:
    :param source: The source location for the WP-CLI PHAR file
    :param checksum: The checksum for the PHAR file
    :param user: The user that should own the PHAR file
    :param group: The group that should own the PHAR file
    :return:
    """
    ret = {
        'name': name,
        'changes': {},
        'result': False,
        'comment': '',
        'pchanges': {},
    }

    # TODO Adjust this function to also validate file ownership and version
    # FIXME This function should probably just wrap ``file.managed``

    # Start with basic error-checking.  Do all the passed parameters make sense and agree with each-other?
    # In this state, we do not yet have any params to check.
    # If we did, however, we would ``raise salt.exceptions.SaltInvocationError('Descriptive text here')
    # REFINE Check the distinction between returning a result of ``False`` and raising SaltInvocationError
    # REFINE Further, the ``file.managed`` state internally validates the user and group
    if not __salt__['user.info'](user):
        ret['comment'] = 'User is not present: {0}'.format(user)
        ret['result'] = False
        return ret

    if not __salt__['group.info'](group):
        ret['comment'] = 'Group is not present: {0}'.format(group)
        ret['result'] = False
        return ret

    # Check the current state of the system.  Does anything need to change?
    current_state = __salt__['wordpress.check_cli_installed']()

    if current_state:
        ret['result'] = True
        ret['comment'] = 'WP-CLI is already installed'
        return ret

    # The state of the system does need to be changed. Check if we're running
    # in ``test=true`` mode.
    if __opts__['test']:
        ret['comment'] = 'WP-CLI will be installed.'
        ret['pchanges'] = {
            'old': current_state,
            'new': 'Description, diff, whatever of the new state',
        }

        # Return ``None`` when running with ``test=true``.
        ret['result'] = None

        return ret

    # Finally, make the actual change and return the result.
    new_state = __salt__['wordpress.install_wp_cli'](source, checksum, user, group)

    ret['comment'] = 'WP-CLI was installed.'

    ret['changes'] = {
        'old': current_state,
        'new': new_state,
    }

    ret['result'] = True

    return ret
