from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from widget import views

urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='widget_test.html'), name='widget_test'),
)
