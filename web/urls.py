from django.conf.urls import patterns, include, url
from web import views, webhooks

github_user_regex = r'(?P<user>[a-zA-Z0-9-][a-zA-Z0-9-_]*)'
github_repo_regex = r'(?P<repo_name>[a-zA-Z0-9-][a-zA-Z0-9-_]*)'
github_user_repo_regex = r'(?P<full_repo_name>[a-zA-Z0-9-][a-zA-Z0-9-_]*/[a-zA-Z0-9-][a-zA-Z0-9-_]*)'
github_issue_id = r'(?P<issue_id>[0-9]+)'

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^_loginerror$', views.loginerror, name='loginerror'),
    url(r'^_pick$', views.pick, name='pick'),
    url(r'^%s$' % (github_user_repo_regex),
        views.board, name='board'),
    url(r'^%s/%s$' % (github_user_repo_regex, github_issue_id),
        views.issue, name='issue'),
    url(r'^%s/_setupjucy$' % (github_user_repo_regex),
        views.prepare_repo_for_jucy, name='setupjucy'),
    url(r'^%s/_webhooks/all_issues' % (github_user_repo_regex),
        webhooks.all_issues, name='all_issues'),
)
