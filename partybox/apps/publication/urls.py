from django.conf.urls import *

from django.views.generic.base import RedirectView
from apps.publication.views import Posts, AddPost, AddTrackToPlayList, GetLists, GetPlaylist, RemoveTrackFromPlaylist, Home, VoteTrackUp, VoteTrackDown, JsonMessages, JsonImages, JsonTracks, fallback, JsonPosts, JsonFiles, songPlayingNow, removeLastTrackFromPlaylist, playerSongFm, CaptureAll, StartFm
from django.contrib import admin




urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^posts/$', JsonPosts, name= 'jsonposts'),
    url(r'^songnowplaying/$', songPlayingNow, name= 'songplayingnow'),
    url(r'^add/$', AddPost, name= 'add_post'),
    url(r'^messages/$', JsonMessages, name= 'jsonmessages'),
    url(r'^images/$', JsonImages, name= 'jsonimages'),
    url(r'^tracks/$', JsonTracks, name= 'jsontracks'),
    url(r'^files/$', JsonFiles, name= 'jsonfiles'),
    url(r'^list/(?P<track_id>[-_\w]+)/$', AddTrackToPlayList, name= 'addtrack'),
    url(r'^getlists/$', GetLists, name= 'getlists'),
    url(r'^getplaylist/$', GetPlaylist, name= 'getplaylist'),
    url(r'^removetrack/$', removeLastTrackFromPlaylist, name='removeLastTrackFromPlaylist'),
    url(r'^removetrackfromplaylist/(?P<track_id>[-_\w]+)/$', RemoveTrackFromPlaylist, name= 'getplaylist'),
    url(r'^votetrackup/(?P<track_id>[-_\w]+)/$', VoteTrackUp, name= 'votetrackup'),
    url(r'^votetrackdown/(?P<track_id>[-_\w]+)/$', VoteTrackDown, name= 'votetrackdown'),
    url(r'^startfm/$', StartFm, name='startfm'),
    url(r'^home/$', Home, name= 'home'),
    url(r'^.*/$', CaptureAll, name= 'captureall'),
    url(r'^.*$', CaptureAll, name= 'captureall'),

)




