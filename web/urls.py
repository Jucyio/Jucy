from django.conf.urls import patterns, include, url
from web import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^_loginerror$', views.loginerror, name='loginerror'),
    url(r'^_pick$', views.pick, name='pick'),
)
