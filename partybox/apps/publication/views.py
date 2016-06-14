from django.conf import settings
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
import threading
import subprocess
import time
from fabric.api import local
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
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

playmode = 'A' 
playing = False
mic = False 

# the project is build on a principal of captive urls    
def CaptureAll(request):
    return HttpResponseRedirect('/home/')

# add post message, jpg, mp3 or pdf
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
        elif fileExtension == '.mp3' or fileExtension == '.MP3':
        	save_audio_post(request)
        elif fileExtension == '.pdf' or fileExtension == '.txt'  or fileExtension == '.rtf':
        	save_doc_post(request)
        elif len(request.POST["body"]) > 1:
            save_message_post(request)
            print "message"
        else:
            print "post is none"
 
    return HttpResponse('200')


def Home(request):  
    return render_to_response('publication/home.html',  context_instance=RequestContext(request))

# helper urls 
def fallback(request):
    return HttpResponseRedirect('/')

def handler404(request):
    return HttpResponseRedirect('/')

# get json format of messages
def JsonMessages(request):
    messages = TextPost.objects.all().order_by('-created')
    json_list = serializers.serialize('json', messages)
    response = HttpResponse(json_list, mimetype='application/json')
    return response

# get json format of images
def JsonImages(request):
    images = ImagePost.objects.all().order_by('-created')
    json_list = serializers.serialize('json', images)
    response = HttpResponse(json_list, mimetype='application/json')
    return response

# get json format of mp3s
def JsonTracks(request): 
    tracks = Track.objects.all().order_by('-created')
    radio_list = getlastplaylist()
    l3 = [x for x in tracks if x not in radio_list]
    print l3
    zx = 0; 
    for t in tracks: 
        if t.author == "unspecified": 
            t.author = ""

        if len(t.title) > 20:
            t.title = t.title[:20] + ".."
        if len(t.author) > 20:
            t.author = t.author[:23] 
             
        if len(t.author) + len(t.author) > 39:
             t.author = t.author[:14] 
      

    json_list = serializers.serialize('json', tracks)
    response = HttpResponse(json_list, mimetype='application/json')
    return response

# get json format of all posts
def JsonPosts(request):
    texts = TextPost.objects.all().order_by('-created')[:30]  
    tracks = Track.objects.all().order_by('-created')[:10]

    for t in tracks: 
        if t.author == "unspecified": 
            t.author = ""

        if len(t.title) > 20:
            t.title = t.title[:20] + ".."
        if len(t.author) > 20:
            t.author = t.author[:23] 
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

# get json format of PDFs
def JsonFiles(request):
    doc_files = DocPost.objects.all().order_by('-created')

    for doc_file in doc_files:
		doc_file.file_name = str(doc_file).rsplit('/',1)[1]
		doc_file.katten = "hsh"
      
    json_list = serializers.serialize('json', doc_files)
    response = HttpResponse(json_list, mimetype='application/json')
    return response

# get all posts
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

def RemoveItemSuggested(track_list, suggest_list): 
    for tracks in track_list:
        if track in suggest_list:
            track.pop
        
def MakeStreamList(texts, images, tracks, files):
    listing = sorted(chain(texts, images, tracks, files))

    listing = sorted(
        chain(texts, images, tracks, files),
        key=lambda instance: instance.created)

    listing.reverse()
    return listing

def playerSongFm(request):
    last_song = GetFirstSongofPlaylist()
    print last_song 
    run('ffmpeg -i ' + last_song + ' -f s16le -ar 22.05k -ac 1 - | sudo ./pifm -')

def songPlayingNow(request):
    returnjson = {
        'playhead':'', 
		'song': ''  
            }
    timenow = round(time.time())
    returnjson['playhead'] = timenow
    
    returndata = json.dumps(returnjson)
    response = HttpResponse(returndata, mimetype='application/json')
    return response

