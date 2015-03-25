from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    url(r'', include('web.urls')),
    url(r'^_oauth/', include('social.apps.django_app.urls', namespace='social')),
    url(r'^_admin/', include(admin.site.urls)),
)
