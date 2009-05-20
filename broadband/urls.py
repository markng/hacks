from django.conf.urls.defaults import *

urlpatterns = patterns('',
  (r'^$', 'broadband.views.map', {}, "broadband-map"),
)