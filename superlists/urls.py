from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
      #url(r'^admin/', include(admin.site.urls)),

      url(r'^$', 'lists.views.home_page', name='home'),
      url(r'^lists/', include('lists.urls'))
)
