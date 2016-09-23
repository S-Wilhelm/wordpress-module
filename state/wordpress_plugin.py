# -*- coding: utf-8 -*-


def __virtual__():
    """
    Only load the module if WP-CLI is installed
    :return:
    """
    if 'wordpress.check_cli_installed' in __salt__ and __salt__['wordpress.check_cli_installed']():
        return 'wordpress_plugin'
    return False, 'The wordpress_plugin state module cannot be loaded: WP-CLI is not installed'


def _prep_return_array(name):
    # This technique is not used in the SaltStack built-in modules, presumably due to performance
    # However, for early dev, this allows us to reduce repetition
    return {
        'name': name,
        'changes': {},
        'result': False,
        'comment': '',
        'pchanges': {},
    }


def plugin_installed(name,
                     site_path,
                     user='www-data'):
    ret = _prep_return_array(name)

    # Basic error checking, "raise salt.exceptions.SaltInvocationError" if invalid inputs

    # Get the current state, then check for changes
    current_state = __salt__['wordpress.check_plugin_installed'](plugin_name=name,
                                                                 site_path=site_path,
                                                                 user=user)

    if current_state:
        ret['result'] = True
        ret['comment'] = 'System already in the correct state'
        return ret

    # The state needs to change; check for test mode
    if __opts__['test']:
        ret['comment'] = 'The state of "{0}" will be changed.'.format(name)
        ret['pchanges'] = {
            'old': current_state,
            'new': 'Description, diff, whatever of the new state',
        }

        # Return ``None`` when running with ``test=True``
        ret['result'] = None

        return ret

    # Finally, make the actual change and return the result
    new_state = __salt__['wordpress.install_plugin'](plugin_name=name,
                                                     site_path=site_path,
                                                     user=user)

    ret['comment'] = 'The state of "{0}" was changed!'.format(name)

    ret['changes'] = {
        'old': current_state,
        'new': new_state,
    }

    ret['result'] = True

    return ret


def plugin_enabled(name,
                   site_path,
                   user='www-data'):
    ret = _prep_return_array(name)

    # Basic error checking, "raise salt.exceptions.SaltInvocationError" if invalid inputs

    # Get the current state, then check for changes
    current_state = __salt__['wordpress.check_plugin_enabled'](plugin_name=name,
                                                               site_path=site_path,
                                                               user=user)

    if current_state:
        ret['result'] = True
        ret['comment'] = 'System already in the correct state'
        return ret

    # The state needs to change; check for test mode
    if __opts__['test']:
        ret['comment'] = 'The state of "{0}" will be changed.'.format(name)
        ret['pchanges'] = {
            'old': current_state,
            'new': 'Description, diff, whatever of the new state',
        }

        # Return ``None`` when running with ``test=True``
        ret['result'] = None

        return ret

    # Finally, make the actual change and return the result
    new_state = __salt__['wordpress.enable_plugin'](plugin_name=name,
                                                    site_path=site_path,
                                                    user=user)

    ret['comment'] = 'The state of "{0}" was changed!'.format(name)

    ret['changes'] = {
        'old': current_state,
        'new': new_state,
    }

    ret['result'] = True

    return ret


def plugin_disabled(name,
                    site_path,
                    user='www-data'):
    ret = _prep_return_array(name)

    # Basic error checking, "raise salt.exceptions.SaltInvocationError" if invalid inputs

    # Get the current state, then check for changes
    current_state = __salt__['wordpress.check_plugin_enabled'](plugin_name=name,
                                                               site_path=site_path,
                                                               user=user)

    if not current_state:
        ret['result'] = True
        ret['comment'] = 'System already in the correct state'
        return ret

    # The state needs to change; check for test mode
    if __opts__['test']:
        ret['comment'] = 'The state of "{0}" will be changed.'.format(name)
        ret['pchanges'] = {
            'old': current_state,
            'new': 'Description, diff, whatever of the new state',
        }

        # Return ``None`` when running with ``test=True``
        ret['result'] = None

        return ret

    # Finally, make the actual change and return the result
    new_state = __salt__['wordpress.disable_plugin'](plugin_name=name,
                                                     site_path=site_path,
                                                     user=user)

    ret['comment'] = 'The state of "{0}" was changed!'.format(name)

    ret['changes'] = {
        'old': current_state,
        'new': new_state,
    }

    ret['result'] = True

    return ret