def GetPlaylist(request): 
    # get last play list and assign current track
    radio_list = getlastplaylist()	
    
	# there should always be tracks in the playlist
    if len(radio_list) < 4: 
        AddRandomSongToPlaylist()
        # and get the new list 
        radio_list = getlastplaylist()
    
    # build a jsonlist to return
    returnjson = fixlist(radio_list)
    
    # return the playlist 
    returndata = json.dumps(returnjson)
    response = HttpResponse(returndata, mimetype='application/json')
    return response

def RemoveTrackForPlaylist(request):
    # get playlist       
    radio_list = getlastplaylist()

    # get first track        
    current_track = radio_list[0].track
    # is track old remove it from playlist, returns True or False 
    track_done = IsTrackDone(request, current_track)
    if track_done == True:
        removeLastTrackFromPlaylist()
        
    returndata = json.dumps({"trackremoved":track_done})
    response = HttpResponse(returndata, mimetype='application/json')
    return response
    
# url /removetrack/ used by music player   
def removeLastTrackFromPlaylist(request):   
    radio_list = getlastplaylist()
    track_remove_from_radio_list = radio_list[0]
    
    if track_remove_from_radio_list:   
        init_track = LatestSongRequest(track=track_remove_from_radio_list.track)
        print "init",  init_track
        init_track.save()
        track_remove_from_radio_list.delete()
        
    returndata = json.dumps({"trackremoved":init_track.track.title})
    response = HttpResponse(returndata, mimetype='application/json')
    return response

def RadioRemoveLastTrack():   
    radio_list = getlastplaylist()
    try:
        track_remove_from_radio_list = radio_list[0]
        track_remove_from_radio_list.delete()
    except:
        print "not track to delete"
  
# this function is not needed for the moment    
def IsTrackDone(request, current_track): 
    # set track done to false
    track_is_done = False

	# get current time in milli seconds
    millis = int(round(time.time()*1000))
    
    # get or set timing track
    lastsongrequested = LatestSongRequest.objects.order_by('requesttime')[0]
    print lastsongrequested

    # check to see if the time past is greater then the length of the track   
    epochtime = epoch(lastsongrequested.requesttime)
    lengthofplaying = int(millis - epochtime)
    
    # convert time to milli seconds
    hours = int(lastsongrequested.track.duration[0])
    minutes = int(lastsongrequested.track.duration[2:4])
    seconds = int(lastsongrequested.track.duration[5:6])
    songduration_milli = (minutes*60 + seconds) * 1000
    
    # if the length of playing is greater remove the song from playlist if you are logged in
    if lengthofplaying > songduration_milli: 	        
        if playmode == 'A':
            if request.user.is_authenticated(): 
	            track_is_done = True
        else: 			
            track_is_done = True
                
    return track_is_done
     
def AddRandomSongToPlaylist(): 
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
    return True
     
def getlastplaylist():
    try:
        radio_list = PlayList.objects.get(pk=1).tracklisted_set.all().order_by('-position')
    except: 
		radio_list = []
    return radio_list

def GetFirstSongofPlaylist(): 
    try:  
        obj = PlayList.objects.get(pk=1).tracklisted_set.all().order_by('-position')[0]
        print "to del: ", obj
    except PlayList.DoesNotExist:
        obj = False     
    return obj

def fixlist(radio_list): 
    returnjson = {
        'type':'',
		'playlist': '',
        'current_track': '',  
        'current': '',
        'current_all': '',
        'start_playing_at':'', 
        'pk':'',
            }

    returnjson['type'] = "List"
 
    for t in radio_list: 
        t.track.title = t.track.title[:20]
        if t.track.author == 'unspecified': 
            pass
        else:  
            t.track.author = t.track.author[:20] 

    radio_list_as_list = []
           
    current_track_in_list = radio_list[0]
    current_pk = current_track_in_list.pk
    current_track = radio_list[0].track
    item = 1

    for track in radio_list:
        temp = {"title":track.track.title, "file":str(track.track.docfile), "track_pk":track.track.pk, "pk":track.pk, "author":track.track.author, "position":track.position}
        radio_list_as_list.append(temp)
	
	current = LatestSongRequest.objects.all()
    returnjson['current_all'] = {"title":current[0].track.title, "file":str(current[0].track.docfile), "track_pk":current[0].track.pk, "pk":current[0].pk, "author":current[0].track.author}
    
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
        
