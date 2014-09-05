from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from forms import ImageForm, TrackForm, TextForm, DocForm
from models import TextPost, ImagePost, Track, DocPost, PlayList, TrackListed, Vote, sessionUser, LatestSongRequest, SongPlaying
from itertools import chain
from django.http import HttpResponse, Http404
from django.core import serializers
import json
from django.http import HttpResponseNotAllowed
from datetime import datetime, timedelta
from django.contrib.sessions.backends.db import SessionStore

import os

# models for metadata extraction
from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
from hachoir_core.tools import makePrintable
from hachoir_metadata import extractMetadata
from hachoir_core.i18n import getTerminalCharset
from sys import argv, stderr, exit
from hachoir_core.error import HachoirError
from hachoir_core.stream import InputIOStream
from hachoir_parser import guessParser
from hachoir_metadata import extractMetadata
import time

def AddPost(request):
    if request.POST:
        fileExtension = None
        if request.FILES: 
            try:
                fileName, fileExtension = os.path.splitext(request.FILES["file"].name)
            except: 
                pass
	
        millis = int(round(time.time() * 1000))

       
        if fileExtension == '.jpg' or fileExtension == '.png' or fileExtension == '.gif' or fileExtension == '.jpeg' :
        	save_img_post(request)
        elif fileExtension == '.mp3':
        	save_audio_post(request)
        elif fileExtension == '.pdf' or fileExtension == '.txt'  or fileExtension == '.rtf':
        	save_doc_post(request)
        elif len(request.POST["body"]) > 1:
            save_message_post(request)
            print "message"
        else:
            print "postnon"
 
    return HttpResponse('200')

def Home(request):
    return render_to_response('publication/home.html',  context_instance=RequestContext(request))


def fallback(request):
    return HttpResponseRedirect('/')

def handler404(request):
    return HttpResponseRedirect('/')

def JsonMessages(request):
    messages = TextPost.objects.all().order_by('-created')
    json_list = serializers.serialize('json', messages)
    response = HttpResponse(json_list, mimetype='application/json')
    return response

def JsonImages(request):
    images = ImagePost.objects.all().order_by('-created')
    json_list = serializers.serialize('json', images)
    response = HttpResponse(json_list, mimetype='application/json')
    return response

def JsonTracks(request): 
    tracks = Track.objects.all().order_by('-created')
    for t in tracks: 
        if len(t.title) > 20:
            t.title = t.title[:20] + ".."
        if len(t.author) > 20:
            t.author = t.author[:20] 
        if len(t.author) + len(t.author) > 39:
             t.author = t.author[:14] 

    json_list = serializers.serialize('json', tracks)
    response = HttpResponse(json_list, mimetype='application/json')
    return response


def JsonPosts(request):
    texts = TextPost.objects.all().order_by('-created')[:30]  
    tracks = Track.objects.all().order_by('-created')[:10]

    for t in tracks: 
        if len(t.title) > 20:
            t.title = t.title[:20] + ".."
        if len(t.author) > 20:
            t.author = t.author[:20] 
        if len(t.author) + len(t.author) > 39:
             t.author = t.author[:14] 
    files = DocPost.objects.all().order_by('-created')[:10]

    images = ImagePost.objects.all().order_by('-created')[:10]

    listing = MakeStreamList(texts, images, tracks, files)


    for k in listing:
        k.type = k.__class__.__name__

    json_list = serializers.serialize('json', listing)

    response = HttpResponse(json_list, mimetype='application/json')
    return response

def JsonFiles(request):
    files = DocPost.objects.all().order_by('-created')
    for f in files:
        print f.docfile
    json_list = serializers.serialize('json', files)
    response = HttpResponse(json_list, mimetype='application/json')
    return response

