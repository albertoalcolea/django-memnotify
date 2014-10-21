from django.conf.urls import patterns, include, url

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'webtest.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('main.urls', namespace='main')),
)

# Static content
urlpatterns += staticfiles_urlpatterns()