def HandelSession(request):
    try:
        sessionid = request.COOKIES['sessionid']
    except:
        sessionid = None

    if sessionid == None: 
        s = SessionStore()
        s.save()
        sessionid = s.session_key


# get requested track by id
def GetTrackById(track_id): 
    try:
        track = Track.objects.get(pk=track_id)
    except Track.DoesNotExist:
        raise Http404
    return track

# get current playlist  
def GetCurrentPlaylist(): 
	playlist = PlayList.objects.get(pk=1)
	return playlist


# Add track to playlist if it is not already in the playlist        
def AddTrackToPlayList(request, track_id):
    if request.method == 'GET':
        print "track_id: ", track_id
        
    #HandelSession(request)

    # get requested track by id
    track_requested = GetTrackById(track_id)
       
    # get current playlist   
    tracklist = GetCurrentPlaylist() 

    # get current playlist set 
    tracklist_set = tracklist.tracklisted_set.all()

    # check if the requested track is in tracklist

    #is_track_listed = IsTrackRequstedInList(track_requested, tracklist_set)
    #print " -------------------  ", is_track_listed 
	# if track is not it tracklist add the track 
    add_track = AddRequestedTrackToPlayList(track_requested, tracklist)
    if add_track:
        print "katten"
    else:
        VoteTrackUp(request, track_id)

    return HttpResponse(track_id)

# check if the requested track is in tracklist
def IsTrackRequstedInList(track_requested, tracklist): 
    in_list = False
    for t in tracklist:
        if t.pk == track_requested.pk:
            in_list = True
    return in_list 

# if track is not it tracklist add the track 			
def AddRequestedTrackToPlayList(track_requested, tracklist):
    try:
        new_track_to_list = TrackListed(playlist=tracklist, track=track_requested, position = 1)
        new_track_to_list.save()
        track_add = True
    except:
        track_add = False
        
    return track_add
    
def RemoveTrackFromPlaylist(request, track_id):

    pl = PlayList.objects.get(pk=1)
    # here
    try:
    	track_listed = TrackListed.objects.get(playlist=pl, pk=track_id) 
    except TrackListed.DoesNotExist:
       track_listed = None
       raise Http404


    if track_listed:
        track_listed.delete()
    return HttpResponse(track_id)

def VoteTrackUp(request, track_id): 
    print "voting up"
    #Playfm()

    # get requested track by id
    track_requested = GetTrackById(track_id)

    # get current playlist   
    tracklist = GetCurrentPlaylist() 

    # get the track as track in tracklist
    
    # get current playlist set 
    
    the_track_voted_for = TrackListed.objects.get(playlist=tracklist, track=track_requested) 

    if the_track_voted_for:
        the_track_voted_for.position = the_track_voted_for.position + 1
        the_track_voted_for.save()
  
    return HttpResponse(the_track_voted_for)

def VoteTrackDown(request, track_id):
    print "voting "
    #Playfm() 
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

# radio logic
global sound 
global talk
global output
global talk_output

def StartFm(request):
    Playfm()

def Playfm(request):
    ffmpeg_process = subprocess.Popen(("omxplayer", "local", last_song_file), stdout=subprocess.PIPE)
    #ffmpeg_process = subprocess.Popen(("ffmpeg", "-i", last_song_file, "-f", "s16le", "-ar", "22.05k", "-ac", "1", "-"), stdout=subprocess.PIPE)
    output = subprocess.check_output(("sudo", "/home/pi/partybox/partybox/pifm", "-" "107.1" "22050"), stdin=ffmpeg_process.stdout)
    ffmpeg_process.wait()

#ffmpeg -i 1.mp3 -f s16le -ar 22.05k -ac 1 - | sudo ./pifm -^C
def playNextSong(request):
    TrackPlayer()
    return HttpResponse("song aling...")


