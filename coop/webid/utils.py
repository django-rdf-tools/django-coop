import logging

from django.contrib.auth.models import UserManager
from django.db import models

logger = logging.getLogger(name=__name__)


def create_blank_profile(user=None):
    from django_webid.provider.models import WebIDUser
    from django.conf import settings
    if not user:
        logger.warning('create_blank_profile: no user.')
        return
    profile_model = settings.AUTH_PROFILE_MODULE
    app_split = profile_model.split('.')
    if len(app_split) == 2:
        app_label, mod_label = app_split
    else:
        app_label, mod_label = app_split[-2:]
    pklss = models.get_model(app_label, mod_label)

    webiduser = WebIDUser.objects.get(id=user.id)
    try:
        pklss.objects.create(
            user=webiduser,
            first_name=" ",
            last_name=" ")
    except:
        raise


def custom_webid_uri(webiduser):
    return 'testing/webid/%s' % webiduser.username


# This function below copied and slightly modified from
# the builtin user creation method on WebIDAuth backend.

# If you want to access other fields not retrieved, you
# can alwas get the info from the raw profile stored in webidinfo.

def build_coop_user(request):
    """
    create a valid (and stored) django user to be associated with
    the authenticated WebID URI. This method will be used if no alternative
    is provided in the settings.WEBIDAUTH_CREATE_USER_CALLBACK value, or if
    the value there is not a valid function.
    """
    import re
    logger.debug('building user!')
    data = request.webidinfo
    validatedURI = data.validatedURI
    logger.debug('validatedURI = %s' % validatedURI)
    if not validatedURI:
        #XXX this check should be moved to "create_user" function
        logger.error('attempt to build an user with no validatedURI! \
skipping...')
        return None

    names = data.webid_name

    ###################################
    # XXX THIS IS THE COOP SPECIFIC BIT
    # XXX should take care of missing info.

    givenName = names.get('givenName', None)
    familyName = names.get('familyName', None)
    target_name = "%s.%s" % (givenName, familyName)

    ###################################

    def augment_name(name):
        ends_number = re.findall('\S+_(\d+)', name)
        if ends_number:
            number = int(ends_number[0]) + 1
            logger.debug('number %s' % number)
            _name = name.replace('_%s' % ends_number[0], '_%s' %
                    str(number))
            return _name
        else:
            return u"%s_1" % (name)

    #[warning] This is "a bit" hackish:
    max_tries = 20
    tries = max_tries

    while tries > 0:
        print 'looping'
        print 'target_name', target_name
        print 'try', max_tries - tries
        #XXX build kwargs dict, instead of hardcoding name
        colliding_users = models.WebIDUser.objects.all().\
                filter(username=target_name)
        #print 'colliding ', colliding_users
        #print colliding_users.count()
        #print 'all ', WebIDUser.objects.all()

        if colliding_users.count() > 0:
            target_name = augment_name(target_name)
            tries -= 1
        else:
            break
    else:
        logger.warning('Sorry... *that* name is already taken...')
        #XXX here we should signal some way of getting
        #user input (a form, or something)

    # XXX this assumption is VERY VERY weak
    # i.e, make sure to find a proper username if we do not
    # have the family name / given name
    # Also, handle collisions
    # (better to have, for instance, user@site usernames in the db
    # and have a display-name?)
    user = models.WebIDUser.objects.create(username=target_name)
    useruri = models.WebIDURI.objects.create(uri=validatedURI, user=user)
    useruri.save()
    logger.info('username set to %s' % names['name'])
    user.password = UserManager().make_random_password()
    user.is_active = True
    logger.debug('saving WebIDUser with name %s' % target_name)
    user.save()
    return user
