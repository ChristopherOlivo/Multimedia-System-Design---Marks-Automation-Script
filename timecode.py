import subprocess
import re
import math

class TimeCodeUnits:
    def __init__(self, hh, mm, ss, ff):
        self.hours = hh
        self.minutes = mm
        self.seconds = ss
        self.frame = ff


def framesToTimecode(frame):
    ss = math.floor(frame / 60)
    mm = math.floor(ss / 60)
    hh = math.floor(mm / 60)
    ff = math.floor(frame % 60)

    if (len(str(hh)) == 1):
        hh = "0" + str(hh)
    else:
        hh = str(hh)

    if (len(str(mm)) == 1):
        mm = "0" + str(mm)
    else:
        mm = str(mm)

    if (len(str(ss)) == 1):
        ss = "0" + str(ss)
    else:
        ss = str(ss)

    if (len(str(ff)) == 1):
        ff = "0" + str(ff)
    else:
        ff = str(ff)
    return TimeCodeUnits(hh, mm, ss, ff)


def isGreaterTimecode(frameTimecode, videoTimecode):
    if timecodeToFrames(frameTimecode) > timecodeToFrames(videoTimecode):
        return True
    else:
        return False


def timecodeToFrames(timecode):
    sum = 0
    sum = sum + (int(timecode.minutes) * 60)
    sum = sum + (int(timecode.hours * 3600))
    sum = sum + (int(timecode.seconds))
    framerate = sum * 60
    framerate = framerate + int(timecode.frame)
    return framerate


def middleRangeTimecode(firstFrame, secondFrame):
    middleFrame = math.floor((secondFrame - firstFrame) / 2)
    return framesToTimecode(firstFrame + middleFrame)


def printTimecode(timecode):
    print(timecode.hours + ":" + timecode.minutes + ":" +
          timecode.seconds + ":" + timecode.frame)


videoTimecode = TimeCodeUnits("00", "01", "40", "38")
locations = []
frames = []
timecodes = []
middleTimecode = []

# Function to extract timecode information from the video using FFmpeg
def extract_timecode(video_file):
    command = f"ffprobe -v error -show_entries format_tags=timecode -of default=noprint_wrappers=1:nokey=1 {video_file}"
    output = subprocess.check_output(command, shell=True, text=True)
    timecode_data = output.strip()
    timecode_components = re.match(r'(\d+):(\d+):(\d+)\.(\d+)', timecode_data)
    if timecode_components:
        hh, mm, ss, ff = timecode_components.groups()
        return TimeCodeUnits(hh, mm, ss, ff)
    else:
        return None

video_file_path = "/Users/chrisolivo/Desktop/Project3/twitch_nft_demo.mp4"
video_timecode = extract_timecode(video_file_path)

if video_timecode:
    print(f"Video Timecode: {video_timecode.hours}:{video_timecode.minutes}:{video_timecode.seconds}.{video_timecode.frame}")
else:
    print("No timecode information found.")