def TrackPlayer():
    StopAudio()     
    global sound
    time.sleep(0.5)
    last_song_pl = GetFirstSongofPlaylist() 

    #t = threading.Thread(target=tracktimer, kwargs={"duration":last_song_pl.track.duration})
    #t.setDaemon(True)
    #t.start()

    last_song_file = str(settings.PROJECT_ROOT) + "/media/" + str(last_song_pl.track.docfile)
    print "playing: ", last_song_file
    RadioRemoveLastTrack()
    AddRandomSongToPlaylist()
    sound = subprocess.Popen(("ffmpeg", "-i", last_song_file, "-f", "s16le", "-ar", "22.05k", "-ac", "1",  "-"), stdout=subprocess.PIPE)
    output = subprocess.Popen(("sudo", "/home/pi/partybox/partybox/pifm", "-", "107.1", "22050"), stdin=sound.stdout)
    

def tracktimer(duration):
    min = duration[2:4]
    sec = duration[5:7]
    timer = (int(min)*60)+int(sec)
    track_playing = True
    time.sleep(timer+2)
    TrackPlayer()
    
def SayRadioGaga(request):
    StopAudio()    
    global sound
    print "radio - gaga ..."
    time.sleep(0.5)
    sound = subprocess.Popen(("ffmpeg", "-i", "/home/pi/partybox/partybox/media/gaga_intro.mp3", "-f", "s16le", "-ar", "22.05k", "-ac", "1", "-"), stdout=subprocess.PIPE)
    output = subprocess.Popen(("sudo", "/home/pi/partybox/partybox/pifm", "-", "107.1", "22050"), stdin=sound.stdout) 
    return HttpResponse("sing along...")

def RadioTalk(request): 
    print "Time to talk"
    k_arecord = os.system('killall arecord')
    StopAudio()    
    time.sleep(0.5)

    talk = subprocess.Popen(["arecord", "-fS16_LE", "-r", "22050", "-Dplughw:1,0", "-d", "100"], stdout=subprocess.PIPE)
    talk_output = subprocess.Popen(("sudo", "/home/pi/partybox/partybox/pifm", "-", "107.1", "22050"), stdin=talk.stdout)
    
    return HttpResponse("start talking...")      

def InterRadiotalk(): 
    k_arecord = os.system('killall arecord')
    StopAudio()    
    talk = subprocess.Popen(["arecord", "-fS16_LE", "-r", "22050", "-Dplughw:1,0", "-d", "100"], stdout=subprocess.PIPE)
    talk_output = subprocess.Popen(("sudo", "/home/pi/partybox/partybox/pifm", "-", "107.1", "22050"), stdin=talk.stdout)
    print "start talking..."      

    return True
 
def StopAudio():
    try:
        k_ffmpeg = os.system('killall ffmpeg')
        termined = True 
    except:
        termined = False

    return termined
      
    
def CheckAudio():
    global sound 
    global talk
    global mic
    try:
        return_code_sound = sound.poll()
        #print "return code sound: ", return_code_sound 
        if return_code_sound == None:
            track_was_on = True
            print "playing ... "
        else: 
            track_was_on = False  
    except:
        track_was_on = False

     
    if track_was_on == False:
        status = "off"
        print "track of"
    else:
        status = "on"
        #print "somethings on"    

    if mic == True: 
        status = "on"
   
    return status

def CheckMic():
    try: 
        print "talk: ", talk.poll, " : ", talk_output.poll
    except:
        print "not taking"     
    
def StartRadio(request):
    global playing 
    global mic
    if playing == False:
        mic = False 
        k_ffmpeg = os.system('killall ffmpeg')
        t = threading.Thread(target=CheckTracking)
        t.setDaemon(True)
        t.start()
        playing = True
     
    return HttpResponseRedirect('/')

def ToggleMic(): 
    global mic
    if mic == True: 
        TrackPlayer()
        mic = False
        time.sleep(2)
        return True

    if mic == False: 
        InterRadiotalk() 
        mic = True
        return True
 

def CheckTracking():
    global mic
    while True:
        
        is_on = CheckAudio()
        input_state = GPIO.input(18)

        if input_state == False:
            ToggleMic()  
            print "toggle mic"

        if is_on == "off":
            TrackPlayer()
            print "track started"    

        time.sleep(1)

