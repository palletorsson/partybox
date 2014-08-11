from django.db import models
from django.core.validators import MaxLengthValidator

class TextPost(models.Model):
    body =    models.CharField(max_length=256)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' %self.body

class ImagePost(models.Model):
    body =    models.CharField(max_length=256)
    imgfile = models.FileField("upload jpg, png", upload_to='documents/%Y/%m/%d' , blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' %self.body

class Track(models.Model):
    title =   models.CharField(max_length=128)
    album =   models.CharField(max_length=128)
    author =   models.CharField(max_length=128)
    music_genre = models.CharField(max_length=128)
    duration = models.TextField()
    docfile = models.FileField("upload ogg and mp3", upload_to='audio/%Y/%m/%d')
    meta_data = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' %self.title

class PlayList(models.Model): 
    title =       models.CharField(max_length=128)
    description = models.CharField(max_length=256, blank=True, null=True)
    tracks =      models.ManyToManyField('Track', through='TrackListed')
    created =     models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' %self.title

class TrackListed(models.Model):
    playlist = models.ForeignKey('Playlist')
    track =    models.ForeignKey('Track')
    position = models.IntegerField()
    added =    models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%s' %self.track

    class Meta:
        ordering = ['position']
        unique_together = (("playlist", "track"),)

class sessionUser(models.Model): 
    number_of_votes =	models.IntegerField(max_length=1, default=0)
    session_id = 		models.CharField(max_length=256)
    last_time_update =    		models.DateTimeField(auto_now=True)
    last_time_votes =    		models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' %self.session_id

class Vote(models.Model): 
    number_of_votes =	models.IntegerField(max_length=1, default=1)
    session_id = 		models.CharField(max_length=256)
    last_time =    		models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' %self.last_time


