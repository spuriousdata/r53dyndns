from django.conf.urls import patterns, url
from r53dyndns.views import ListView, UpdateView

urlpatterns = patterns('',
        url(r'^list/$', ListView.as_view(), name='list'),
        url(r'^update/(?P<fqdn>[\w\.]+)/$', UpdateView.as_view(), name='update'),
)