def Posts(request):
    texts = TextPost.objects.all().order_by('-created')
    images = ImagePost.objects.all().order_by('-created')
    tracks = Track.objects.all().order_by('-created')
    try:
        sessionid = request.COOKIES['sessionid']
    except: 
        sessionid = request.META['XDG_SESSION_COOKIE'][:32]

    p, created = sessionUser.objects.get_or_create(session_id=sessionid)
    print session_id
    p.save()
       
    try:
        radio_list = PlayList.objects.get(pk=1).tracklisted_set.all()
    except: 
		radio_list = None

    imgform = ImageForm()
    listing = MakeStreamList(texts, images, tracks, files)

    json_list = serializers.serialize('json', listing)

    for t in tracks: 
        t.title = t.title[:38]
        t.author = t.author[:38] 

    for k in listing:
        k.type = k.__class__.__name__

    return render_to_response('publication/posts.html', {
            'posts': texts,
            'imgform': imgform,
            'tracks': tracks,
            'images': images,
			'listing': listing, 
  	        'radio': radio_list
        }, context_instance=RequestContext(request))


def MakeStreamList(texts, images, tracks, files):
    listing = sorted(chain(texts, images, tracks, files))

    listing = sorted(
        chain(texts, images, tracks, files),
        key=lambda instance: instance.created)

    listing.reverse()
    return listing

def songPlayingNow(request):
    returnjson = {
        'playhead':'', 
		'song': 'Something'  
            }
    timenow = round(time.time())
    returnjson['playhead'] = timenow
    # get the time from the timestap of lastsongplayed

    returndata = json.dumps(returnjson)
    response = HttpResponse(returndata, mimetype='application/json')
    return response

def GetPlaylist(request): 
    # look for tracks in playlist 
    radio_list = getlastplaylist()
   
    if len(radio_list) < 5: 
        addsongtoplaylist()

    radio_list = getlastplaylist()

    print "----------------- radio list ->", radio_list


    returnjson = fixlist(radio_list)
    current_track = radio_list[0].track
    current_track_in_list = radio_list[0]

    millis = int(round(time.time()*1000))

    try:
        lastsongrequested = LatestSongRequest.objects.get(track = current_track, pk = 1)
    except LatestSongRequest.DoesNotExist:   
        lastsongrequested = LatestSongRequest(track = current_track, pk = 1)
        lastsongrequested.save()
        lastsongrequested = LatestSongRequest.objects.get(track = current_track, pk = 1)

    hours = int(lastsongrequested.track.duration[0])
    minutes = int(lastsongrequested.track.duration[2:4])
    seconds = int(lastsongrequested.track.duration[5:6])
    songduration_milli = (minutes*60 + seconds) * 1000

    if (lastsongrequested.track.pk == current_track_in_list.track.pk):
        epochtime = epoch(lastsongrequested.requesttime)

        lengthofplaying = int(millis - epochtime)
        print lengthofplaying, songduration_milli 
        if lengthofplaying > songduration_milli: 
            removelastsong()
            radio_list = getlastplaylist() 
            returnjson = fixlist(radio_list)
            returnjson['start_playing_at'] = 20000
            # change 
            #lastsongrequested = LatestSongRequest(track = current_track, pk = 1)
            #lastsongrequested.save()
 
        else: 
            returnjson['start_playing_at'] = lengthofplaying

    else: 
        returnjson['start_playing_at'] = 1

    returndata = json.dumps(returnjson)
    response = HttpResponse(returndata, mimetype='application/json')
    return response

def addsongtoplaylist(): 
    track = Track.objects.order_by('?')[0]
    current = track
    try:   
        pl = PlayList.objects.get(pk=1)
    except: 
        pl = PlayList(title = "Radio", description = "A common radio station")
        pl.save()

    try:   
        random_track, created = TrackListed.objects.get_or_create(track = track, playlist = pl, position = 1)
        random_track.save()
    except: 
        pass

    return 1
     
def removelastsong():    
    del_radio_list = getfirstsongofplaylist()
    del_radio_list.delete()
    print del_radio_list
    return 1

def getlastplaylist():
    try:
        radio_list = PlayList.objects.get(pk=1).tracklisted_set.all().order_by('-position')
    except: 
		radio_list = []
    return radio_list

def getfirstsongofplaylist(): 
    obj = PlayList.objects.get(pk=1).tracklisted_set.all()[0]
    return obj

