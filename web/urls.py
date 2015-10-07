from django.conf.urls import patterns, include, url
from web import views

github_user_regex = r'(?P<owner>[a-zA-Z0-9-][a-zA-Z0-9-_]*)'
github_repo_regex = r'(?P<repository>[a-zA-Z0-9-][a-zA-Z0-9-_]*)'
github_user_repo_regex = r'(?P<full_repository_name>(?P<owner>[a-zA-Z0-9-][a-zA-Z0-9-_]*)/(?P<repository>[a-zA-Z0-9-][a-zA-Z0-9-_]*))'
github_issue_id = r'(?P<issue_id>[0-9]+)'

boardurlpatterns = patterns('',
    url(r'^$', views.ideas, name='ideas'),
    url(r'^questions$', views.questions, name='questions'),
    url(r'^_setupjucy$', views.prepare_repo_for_jucy, name='setupjucy'),
)

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^_loginerror$', views.loginerror, name='loginerror'),
    url(r'^_pick$', views.pick, name='pick'),
    # TODO(korfuri): Remove these urlmap entries, since their views are not needed.
    # url(r'^%s$' % (github_user_repo_regex),
    #     views.board, name='board'),
    # url(r'^%s/%s$' % (github_user_repo_regex, github_issue_id),
    #     views.issue, name='issue'),
    url(r'^' + github_user_repo_regex + '/$', include(boardurlpatterns)),
)
