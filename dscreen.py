from __future__ import print_function
#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
from warnings import catch_warnings
import json
import requests
import logging
import pprint
import base64
from datetime import datetime
from time import sleep
from dotenv import dotenv_values


import time
from PIL import Image, ImageDraw, ImageFont
import traceback

# Logging
logging.basicConfig(level=logging.DEBUG)
picdir = os.sep.join([os.path.dirname(os.path.dirname(os.path.realpath("test_dscreen.py"))), 'e-paper/RaspberryPi_JetsonNano/python/pic'])
libdir = os.sep.join([os.path.dirname(os.path.dirname(os.path.realpath("test_dscreen.py"))),
                      'e-paper/RaspberryPi_JetsonNano/python/lib'])
print(picdir)
print(libdir)
if os.path.exists(libdir):
    sys.path.append(libdir)


def is_raspberrypi():
    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower():
                print("rpi");
                return True
    except Exception: pass
    return False    

class EPaperDisplay:
    width = 0
    height = 0
    font22DISPLAYWIDTH_V = 460
    font22DISPLAYWIDTH_H = font22DISPLAYWIDTH_V * 648 / 480
    font22displaywidth = 0
    font20DISPLAYWIDTH = 0
    coloffset = []
    COLMARGIN = 2
    orientation = 0 # 0:h, 1:v

    def __init__(self, cols, width, height, orientation):
        self.coloffset = []
        self.width = width
        self.height = height
        if orientation == 0:
            self.font22displaywidth = self.font22DISPLAYWIDTH_H
        else:
            self.font22displaywidth = self.font22DISPLAYWIDTH_V
        for c in range(0, cols):
            self.coloffset.append(c * (self.font22displaywidth / cols) + self.COLMARGIN)


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

logging.info("Init and Clear")
if is_raspberrypi():
    from waveshare_epd import epd5in83b_V2
    logging.info("import waveshare")
    epd = epd5in83b_V2.EPD()
    epd.init()
    epd.Clear()
    time.sleep(1)
else:
    # see below 493
    pass

cred = dotenv_values(".dscreen-cred")
dscreen_config = dotenv_values(".dscreen-config")

# Wassertemperatures
## Linth
def getWaterTemperatures(loc_ids):
    staos = loc_ids
    for k,v in staos.items():
        stao = k + ": "
        url = "https://api.existenz.ch/apiv1/hydro/latest?locations=" + str(v)
        payload={}
        headers = {}
        try: 
            response = requests.request("GET", url, headers=headers, data=payload)
            if response.status_code == 200:
                print(response.content)
                testjson = json.loads(response.text)
                print(response.text)
                for p in testjson["payload"]:
                    staos[k] += staos[k].join(str(p["par"]) + ":" + str(p["val"]) + ", ")
                    print(staos)
            else:
                print("api.existenz.ch connection error")
            print(stao[:-2])
        except:
            logging.error("api.existenz.ch connection error")
    return staos
# PiHole stats request
def getPiHole(host, timeout):
    url = host + "/admin/api.php?summary"

    payload = {}
    headers = {}

    response = ""
    stats=""
    try:
        response = requests.request("GET", url, headers=headers, data=payload, timeout=timeout)
        if response.status_code == 200:
            stats = json.loads(response.text)
        else:
            return "api error with status_code:"+str(response.status_code)
        return stats
    except:
        logging.error("No connection to PiHole")
        return "no connection"

def getFritzBoxActiveConnections(host, password, timeout):
    from fritzconnection.lib.fritzhosts import FritzHosts
    numOfActiveClient = "-"
    try:
        fh = FritzHosts(address=host, password=password, use_tls=True,timeout=3000)
        fh_hostsInfo = fh.get_hosts_info()
        testwlanfilter = filter(lambda h : (h['status'] == True and (h['interface_type'] == '802.11')), fh_hostsInfo)
        testwlanlist = list(testwlanfilter)
        testethlist=list(filter(lambda h : (h['status'] == True and (h['interface_type'] == 'Ethernet')), fh_hostsInfo))
        numOfActiveClient = "w:" + str(len(testwlanlist))+ \
                        "|e:" + str(len(testethlist))
    except Exception:
        logging.error("{}: No connection using FritzHosts")
    return numOfActiveClient

