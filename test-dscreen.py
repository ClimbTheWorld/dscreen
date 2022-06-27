from __future__ import print_function
#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath("test_screen.ipynb"))),
                      'e-paper\RaspberryPi_JetsonNano\python\pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath("test_screen.ipynb"))),
                      'e-paper\RaspberryPi_JetsonNano\python\lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
import logging
import pprint
#import pyyaml
from datetime import datetime, timedelta
# from waveshare_epd import epd5in83b_V2
import time
from PIL import Image, ImageDraw, ImageFont
import traceback

class EPaperDisplay:
    width = 0
    height = 0
    FONT24DISPLAYWIDTH_V = 460
    FONT24DISPLAYWIDTH_H = FONT24DISPLAYWIDTH_V * 648 / 480
    font24displaywidth = 0
    FONT18DISPLAYWIDTH = 0
    coloffset = []
    COLMARGIN = 2
    orientation = 0 # 0:h, 1:v

    def __init__(self, cols, width, height, orientation):
        self.coloffset = []
        self.width = width
        self.height = height
        if orientation == 0:
            self.font24displaywidth = self.FONT24DISPLAYWIDTH_H
        else:
            self.font24displaywidth = self.FONT24DISPLAYWIDTH_V
        for c in range(0, cols):
            self.coloffset.append(c * (self.font24displaywidth / cols) + self.COLMARGIN)


def convertWhitePxToTransparent(img):
    # img = Image.open('img.png')
    img = img.convert("RGBA")
    datas = img.getdata()
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    # img.save("mod_img1.png", "PNG")
    return img


def convertPxColor(img, fromColor, toColor):
    # img = Image.open('img.png')
    img = img.convert("RGBA")
    datas = img.getdata()
    intData = []
    newData = []
    intermediateColor = (170, 0, 0, 0)
    for item in datas:
        if item[0] == fromColor:  # and item[1] == 100 and item[2] == 100:
            intData.append(intermediateColor)
        else:
            intData.append(item)
    for item in intData:
        if item[0] == intermediateColor:  # and item[1] == 100 and item[2] == 100:
            newData.append(toColor)
        else:
            newData.append(item)

    img.putdata(newData)
    #img.show()
    # img.save("mod_img1.png", "PNG")
    return img


def combineLayers(background, foreground):
    # background = Image.open("mod_img1.png")
    # foreground = Image.open("mod_img2.png")
    foreground = foreground.convert("RGBA")
    background.paste(foreground, (0, 0), foreground)
    return background


logging.basicConfig(level=logging.DEBUG)
import json
import requests
# Wassertemperaturen
## Linth
staos = {"Linth":2104, "ReussLuzern":2152, "ReussSeedorf":2056}
for k,v in staos.items():
    stao = k + ": "
    url = "https://api.existenz.ch/apiv1/hydro/latest?locations=" + str(v)
    payload={}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    if response.status_code == 200:
        print(response.content)
        testjson = json.loads(response.text)
        for p in testjson["payload"]:
            stao += str(p["par"]) + ":" + str(p["val"]) + ", "
    else:
        print("error")
    print(stao[:-2])
# PiHole stats request
def getPiHole(command, host, port):
    import socket
    s = socket.socket()
    s.connect((host, port))
    str = input(command)
    s.send(str.encode());
    #if (str == "Bye" or str == "bye"):
    #    break
    print("N:", s.recv(1024).decode())
    s.close()
# ÖV
## Himmelrichstrasse
def getStationboard():
    url = "http://transport.opendata.ch/v1/stationboard?station=Kriens, Himmelrichstrasse&limit=3&id=8589714"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        fahrplan = json.loads(response.text)
        stationboard = []
        #fahrplan_from['stationboard'][3]['stop']['station']['name'],
        # fahrplan_to['stationboard'][3]['to'],
        # when[''stationboard'][3]['[departure']['departure']
        numOfDepartures = 0
        if len(fahrplan['stationboard']) >= 4:
            numOfDepartures = 4
        else:
            numOfDepartures = len(fahrplan['stationboard'])
        for i in range(numOfDepartures):
            now = datetime.now()
            #now.ts
            timestampOfDeparture = datetime.fromtimestamp(fahrplan['stationboard'][i]['stop']['departureTimestamp'])
            dfrom =fahrplan['stationboard'][i]['stop']['station']['name'] + " nach "
            dto = fahrplan['stationboard'][i]['to'] + " am: "
            dwhen = fahrplan['stationboard'][i]['stop']['departure']
            #din = timedelta(now, now)
            stationboard.append(fahrplan['stationboard'][i]['stop']['station']['name'].split(", ")[1][:1] + "..." + "-" + \
                            fahrplan['stationboard'][i]['to'].split(", ")[1] + ": " + \
                    fahrplan['stationboard'][i]['stop']['departure'][12:19])
            logging.info(stationboard[len(stationboard)-1])
        return stationboard
    else:
        print("SBB request error <> 200")

