from django.conf.urls import patterns, include, url
from api import views
from web.urls import github_user_repo_regex

boardurlpatterns = patterns('',
    url(r'^ideas/random/$', views.vote_random_ideas, name='vote_random_ideas'),
    url(r'^ideas/comments/(?P<issue_number>\d+)/$', views.ideas_comments, name='ideas_comments'),
    url(r'^ideas/create/$', views.post_idea, name='post_idea'),
    url(r'^contact/$', views.contact, name='contact'),
    url(r'^ideas/(?P<vote>vote)/(?P<issue_number>\d+)/$', views.ideas_vote, name='ideas_vote'),
    url(r'^ideas/(?P<vote>unvote)/(?P<issue_number>\d+)/$', views.ideas_vote, name='ideas_unvote'),
)

urlpatterns = patterns('',
    url(r'^' + github_user_repo_regex + '/', include(boardurlpatterns)),
    url(r'^authenticate/', views.authenticate, name='api_authenticate'),
)
