"""
This file was generated with the customdashboard management command, it
contains the two classes for the main dashboard and app index dashboard.
You can customize these classes as you want.

To activate your index dashboard add the following to your settings.py::
    ADMIN_TOOLS_INDEX_DASHBOARD = 'devcoop.dashboard.CustomIndexDashboard'

And to activate the app index dashboard::
    ADMIN_TOOLS_APP_INDEX_DASHBOARD = 'devcoop.dashboard.CustomAppIndexDashboard'
"""

from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from admin_tools.dashboard import modules, Dashboard, AppIndexDashboard
from admin_tools.utils import get_admin_site_name
from django.conf import settings

class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for devcoop.
    """
    columns = 2
    title = ''
    template = 'admin_tools/coop_dashboard.html'

    def init_with_context(self, context):
        site_name = get_admin_site_name(context)

        # append a link list module for "quick links"
        # self.children.append(modules.LinkList(
        #     _('Quick links'),
        #     layout='inline',
        #     draggable=False,
        #     deletable=False,
        #     collapsible=False,
        #     children=[
        #         #[_('Return to site'), '/'],
        #         [_('Change password'),
        #          reverse('%s:password_change' % site_name)],
        #         [_('Log out'), reverse('%s:logout' % site_name)],
        #     ]
        # ))

        # self.children.append(modules.AppList(
        #     _(u"Articles"),
        #     models=('coop_local.models.Article',
        #             'coop_cms.models.ArticleCategory',
        #             'coop_cms.apps.rss_sync.models.RssItem',
        #             #'django.contrib.comments.Comment',
        #             'forms_builder.forms.models.Form',
        #             ),
        #     template='admin_tools/coop_applist.html'
        # ))

        # if 'coop.agenda' in settings.INSTALLED_APPS:
        #     self.children.append(modules.AppList(
        #         _(u"Agenda"),
        #         models=('coop_local.models.Event',
        #                 'coop_local.models.EventCategory',
        #                 ),
        #         template='admin_tools/coop_applist.html',
        #     ))


        # self.children.append(modules.AppList(
        #     _(u"My network"),
        #     models=('coop_local.models.Person',
        #             'coop_local.models.PersonCategory',
        #             'coop_local.models.Organization',
        #             'coop_local.models.OrganizationCategory',
        #             ),
        #     template='admin_tools/coop_applist.html',
        # ))


        # # append an app list module for "Administration"
        # self.children.append(modules.AppList(
        #     _('Administration'),
        #     models=('django.contrib.*',),
        #     template='admin_tools/coop_applist.html',
        # ))

        # append a recent actions module
        self.children.append(modules.RecentActions(_('Recent Actions'), 10))

        # append a feed module
        self.children.append(modules.Feed(
            _('Latest Django News'),
            feed_url='http://www.djangoproject.com/rss/weblog/',
            limit=5
        ))

        # append another link list module for "support".
        self.children.append(modules.LinkList(
            _('Support'),
            children=[
                {
                    'title': _('Blog PES'),
                    'url': 'http://blog.credis.org/',
                    'external': True,
                },
                {
                    'title': _('Django "django-users" mailing list'),
                    'url': 'http://groups.google.com/group/django-users',
                    'external': True,
                },

            ]
        ))


class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for devcoop.
    """

    # we disable title because its redundant with the model list module
    title = ''

    def __init__(self, *args, **kwargs):
        AppIndexDashboard.__init__(self, *args, **kwargs)

        # append a model list module and a recent actions module
        self.children += [
            modules.ModelList(self.app_title, self.models),
            modules.RecentActions(
                _('Recent Actions'),
                include_list=self.get_app_content_types(),
                limit=5
            )
        ]

    def init_with_context(self, context):
        """
        Use this method if you need to access the request context.
        """
        return super(CustomAppIndexDashboard, self).init_with_context(context)