# Calendar
#HB
def getCalendarEvents():
    import datetime
    import os.path

    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


    """Shows basic usage of the Google Calendar API for gmail.com-calendards (not G Suite).
    Prints the start and name of the next 10 events on the user's calendar.
    1. Create service account
    2. Grant access to Calendar API for service account
    3. Create key for service account (as credentials.json) and put it into base folder named
    3. Add CalendarId, in code below, which you want to access
        How do I find a calendar ID?
        Obtain your Google Calendar's ID:
        In the Google Calendar interface, locate the "My calendars" area on the left.
        Hover over the calendar you need and click the downward arrow.
        A menu will appear. Click "Calendar settings".
        In the "Calendar Address" section of the screen, you will see your Calendar ID.
    4. Add service account email to calendar which you want to have access to. Go to gmail.com>Calendar>>Settings>Settings for my calendars>Choose calendar>Calendar settings>Share with specific people>Add service account email here
    """
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    from google.oauth2 import service_account
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    SERVICE_ACCOUNT_FILE = 'credentials.json'
    from google.cloud import storage

    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    try:
        service = build('calendar', 'v3', credentials=credentials)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='lukaskempf@gmail.com', timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        eventlist = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            eventlist.append(start+" "+ event['summary'])


    except HttpError as error:
        print('An error occurred: %s' % error)
    return eventlist

#print(response.text)

class ContentHandler():
    content = []
    templ_block = {"col": 1, "row": 1, "content": "HEUTE", "blocktitle": "first title", "type": "title",
                   "color": "black"}
    orientation = "h"  # v or h
    numOfCols = 0
    BLOCKCOUNTER = 0
    contentBlocks = 0

    def __init__(self, orientation, numOfCols):
        self.content = []
        self.orientation = orientation
        self.numOfCols = numOfCols
        self.contentBlocks = []

    def appendContent(self, newentry):
        hasBlockTitle = 0
        #for block in self.content:
        #    if block['type'] == 'title':
        #        if block['blocktitle'] == newentry['blocktitle']:
        #            logging.info("blocktitle: already there!")
        #            return -1
        #        else:
        #            self.content.append(newentry)
        #            return 0
        #    elif block['type'] == "content":
        #        self.content.append(block)
        #        return 1
        #    else:
        #        logging.info("block has not type=title")
        #        return -2
        contentLen = len(self.content)
        self.content.append(newentry)
        if contentLen < len(self.content):
            return 0
        return -1

    def __str__(self):
        return pprint.pformat(self.content)

    def printContentLength(self):
        logging.info("content-length:%s", str(self.content.__len__()))

logging.info("Clear...")
# epd.init()
# epd.Clear()
# endregion
logging.info("Goto Sleep...")
# epd.sleep()

# region VerticalImage
# Drawing on the Vertical image
logging.info("2.Drawing on the Vertical image...")
epd = EPaperDisplay(2, 480, 648, 1)
LBlackimage = Image.new('1', (epd.width, epd.height), 255)
LRYimage = Image.new('1', (epd.width, epd.height), 255)
drawblack = ImageDraw.Draw(LBlackimage)
drawry = ImageDraw.Draw(LRYimage)


c2 = -3
c3 = -3
# try:
logging.info("epd5in83b_V2 Demo")

# Drawing on the image
logging.info("Drawing")
logging.info(picdir)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
ont24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

# Block oben links
drawblack.text((2, 0), 'HEUTE', font=font24, fill=0)
drawblack.text((2, 27), 'Post eingeschrieben abholen', font=font24, fill=0)
drawblack.text((2, 52), 'Denise ob ich am WE mit ihr', font=font24, fill=0)
drawblack.text((2, 77), 'OLG 17.30', font=font24, fill=0)
drawblack.text((2, 102), 'Karton', font=font24, fill=0)