def fixlist(radio_list): 
    returnjson = {
        'type':'',
		'playlist': '',
        'current_track': '',  
        'current': '',
        'start_playing_at':'', 
        'pk':'',
            }

    returnjson['type'] = "List"
    print "eee",  len(radio_list) 
    for t in radio_list: 
        t.track.title = t.track.title[:20]
        t.track.author = t.track.author[:20] 

    radio_list_as_list = []
           
    current_track_in_list = radio_list[0]
    current_pk = current_track_in_list.pk
    current_track = radio_list[0].track
    item = 1

    for track in radio_list:
        temp = {"title":track.track.title, "file":str(track.track.docfile), "track_pk":track.track.pk, "pk":track.pk, "author":track.track.author }
        radio_list_as_list.append(temp)

    returnjson['current_track'] = str(current_track_in_list.track.docfile)
    returnjson['current'] = current_pk
    returnjson['playlist'] = radio_list_as_list  
    returnjson['pk'] = radio_list[0].pk

    return returnjson

def GetLists(request): 
    returnjson = {
        'stream':'', 
		'Message': '',  
        'type':'' 
            }

    try:
        sessionid = request.COOKIES['sessionid']
    except: 
        sessionid = None

    if sessionid == None: 
        try:
            sessionid = request.META['XDG_SESSION_COOKIE'][:32]
        except: 
            hassession = False

    if sessionid == None: 
        hassession = False
        s = SessionStore()
        s.save()
        sessionid = s.session_key
        print sessionid
    else:
        hassession = True

    try: 
        user, create = sessionUser.objects.get_or_create(session_id=sessionid)
        time_threshold = user.last_time_update
        user.save()

        texts = TextPost.objects.filter(created__gte=time_threshold).order_by('-created')
        images = ImagePost.objects.filter(created__gte=time_threshold).order_by('-created')
        tracks = Track.objects.filter(created__gte=time_threshold).order_by('-created')
        files = DocPost.objects.filter(created__gte=time_threshold).order_by('-created')
        returnjson['type'] = "parcial"
    except: 
        texts = TextPost.objects.all().order_by('-created')[:30]
        images = ImagePost.objects.all().order_by('-created')[:10]
        tracks = Track.objects.all().order_by('-created')[:20]
        files = DocPost.objects.all().order_by('-created')[:10]
        returnjson['type'] = "all"


    for t in texts:
        t.created = datetime.strptime(str(t.created)[:19], "%Y-%m-%d %H:%M:%S")

    for i in images:
        i.created = datetime.strptime(str(i.created)[:19], "%Y-%m-%d %H:%M:%S")

    imgform = ImageForm()
    listing = MakeStreamList(texts, images, tracks, files)


    for k in listing:
        k.type = k.__class__.__name__
 

    json_list = serializers.serialize('json', listing)


    returnjson['Message'] = "Your request was granted"
    returnjson['stream'] = json_list
	
    returndata = json.dumps(returnjson)
    response = HttpResponse(returndata, mimetype='application/json')
    return response

def save_img_post(request):
    """
    Saves a ImagePost
    """
    form = ImageForm(request.POST, request.FILES)
    if form.is_valid():
        newdoc = ImagePost(imgfile = request.FILES["file"])
        newdoc.save()
    else:
        print form.errors

def save_message_post(request):
    """
    Saves a MessagePost
    """
    form = TextForm(request.POST)

    if form.is_valid():
        newdoc = TextPost(body = request.POST["body"])
        newdoc.save()   
        return_obj = TextPost.objects.all().order_by('-created')[:1]
    else:
        print form.errors
 
    return return_obj 

def save_doc_post(request):
    """
    Saves a DocPost
    """
    form = DocForm(request.POST, request.FILES)
    if form.is_valid():
        newdoc = DocPost(docfile = request.FILES["file"])
        newdoc.save()
    else:
        print form.errors

def save_audio_post(request):
    """
    Saves a Track
    """
    form = TrackForm(request.POST, request.FILES)
    if form.is_valid():
        the_track_file = request.FILES["file"]
        meta = metadata_for_filelike(the_track_file)
        newdoc = Track(docfile = request.FILES["file"]) 

        try:
            newdoc.title = meta['title']
        except: 
            newdoc.title = request.FILES['file'].name

        try:
            newdoc.album = meta['album']
        except: 
            newdoc.album = 'unspecified'

        try:
            newdoc.author = meta['author']
        except:         
            newdoc.author = 'unspecified'

        try:
            newdoc.duration = meta['duration']
        except:         
            newdoc.duration = 'unspecified'

        try:
            newdoc.music_genre = meta['music_genre']
        except:         
            newdoc.music_genre = 'unspecified'

        newdoc.meta_data = meta
		
        if meta['mime_type'] == 'audio/mpeg':
            newdoc.body = "Audio track: "+newdoc.title+" was uploaded." 
            if request.POST["body"] != "": 
                newdoc.body = newdoc.body+ request.POST["body"]
            newdoc.save() 
 
    else:
        print form.errors

