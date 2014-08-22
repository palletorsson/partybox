from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView
from forms import ImageForm, TrackForm, TextForm
from models import TextPost, ImagePost, Track, PlayList, TrackListed, Vote, sessionUser
from itertools import chain
from django.http import HttpResponse, Http404
from django.core import serializers
import json
from django.http import HttpResponseNotAllowed
from datetime import datetime
from django.contrib.sessions.backends.db import SessionStore

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




def AddPost(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed('Love')

    if request.POST:
        form_type = request.POST["form_type"]

        if form_type == 'image':
        	save_img_post(request)
        elif form_type == 'message':
        	save_message_post(request)
        else:
            save_audio_post(request)
              

    return HttpResponse('200')

def Home(request):
    return render_to_response('publication/home.html')


def JsonMessages(request):
    texts = TextPost.objects.all().order_by('-created')
    json_list = serializers.serialize('json', texts)
    print json_list
    returndata = json.dumps(json_list)

    response = HttpResponse(json_list, mimetype='application/json')
    return response

def JsonTracks(request): 
    tracks = Track.objects.all().order_by('-created')
    json_list = serializers.serialize('json', tracks)
    print json_list
    returndata = json.dumps(json_list)

    response = HttpResponse(json_list, mimetype='application/json')
    return response

def Posts(request):
    texts = TextPost.objects.all().order_by('-created')
    images = ImagePost.objects.all().order_by('-created')
    tracks = Track.objects.all().order_by('-created')

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
    else:
        hassession = True

    if (hassession):
        p, created = sessionUser.objects.get_or_create(session_id=sessionid)
        p.save()
       
    try:
        radio_list = PlayList.objects.get(pk=1).tracklisted_set.all()
    except: 
		radio_list = None

    imgform = ImageForm()
    listing = MakeStreamList(texts, images, tracks)

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


def MakeStreamList(texts, images, tracks):
    listing = sorted(chain(texts, images, tracks))

    listing = sorted(
        chain(texts, images, tracks),
        key=lambda instance: instance.created)

    listing.reverse()
    return listing

def GetPlaylist(request): 
    returnjson = {
        'type':'',
		'playlist': '',
        'current_track': '',  
        'current': '',
            }
    try:
        radio_list = PlayList.objects.get(pk=1).tracklisted_set.all()
    except: 
		radio_list = None
    
    print radio_list

    for t in radio_list: 
        t.track.title = t.track.title[:20]
        t.track.author = t.track.author[:20] 

    radio_list_as_list = []
    radio_list_as_list_titles = []
          
    if radio_list: 
        returnjson['type'] = "List"
        current = radio_list[0].pk
        for track in radio_list:
            temp = {"title":track.track.title, "file":str(track.track.docfile), "pk":track.track.pk, "author":track.track.author }
            radio_list_as_list.append(temp)
        returnjson['current_track'] = str(radio_list[0].track.docfile)
        returnjson['current'] = current 
        returnjson['playlist'] = radio_list_as_list  	
    else: 
        returnjson['type'] = "Random"
        track = Track.objects.order_by('?')[0]
        print track
        returnjson['current_track'] = str(track.docfile)
        returnjson['current'] = track.pk
        temp = {"title":track.title, "file":str(track.docfile), "pk":track.pk, "author":track.author }
        radio_list_as_list.append(temp)
        returnjson['playlist'] = radio_list_as_list
    
    returndata = json.dumps(returnjson)

    response = HttpResponse(returndata, mimetype='application/json')
    return response

def GetLists(request): 
    returnjson = {
        'stream':'', 
		'Message': ''  
            }

    sessionid = request.COOKIES['sessionid']
    
    user = sessionUser.objects.get(session_id=sessionid)
    time_threshold = user.last_time_update

    user.save()

    texts = TextPost.objects.filter(created__gte=time_threshold).order_by('-created')
    images = ImagePost.objects.filter(created__gte=time_threshold).order_by('-created')
    tracks = Track.objects.filter(created__gte=time_threshold).order_by('-created')


    for t in texts:
        t.created = datetime.strptime(str(t.created)[:19], "%Y-%m-%d %H:%M:%S")

    for i in images:
        i.created = datetime.strptime(str(i.created)[:19], "%Y-%m-%d %H:%M:%S")

    imgform = ImageForm()
    listing = MakeStreamList(texts, images, tracks)


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
        newdoc = ImagePost(imgfile = request.FILES["docfile"], body = request.POST['body'])
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

def save_audio_post(request):
    """
    Saves a Track
    """
    form = TrackForm(request.POST, request.FILES)
    if form.is_valid():
        the_track_file = request.FILES["trackfile"]
        meta = metadata_for_filelike(the_track_file)
        print meta
        newdoc = Track(docfile = request.FILES["trackfile"]) 

        try:
            newdoc.title = meta['title']
        except: 
            newdoc.title = request.FILES['trackfile'].name

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

    try:
    	track_listed = TrackListed.objects.get(playlist=pl, track=track1)
    except TrackListed.DoesNotExist:
        track_listed = None

    if track_listed:
        track_listed.position = track_listed.position + 1
        track_listed.save()	
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


