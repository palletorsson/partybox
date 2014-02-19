from django.conf.urls import url, patterns
from apps.publication.views import Posts, AddPost

urlpatterns = patterns('',
    url(r'^/*$', Posts, name= 'list_posts'),
    url(r'^add/$', AddPost, name= 'add_post'),
)