def AddTrackToPlayList(request, track_id):
    if request.method == 'GET':
        print track_id
    try:
        sessionid = request.COOKIES['sessionid']
    except:
        sessionid = None

    if sessionid == None: 
        s = SessionStore()
        s.save()
        sessionid = s.session_key
        print sessionid

    pl = PlayList.objects.get(pk=1)
    try:
        track1 = Track.objects.get(pk=track_id)
    except Track.DoesNotExist:
        raise Http404	

    tracklist = pl.tracklisted_set.all()

    for t in tracklist:
        print t.pk, track1.pk
        if t.pk == track1.pk: 
            in_list = True
        else: 
            in_list = False
	
    p = TrackListed.objects.filter(track=track1)

    if in_list == False:
        try:
    	    track_listed = TrackListed(playlist=pl, track=track1, position = 1)
            print track_listed
        except TrackListed.DoesNotExist:
            pass

    if in_list == True:
        try: 
    	    track_listed = TrackListed.objects.get(playlist=pl, track=track1)
            track_listed.position = track_listed.position + 1
            track_listed.save()	
        except:
            pass
    else:
        count = len(p) + 1
        TrackListed.objects.create(playlist=pl, track=track1, position=count)

    p, created = Vote.objects.get_or_create(session_id=sessionid)

    if created: 
        p.number_of_votes = 1
        p.save()
    else: 
        if p.number_of_votes < 100: 
            p.number_of_votes = p.number_of_votes+1
            p.save()
        else:
            now_more_voting = True


    return HttpResponse(track_id)

def RemoveTrackFromPlaylist(request, track_id):

    pl = PlayList.objects.get(pk=1)
    # here
    try:
    	track_listed = TrackListed.objects.get(playlist=pl, pk=track_id) 
    except TrackListed.DoesNotExist:
       track_listed = None
       raise Http404

    print track_listed
    if track_listed:
        track_listed.delete()
    return HttpResponse(track_id)

def VoteTrackUp(request, track_id): 
    try:
        track1 = Track.objects.get(pk=track_id)
    except Track.DoesNotExist:
        raise Http404	

    pl = PlayList.objects.get(pk=1)

    try:
    	track_listed = TrackListed.objects.get(playlist=pl, track=track1)
    except TrackListed.DoesNotExist:
       track_listed = None

    if track_listed:
        track_listed.position = track_listed.position - 1
        track_listed.save()
    try:
    	track_listed = TrackListed.objects.all()
    except TrackListed.DoesNotExist:
       track_listed = None
 
    return HttpResponse(track_listed)


def VoteTrackDown(request, track_id): 
    try:
        track1 = Track.objects.get(pk=track_id)
    except Track.DoesNotExist:
        raise Http404	

    pl = PlayList.objects.get(pk=1)

    try:
    	track_listed = TrackListed.objects.get(playlist=pl, track=track1)
    except TrackListed.DoesNotExist:
       track_listed = None

    if track_listed:
        track_listed.position = track_listed.position + 1
        track_listed.save()
    try:
    	track_listed = TrackListed.objects.all()
    except TrackListed.DoesNotExist:
       track_listed = None

    return HttpResponse(track_listed)

# help functions 
def metadata_for_filelike(filelike):
    try:
        filelike.seek(0)
    except (AttributeError, IOError):
        return None

    stream = InputIOStream(filelike, None, tags=[])
    parser = guessParser(stream)
	
    if not parser:
        return None

    try:
        metadata = extractMetadata(parser)
    except HachoirError:
        return None

    metas = {}
    for k,v in metadata._Metadata__data.iteritems():
        if v.values:
            metas[v.key] = v.values[0].value
    return metas

from django import template

register = template.Library()

@register.filter
def epoch(value):
    try:
        return int(time.mktime(value.timetuple())*1000)
    except AttributeError:
        return ''


