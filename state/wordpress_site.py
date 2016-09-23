# -*- coding: utf-8 -*-


def __virtual__():
    """
    Only load the module if WP-CLI is installed
    :return:
    """
    if 'wordpress.check_cli_installed' in __salt__ and __salt__['wordpress.check_cli_installed']():
        return 'wordpress_site'
    return False, 'The wordpress_site state module cannot be loaded: WP-CLI is not installed'


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


def site_downloaded(name,
                    user='www-data'):
    ret = _prep_return_array(name)

    # Basic error checking, "raise salt.exceptions.SaltInvocationError" if invalid inputs

    # Get the current state, then check for changes
    current_state = __salt__['wordpress.check_wp_downloaded'](site_path=name)

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
    new_state = __salt__['wordpress.download_wordpress'](site_path=name, user=user)

    ret['comment'] = 'The state of "{0}" was changed!'.format(name)

    ret['changes'] = {
        'old': current_state,
        'new': new_state,
    }

    ret['result'] = True

    return ret


def site_configured(name,
                    config,
                    user='www-data'):
    ret = _prep_return_array(name)

    # Basic error checking, "raise salt.exceptions.SaltInvocationError" if invalid inputs

    # Get the current state, then check for changes
    current_state = __salt__['wordpress.check_site_configured'](site_path=name)

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
    new_state = __salt__['wordpress.config_site'](site_path=name, config=config, user=user)

    ret['comment'] = 'The state of "{0}" was changed!'.format(name)

    ret['changes'] = {
        'old': current_state,
        'new': new_state,
    }

    ret['result'] = True

    return ret


# FIXME This is inconsistent; site_configured takes a dict of options, this takes named parameters
def site_installed(name,
                   site_url,
                   site_title,
                   admin_user,
                   admin_password,
                   admin_email,
                   user='www-data'):
    ret = _prep_return_array(name)

    # Basic error checking, "raise salt.exceptions.SaltInvocationError" if invalid inputs

    # Get the current state, then check for changes
    current_state = __salt__['wordpress.check_site_installed'](site_path=name, user=user)

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
    new_state = __salt__['wordpress.install_site'](site_url=site_url,
                                                   site_title=site_title,
                                                   admin_user=admin_user,
                                                   admin_password=admin_password,
                                                   admin_email=admin_email,
                                                   site_path=name,
                                                   user=user)

    ret['comment'] = 'The state of "{0}" was changed!'.format(name)

    ret['changes'] = {
        'old': current_state,
        'new': new_state,
    }

    ret['result'] = True

    return ret
