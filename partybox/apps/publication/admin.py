from django.contrib import admin
from models import  TextPost,ImagePost, Track, PlayList, TrackListed, Vote, sessionUser

class TextPostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'body', 'created', )

admin.site.register(TextPost, TextPostAdmin)

class ImagePostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'body', 'created', 'imgfile',)

admin.site.register(ImagePost, ImagePostAdmin)

class TrackAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'album', 'author', 'meta_data', 'created', 'music_genre', 'docfile',)

admin.site.register(Track, TrackAdmin)

class PlayListAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description', 'created',)

admin.site.register(PlayList, PlayListAdmin)

class TrackListedAdmin(admin.ModelAdmin):
    list_display = ('pk', 'playlist', 'track', 'position', 'added',)

admin.site.register(TrackListed, TrackListedAdmin)

class VoteAdmin(admin.ModelAdmin):
    list_display = ('pk', 'number_of_votes', 'session_id', 'last_time',)

admin.site.register(Vote, VoteAdmin)

class sessionUserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'number_of_votes', 'session_id', 'last_time_update', 'last_time_votes',)

admin.site.register(sessionUser, sessionUserAdmin)
