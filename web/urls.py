from django.conf.urls import patterns, include, url
from web import views

github_user_regex = r'[a-zA-Z0-9-][a-zA-Z0-9-_]*'
github_repo_regex = r'[a-zA-Z0-9-][a-zA-Z0-9-_]*'
github_issue_id = r'[0-9]+'

urlpatterns = patterns(
    '',
    url(r'^$', views.index, name='index'),
    url(r'^_loginerror$', views.loginerror, name='loginerror'),
    url(r'^_pick$', views.pick, name='pick'),
    url(r'^%s/%s$' % (github_repo_regex, github_user_regex),
        views.board, name='board'),
    url(r'^%s/%s/%s$' % (github_repo_regex, github_user_regex, github_issue_id),
        views.issue, name='issue'),
)
