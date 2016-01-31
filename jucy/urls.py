from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = patterns('',
    url(r'', include('web.urls')),
    url(r'^_oauth/', include('social.apps.django_app.urls', namespace='social')),
    url(r'^_admin/', include(admin.site.urls)),
    url(r'^_api/', include('api.urls')),
    url(r'^_ajax/', include('api.urls')),
) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += url(r'^_widget/', include('widget.urls')),
