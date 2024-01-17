import argparse
import pymongo
import csv
import subprocess
import shlex
import math
import xlsxwriter

parser = argparse.ArgumentParser(
    description="import and count text file lines")
parser.add_argument("-p", "--process", type=str,
                    help="name of the video file to process", nargs="+")
parser.add_argument("-o", "--output", action="store_true",
                    help="export data to xls and csv")
args = parser.parse_args()

myclient = pymongo.MongoClient("mongodb://localhost:27017")
mydb = myclient["Project2"]
col2 = mydb["mycollection2"]

if args.process:
    for video_file in args.process:
        subprocess.run(shlex.split(f"ffmpeg -i {video_file}"))
        subprocess.run(shlex.split(f"ffmpeg -i {video_file} -filter:v 'crop=96:74:920:503' cropped_output.mp4"))

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

for x in col2.find():
    string = x.get("frame_ranges")
    if string is None:
        continue  # Skip this document if 'frame_ranges' key is missing or None
    firstRange = ""
    secondRange = ""
    isSecondRange = False
    if isinstance(string, str) and "-" in string:
        for char in string:
            if char != "-" and isSecondRange == False:
                firstRange = firstRange + char
            if char == "-":
                isSecondRange = True
                continue
            if char != "-" and isSecondRange == True:
                secondRange = secondRange + char
    else:
        firstRange = string

    if (isGreaterTimecode(framesToTimecode(int(firstRange)), videoTimecode) == True):
        continue
    else:
        locations.append(x["location"])
        frames.append(x["frame_ranges"])
        firstTimecode = framesToTimecode(int(firstRange))
        if secondRange != "":
            secondTimecode = framesToTimecode(int(secondRange))
            timecodes.append(firstTimecode.hours + ":" + firstTimecode.minutes + ":" +
                             firstTimecode.seconds + ":" + firstTimecode.frame + " / " + secondTimecode.hours + ":" + secondTimecode.minutes + ":" + secondTimecode.seconds + ":" + secondTimecode.frame)
            middleTimecode.append(middleRangeTimecode(
                int(firstRange), int(secondRange)))
        elif secondRange == "":
            middleTimecode.append(firstTimecode)
            timecodes.append(firstTimecode.hours + ":" + firstTimecode.minutes + ":" +
                             firstTimecode.seconds + ":" + firstTimecode.frame)

if args.output:
    workbook = xlsxwriter.Workbook('project3/project3.xlsx')
    worksheet = workbook.add_worksheet()
    index = 2
    worksheet.write("A1", "Locations")
    worksheet.write("B1", "Frames")
    worksheet.write("C1", "Timecodes")
    worksheet.write("D1", "Thumbnail")
    for location in locations:
        worksheet.write("A"+str(index), location)
        worksheet.write("B"+str(index), frames[index - 2])
        worksheet.write("C"+str(index), timecodes[index - 2])
        subprocess.run(shlex.split("ffmpeg -i cropped_output.mp4 -ss " +
                                   middleTimecode[index - 2].hours + ":" + middleTimecode[index - 2].minutes + ":" + middleTimecode[index - 2].seconds + " -frames:v 1 output" + str(index - 1) + ".jpg"))
        worksheet.insert_image(
            "D"+str(index), "output" + str(index - 1) + ".jpg")
        index = index + 1
    workbook.close()

    fields = ["location", "frames", "timecode"]

    rows = []
    index = 0
    for location in locations:
        rows.append([location, frames[index], timecodes[index]])

    with open("project3.csv", "w") as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(rows)