# SBB Departures from location
## Himmelrichstrasse
def getStationboard(station, id):
    url = "http://transport.opendata.ch/v1/stationboard?station="+station+"&limit=3&id="+str(id)

    payload={}
    headers = {}
    try:
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
            return ("SBB request error <> 200")
    except:
        return "fail"

# Wasser SeenFlüsse
"""
ReussSeedorf: 2056
ReussLuzern: 2152
LimmatHardbrück: 2099
LinthWeesen: 2104
WalenseeMurg: 2118"""
def getWaterfun(waterfun_loc_ids, timeout):
    waterfun = waterfun_loc_ids
    url = "https://api.existenz.ch/apiv1/hydro/latest?locations="
    hotspots = []
    try:
        for loc, id in waterfun.items():

            payload={}
            headers = {}

            response = requests.request("GET", url + str(id), headers=headers, data=payload, timeout=timeout)

            data = json.loads(response.text)
            logging.info(data)
            hotspot = loc + ": "
            for i in range(len(data['payload'])):
                hotspot += str(data['payload'][i]['val']) + " | "
            logging.info(hotspot)
            hotspots.append(hotspot[:-2])
    except:
        logging.error("No connection to api.existenz.ch")
        return hotspots
    return hotspots

# Meteo Forecast https://developer.srgssr.ch/apis/srf-weather/docs
""" 
Kriens: 47.0330,8.2791
Luzern: 47.0384,8.3135
Mols: 47.1120,9.2810
8057: 47.4001,8.5415
"""
def getMeteoForecast(geolocId):
    url = "https://api.srgssr.ch/srf-meteo/forecast/" + str(geolocId)
    token = ""
    tries = 0
    token = getMeteoToken()
    payload = {}
    headers = {
    'geolocationId': '',
    'Authorization': 'Bearer ' + str(token)
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    while(response.status_code != 200 and tries < 2):
        

        """ Error codes
        400	Invalid request
        401	Invalid or expired access token
        404	Resource not found"""
        tries = tries + 1
        if(response.status_code == 202 or response.status_code ==401):
            # create new token
            token = getMeteoToken()
        else:
            pass
    data = json.loads(response.text)
    with open('forecast.json', 'w') as f:
        f.writelines(response.text)
    rainPossibility = data
    return rainPossibility

def getMeteoToken():
    url = "https://api.srgssr.ch/oauth/v1/accesstoken?grant_type=client_credentials"
    consumerKey = ""
    base64enc = base64.b64encode('data to be encoded'.encode('ascii'))
    payload = {}
    headers = {
        'Authorization': 'Basic ' + cred['srfmeteo_auth'],
        'Cache-Control': 'no-cache',
        'Content-Length': '0'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    token = json.loads(response.text)
    return token['access_token']


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
    # The file dscreen-cred.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    from google.oauth2 import service_account
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    #SERVICE_ACCOUNT_FILE = 'dscreen-cred.json'
    from google.cloud import storage
    
    credentials = service_account.Credentials.from_service_account_info(
            json.loads(cred['google_calendar_credentials']))
    try:
        service = build('calendar', 'v3', credentials=credentials)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId=cred['google_calendar_id'], timeMin=now,
                                            maxResults=10, singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Prints the start and name of the next 10 events
        eventlist = []
        from datetime import datetime

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['start'])
            if len(start) > 10:
                startdt =datetime.strptime(start, "%Y-%m-%dT%H:%M:%S%z")
                start = startdt.strftime("%d.%m %H:%M")
            else:
                startdt = datetime.strptime(start, "%Y-%m-%d")
                start = startdt.strftime("%d.%m         ")
            eventlist.append(start+" "+ event['summary'])
            start = ""


    except HttpError as error:
        logging.error('Google Calendar:An error occurred: %s' % error)
    return eventlist

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
        contentLen = len(self.content)
        self.content.append(newentry)
        if contentLen < len(self.content):
            return 0
        return -1

    def __str__(self):
        return pprint.pformat(self.content)

    def printContentLength(self):
        logging.info("content-length:%s", str(self.content.__len__()))




c2 = -3
c3 = -3
# try:

# Drawing on the image
logging.info("Drawing")
logging.info(picdir)
font22 = ImageFont.truetype(os.path.join(picdir, 'calibrib.ttf'), 24)
font20 = ImageFont.truetype(os.path.join(picdir, 'calibri.ttf'), 18)

#endregion
##################################### test dynamic content

logging.info("dynamic content")
content = ContentHandler('h', 2)
logging.info("2.Drawing on the horizontal image dynamic...")
if is_raspberrypi():
    epd = epd
    logging.info("is raspberry pi")
else:
    # for debugging purpose
    epd = EPaperDisplay(json.loads(dscreen_config['dscreen_col_config'])["numOfCols"], json.loads(dscreen_config["e_paper_resolution"])[0], json.loads(dscreen_config["e_paper_resolution"])[1], int(dscreen_config['dscreen_orientation']))
#LBlackimage = Image.new('1', (epd.width, epd.height), 255)
#LRYimage = Image.new('1', (epd.width, epd.height), 255)
#drawblack = ImageDraw.Draw(LBlackimage)
#drawry = ImageDraw.Draw(LRYimage)
HBlackimage = Image.new('1', (epd.width, epd.height), 255)
HRYimage = Image.new('1', (epd.width, epd.height), 255)
drawblack = ImageDraw.Draw(HBlackimage)
drawry = ImageDraw.Draw(HRYimage)
time.sleep(2)

#region Collect content and append to blocks
# Get Calendar
c1 = content.appendContent(
    {"col": 1, "row": 1, "blocktitle": "HEUTE", "content": "HEUTE", "type": "title", "color": "black"})
calendarEvents = getCalendarEvents()
for event in calendarEvents:
    text = event
    content.appendContent({"col": 1, "row": 1, "blocktitle": "HEUTE", "content": str(text), "type": "bulletpoint", "color": "black"})
# Get Waterfun
hotspots = getWaterfun(json.loads(dscreen_config['waterfun_loc_ids']), 1700)
c38 = content.appendContent(
            {"col": 2, "row": 1, "blocktitle": "Water", "content": "WATER m^3/s | m.ü.M. | °C", "type": "title", "color": "black"})
for hotspot in hotspots:
    if hotspot != "":
            c38c = content.appendContent(
            {"col": 2, "row": 1, "blocktitle": "Water", "content": hotspot, "type": "bulletpoint", "color": "black"})
# Get Bus departme   
stationboardlist = getStationboard(dscreen_config['sbb_stationboard_station'], int(dscreen_config['sbb_stationboard_id']))
c4 = content.appendContent({"col": 1, "row": 3, "blocktitle": "FAHRPLAN", "content": "FAHRPLAN", "type": "title"})

busnr = 0
for bus in stationboardlist:
    content.appendContent({"col": 1, "row": 1, "blocktitle": "FAHRPLAN", "content": str(bus), "type": "bulletpoint", "color": "black"})
# Get Forecast of weather
areas = json.loads(dscreen_config['srfmeteo_loc_ids'])
content.appendContent({"col": 2, "row": 1, "blocktitle": "FORECAST", "content": "FORECAST", "type": "title"})
for name, geolocId in areas.items():
    forecast = getMeteoForecast(geolocId)
    print(type(forecast))
    if 'message' in forecast:
        continue
    logging.info(forecast)
    rainPROBPERC_mm = "17-21h(%|mm): "
    for i in range(len(forecast['forecast']['60minutes'][17:21])):
        rainPROBPERC_mm = rainPROBPERC_mm + "; " + str(17+i) + "h:" + str(forecast['forecast']['60minutes'][i]['PROBPCP_PERCENT']) + "|" + str(forecast['forecast']['60minutes'][i]['RRR_MM'])
    c39 = content.appendContent({"col":2, "row":1, "blocktitle": "FORECAST", "content": "Name:"+name + " FC:" + rainPROBPERC_mm , "type": "radiobutton"})

# Get PiHole
piholestats = getPiHole(dscreen_config['pihole_ip'], 1000)


if piholestats != 'no connection':
    piholestats = "up"
else:
    piholestats = "down"
# Get Number of active clients
numOfActiveClient = "-"
numOfActiveClient = getFritzBoxActiveConnections(dscreen_config['router_host'], cred['router_password'], timeout=700)
content.appendContent({"col":2,"row":1, "blocktitle": "NETZWERK", "content": "NETZWERK","type":"title", "color":"black"})
content.appendContent({"col":2,"row":1, "blocktitle": "NETZWERK", "content": "Clients: " + numOfActiveClient + "| PiHoleStatus: " + piholestats, "type":"radiobutton", "color": "black"})
# Get LAST UPDATED
from datetime import datetime
now = datetime.now()
nowstr = datetime.strftime(now, "%d.%m.%Y %H:%M")
c83 = content.appendContent(
    {"col": 2, "row": 1, "blocktitle": "LAST UPDATED", "content": "LAST UPDATED", "type": "title", "color": "black"})

c83 = content.appendContent(
    {"col": 2, "row": 1, "blocktitle": "LAST UPDATED", "content": nowstr, "type": "radiobutton", "color": "black"})
#endregion

#region Write screen image from content
# build screen image
rowheight = int(dscreen_config['dscreen_rowheightText'])
rowheightTitle = int(dscreen_config['dscreen_rowheightTitle'])

# Write dynamic content to displayhorizontalcontent
logging.info("num-of-entries:%s", content.content.__len__())
logging.info("content:%s", content.__str__())
# create vertical image from dynamic content
if is_raspberrypi():
    epd = epd
    logging.info("is raspberry pi")
else:
    epd = EPaperDisplay(json.loads(dscreen_config['dscreen_col_config'])["numOfCols"], json.loads(dscreen_config["e_paper_resolution"])[0], json.loads(dscreen_config["e_paper_resolution"])[1], int(dscreen_config['dscreen_orientation']))

cnt_c1 = 1
cnt_c2 = 1

coloffset = [json.loads(dscreen_config['dscreen_col_config'])["colXoffset"][0], json.loads(dscreen_config['dscreen_col_config'])['colXoffset'][1]]
for c in content.content:
    if c['col'] == 1:
        if c['type'] == 'title':
            cnt_c1 += 1
            drawblack.text((coloffset[c['col']-1], cnt_c1*rowheight-rowheight), c['content'], font=font22, fill=0)
        else:
            if len(c['content']) > 40:
                drawblack.text((coloffset[c['col']-1], cnt_c1*rowheight-rowheight), c['content'][:40], font=font20, fill=0)
                cnt_c1 += 1
                drawblack.text((coloffset[c['col']-1], cnt_c1*rowheight-rowheight), c['content'][40:], font=font20, fill=0)
            else:
                drawblack.text((coloffset[c['col']-1], cnt_c1*rowheight-rowheight), c['content']
                            , font=font20, fill=0)
        cnt_c1 = cnt_c1 + 1
    elif c['col'] == 2:
        if c['type'] == 'title':
            cnt_c2 += 1
            drawblack.text((coloffset[c['col']-1], cnt_c2*rowheight-rowheight), c['content'], font=font22, fill=0)

        else:
            if len(c['content']) > 40:
                drawblack.text((coloffset[c['col']-1], cnt_c2*rowheight-rowheight), c['content'][:40], font=font20, fill=0)
                cnt_c2 += 1
                drawblack.text((coloffset[c['col'] - 1], cnt_c2 * rowheight - rowheight), c['content'][40:], font=font20,
                               fill=0)
            else:
                drawblack.text((coloffset[c['col'] - 1], cnt_c2 * rowheight - rowheight), c['content'],
                               font=font20, fill=0)
        cnt_c2 = cnt_c2 + 1
HRYimage = convertWhitePxToTransparent(HRYimage)
h_d_img = combineLayers(HBlackimage, HRYimage)
if is_raspberrypi():
    #epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
    logging.info("display {}".format(type(epd)))
now = datetime.now()
nowstr = datetime.strftime(now, "%d.%m.%Y %H:%M")
sleep(1)
#if not is_raspberrypi():
#    h_d_img.show()
if is_raspberrypi():
    epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
else:
    v_img = combineLayers(HBlackimage, HRYimage)
    v_img.show()
    v_img.save("v_test.png", 'PNG')
cnt = 0
#endregion