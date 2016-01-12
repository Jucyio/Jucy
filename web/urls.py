from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from web import views, webhooks

github_user_regex = r'(?P<owner>[a-zA-Z0-9-][a-zA-Z0-9-_]*)'
github_repo_regex = r'(?P<repository>[a-zA-Z0-9-][a-zA-Z0-9-_\.]*)'
github_user_repo_regex = r'(?P<full_repository_name>(?P<owner>[a-zA-Z0-9-][a-zA-Z0-9-_]*)/(?P<repository>[a-zA-Z0-9-\.][a-zA-Z0-9-_\.]*))'
github_issue_id = r'(?P<issue_id>[0-9]+)'

boardurlpatterns = patterns('',
    url(r'^$', views.ideas, name='ideas'),
    url(r'^ideas[/]+$', views.ideas, name='ideas'),
    url(r'^questions[/]+$', views.questions, name='questions'),
    url(r'^setup$', views.prepare_repo_for_jucy, name='setupjucy'),
)

urlpatterns = patterns('',
    url(r'^$', views.genericViewWithContext, name='index'),
    url(r'^_loginerror[/]+$', views.genericViewWithContext, name='loginerror'),
    url(r'^_pick[/]+$', views.pick, name='pick'),
    url(r'^_mailing[/]+$', views.genericViewWithContext, name='mailing'),
    url(r'^_about[/]+$', views.genericViewWithContext, name='about'),
    url(r'^_terms[/]+$', views.genericViewWithContext, name='terms'),
    url(r'^_privacy[/]+$', views.genericViewWithContext, name='privacy'),
    url(r'^_logout[/]+$', 'django.contrib.auth.views.logout', {'next_page': '/'}),


    url(r'^_ajax/authenticate[/]+$', views.ajax_authenticate, name='ajax_authenticate'),

    url(r'^' + github_user_repo_regex + '/', include(boardurlpatterns)),

    # url(r'^%s$' % (github_user_repo_regex),
    #     views.board, name='board'),

    # url(r'^%s/%s$' % (github_user_repo_regex, github_issue_id),
    #     views.issue, name='issue'),

    # url(r'^%s/_ajax/createidea$' % (github_user_repo_regex),
    #     views.create_idea, name='createidea'),
    # url(r'^%s/_webhooks/all_issues' % (github_user_repo_regex),
    #     webhooks.all_issues, name='all_issues'),

    url(r'^%s/_ajax/issue/%s/comments$' % (github_user_repo_regex, github_issue_id),
        views.get_issue_comments, name='get_issue_comments'),
)
