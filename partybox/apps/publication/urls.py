from django.conf.urls import url, patterns
from apps.publication.views import Posts, AddPost, AddTrackToPlayList, GetLists, GetPlaylist, RemoveTrackFromPlaylist, Home, VoteTrackUp, VoteTrackDown, JsonMessages, JsonTracks

urlpatterns = patterns('',
    url(r'^/*$', Posts, name= 'list_posts'),
    url(r'^home/$', Home, name= 'home'),
    url(r'^add/$', AddPost, name= 'add_post'),
    url(r'^messages/$', JsonMessages, name= 'jsonmessages'),
    url(r'^tracks/$', JsonTracks, name= 'jsontracks'),
    url(r'^list/(?P<track_id>[-_\w]+)/$', AddTrackToPlayList, name= 'addtrack'),
    url(r'^getlists/$', GetLists, name= 'getlists'),
    url(r'^getplaylist/$', GetPlaylist, name= 'getplaylist'),
    url(r'^removetrackfromplaylist/(?P<track_id>[-_\w]+)/$', RemoveTrackFromPlaylist, name= 'getplaylist'),
    url(r'^votetrackup/(?P<track_id>[-_\w]+)/$', VoteTrackUp, name= 'votetrackup'),
    url(r'^votetrackdown/(?P<track_id>[-_\w]+)/$', VoteTrackDown, name= 'votetrackdown'),
)



