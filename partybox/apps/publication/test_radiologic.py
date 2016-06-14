#import RPi.GPIO as GPIO
import os
import subprocess
import time
base_path = '/media/palle/13d368bf-6dbf-4751-8ba1-88bed06bef77/home/pi/partybox/partybox/'

def StartSongFm():
    PlaySongFm()
    talk_state = False
    MicTracking(talk_state)

# play song if not vioce
def PlaySongFm():
    print "play song"
    kill_all_sound()
    time.sleep(0.5)
    last_song_file = base_path+'media/gaga_intro.mp3'
    omx_process = subprocess.Popen(("ffmpeg", "-i", last_song_file, "-f", "s16le", "-ar", "22.05k", "-ac", "1",  "-"), stdout=subprocess.PIPE)
    #ffmpeg_process = subprocess.Popen(("ffmpeg", "-i", last_song_file, "-f", "s16le", "-ar", "22.05k", "-ac", "1", "-"), stdout=subprocess.PIPE)
    output = subprocess.check_output(("sudo", base_path+"pifm", "-" "107.1" "22050"), stdin=omx_process.stdout)
    # wait for song to play
    omx_process.wait()
    print "stopped"
    PlaySongFm()

def RadioTalk(): 
    kill_all_sound()
    time.sleep(0.1)

    talk = subprocess.Popen(["arecord", "-fS16_LE", "-r", "22050", "-Dplughw:1,0", "-d", "100"], stdout=subprocess.PIPE)
    talk_output = subprocess.Popen(("sudo", base_path+"pifm", "-", "107.1", "22050"), stdin=talk.stdout)
    
    return True     


def MicTracking(talk_state):
    while True:
        
        #input_state = GPIO.input(18)

        # if button press 
        if input_state == False:
            if talk_state == False: 
                talk_state = True
                # enable talk  
                RadioTalk() 
            else: 
                talk_state = False
                PlaySongFm()

        time.sleep(1)
        MicTracking(talk_state)


def kill_all_sound():
    os.system('killall omxplayer.bin')
    os.system('killall ffmpeg')
    os.system('killall arecord')
    return True


StartSongFm()