from django.conf.urls import url, patterns
from apps.publication.views import Posts, AddPost, AddTrackToPlayList, GetLists, GetPlaylist,  RemoveTrackFromPlaylist, VoteTrackUp, VoteTrackDown

urlpatterns = patterns('',
    url(r'^/*$', Posts, name= 'list_posts'),
    url(r'^add/$', AddPost, name= 'add_post'),
    url(r'^list/(?P<track_id>[-_\w]+)/$', AddTrackToPlayList, name= 'addtrack'),
    url(r'^getlists/$', GetLists, name= 'getlists'),
    url(r'^getplaylist/$', GetPlaylist, name= 'getplaylist'),
    url(r'^removetrackfromplaylist/(?P<track_id>[-_\w]+)/$', RemoveTrackFromPlaylist, name= 'getplaylist'),
    url(r'^votetrackup/(?P<track_id>[-_\w]+)/$', VoteTrackUp, name= 'getplaylist'),
    url(r'^votetrackdown/(?P<track_id>[-_\w]+)/$', VoteTrackDown, name= 'getplaylist'),
)