# Block mitte links
drawblack.text((2, 132), 'GEBURI', font=font24, fill=0)
drawblack.text((2, 159), '29.6. Peter', font=font24, fill=0)

# Block unten links
drawblack.text((2, 186), 'REGENJACKE', font=font24, fill=0)
drawblack.text((2, 213), 'Ab16.0070% ', font=font24, fill=0)

# drawblack.text((20, 50), u'微雪电子', font = font18, fill = 0)
# drawblack.line((10, 90, 60, 140), fill = 0)
# drawblack.line((60, 90, 10, 140), fill = 0)
# drawblack.rectangle((10, 90, 60, 140), outline = 0)
# drawry.line((95, 90, 95, 140), fill = 0)
# drawry.line((70, 115, 120, 115), fill = 0)
# drawry.arc((70, 90, 120, 140), 0, 360, fill = 0)
# drawry.rectangle((10, 150, 60, 200), fill = 0)
# drawry.chord((70, 150, 120, 200), 0, 360, fill = 0)
# LBlackimage.save("v_blackimage.png", "PNG")
# LRYimage.save("v_hryimage.png", "PNG")
LRYimage = convertWhitePxToTransparent(LRYimage)
v_img = combineLayers(LBlackimage, LRYimage)
v_img.show()
v_img.save("v_test.png", 'PNG')
# epd.display(epd.getbuffer(LBlackimage), epd.getbuffer(LRYimage))
time.sleep(2)


##################################### test dynamic content
logging.info("dynamic content")
content = ContentHandler('v', 2)
logging.info("2.Drawing on the Vertical image dynamic...")
epd = epd
LBlackimage = Image.new('1', (epd.width, epd.height), 255)
LRYimage = Image.new('1', (epd.width, epd.height), 255)
drawblack = ImageDraw.Draw(LBlackimage)
drawry = ImageDraw.Draw(LRYimage)

c1 = content.appendContent(
    {"col": 1, "row": 1, "blocktitle": "HEUTE", "content": "HEUTE", "type": "title", "color": "black"})
calendarEvents = getCalendarEvents()
for event in calendarEvents:
    content.appendContent({"col": 1, "row": 1, "blocktitle": "HEUTE", "content": str(event), "type": "bulletpoint", "color": "black"})

c2 = content.appendContent(
    {"col": 1, "row": 2, "blocktitle": "HEUTE", "content": "Post eingeschrieben abholen", "type": "bulletpoint",
     "color": "black"})
c3 = content.appendContent(
    {"col": 2, "row": 1, "blocktitle": "GEBURI", "content": "GEBURI", "type": "title", "color": "black"})
stationboardlist = getStationboard()
c4 = content.appendContent({"col": 1, "row": 3, "blocktitle": "FAHRPLAN", "content": "FAHRPLAN", "type": "title"})
busnr = 0
for bus in stationboardlist:
    content.appendContent({"col": 1, "row": 1, "blocktitle": "FAHRPLAN", "content": str(bus), "type": "bulletpoint", "color": "black"})
piholestats = getPiHole(">stats", "127.0.0.1", 4711)
rowheight = 24
cnt = 0
for c in content.content:
    drawblack.text((epd.coloffset[c['col']-1], cnt*rowheight), c['content'], font=font24, fill=0)
    cnt=cnt+1
LRYimage = convertWhitePxToTransparent(LRYimage)
v_d_img = combineLayers(LBlackimage, LRYimage)
v_d_img.show()
logging.info("content:%s", content.__str__())

# dynamic displayhorizontalcontent
logging.info("num-of-entries:%s", content.content.__len__())
logging.info("content:%s", content.__str__())
# create vertical image from dynamic content
epd = EPaperDisplay(2, 648, 480, 0)
HBlackimage = Image.new('1', (epd.width, epd.height), 255)
HRYimage = Image.new('1', (epd.width, epd.height), 255)
drawblack = ImageDraw.Draw(HBlackimage)
drawry = ImageDraw.Draw(HRYimage)
cnt = 1
for c in content.content:
    drawblack.text((epd.coloffset[c['col']-1], cnt*rowheight), c['content'], font=font24, fill=0)
    cnt = cnt + 1
HRYimage = convertWhitePxToTransparent(HRYimage)
h_d_img = combineLayers(HBlackimage, HRYimage)
h_d_img.show()


