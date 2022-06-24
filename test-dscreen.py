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
# from waveshare_epd import epd5in83b_V2
import time
from PIL import Image, ImageDraw, ImageFont
import traceback


class epd:
    width = 0
    height = 0

    def __init__(self):
        self.width = 0
        self.height = 0


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
    img.show()
    # img.save("mod_img1.png", "PNG")
    return img


def combineLayers(background, foreground):
    # background = Image.open("mod_img1.png")
    # foreground = Image.open("mod_img2.png")
    foreground = foreground.convert("RGBA")
    background.paste(foreground, (0, 0), foreground)
    return background


logging.basicConfig(level=logging.DEBUG)


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
        for block in self.contentBlocks:
            if block['type'] == newentry['title']:
                if block['content'] == newentry['title']:
                    logging.info("blocktitle: already there!")
                    return -1
                else:
                    self.content.append(newentry)
                    return 0
            elif block['type'] == "content":
                self.content.append(block)
                return 1
            else:
                logging.info("block has not type=title")
                return -2
        return -1

    def __str__(self):
        # for x in self.content:
        #    logging.info(x)
        self.content

    def printContentLength(self):
        logging.info("content-length:{}", self.content)


content = ContentHandler('v', '2')
content.printContentLength()
logging.info("Clear...")
# epd.init()
# epd.Clear()
# endregion
logging.info("Goto Sleep...")
# epd.sleep()
# HB
c2 = -3
c3 = -3
# try:
logging.info("epd5in83b_V2 Demo")

# Drawing on the image
logging.info("Drawing")
logging.info(picdir)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
epd = epd()
epd.width = 648
epd.height = 480
# region HorizontalImage: Drawing on the Horizontal image
logging.info("1.Drawing on the Horizontal image...")
HBlackimage = Image.new('1', (epd.width, epd.height), 100)  # 648*480
HRYimage = Image.new('1', (epd.width, epd.height), 100)  # 648*480  HRYimage: red or yellow image
drawblack = ImageDraw.Draw(HBlackimage)
drawry = ImageDraw.Draw(HRYimage)
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
time.sleep(2)
#region VerticalImage
# Drawing on the Vertical image
logging.info("2.Drawing on the Vertical image...")
LBlackimage = Image.new('1', (epd.height, epd.width), 255)
LRYimage = Image.new('1', (epd.height, epd.width), 255)
drawblack = ImageDraw.Draw(LBlackimage)
drawry = ImageDraw.Draw(LRYimage)
# drawry.line((95, 90, 95, 140), fill = 0)
# drawry.line((70, 115, 120, 115), fill = 0)
# drawry.arc((70, 90, 120, 140), 0, 360, fill = 0)
# drawry.rectangle((10, 150, 60, 200), fill = 0)
# drawry.chord((70, 150, 120, 200), 0, 360, fill = 0)

LBlackimage.save("v_blackimage.png", "PNG")
LRYimage.save("v_hryimage.png", "PNG")
LRYimage = convertWhitePxToTransparent(LRYimage)
v_img = combineLayers(LBlackimage, LRYimage)
v_img.show()
v_img.save("v_test.png", 'PNG')
# epd.display(epd.getbuffer(LBlackimage), epd.getbuffer(LRYimage))
time.sleep(2)

logging.info("3.read bmp file")
HBlackimage = Image.open(os.path.join(picdir, '5in83b_V2_b.bmp'))
HRYimage = Image.open(os.path.join(picdir, '5in83b_V2_r.bmp'))
#epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))
time.sleep(2)

logging.info("4.read bmp file on window")
blackimage1 = Image.new('1', (epd.width, epd.height), 255)
redimage1 = Image.new('1', (epd.width, epd.height), 255)
newimage = Image.open(os.path.join(picdir, 'v_100x100.bmp'))
blackimage1.paste(newimage, (50,10))    
#epd.display(epd.getbuffer(blackimage1), epd.getbuffer(redimage1))


# HB
c2 = -3
c3 = -3
# try:
logging.info("epd5in83b_V2 Demo")

# Drawing on the image
logging.info("Drawing")
logging.info(picdir)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)
epd = epd()
epd.width = 648
epd.height = 480
# region HorizontalImage: Drawing on the Horizontal image
logging.info("1.Drawing on the Horizontal image...")
HBlackimage = Image.new('1', (epd.width, epd.height), 100)  # 648*480
HRYimage = Image.new('1', (epd.width, epd.height), 100)  # 648*480  HRYimage: red or yellow image
drawblack = ImageDraw.Draw(HBlackimage)
drawry = ImageDraw.Draw(HRYimage)
drawblack.text((10, 0), 'hello world', font=font24, fill=0)
drawblack.text((10, 20), '5.83inch e-Paper b V2', font=font24, fill=0)
drawblack.text((150, 0), u'微雪电子', font=font24, fill=0)
drawblack.line((20, 50, 70, 100), fill=0)
drawblack.line((70, 50, 20, 100), fill=0)
drawblack.rectangle((20, 50, 70, 100), outline=0)
drawry.line((165, 50, 165, 100), fill=0)
drawry.line((140, 75, 190, 75), fill=0)
drawry.arc((140, 50, 190, 100), 0, 360, fill=0)
drawry.rectangle((80, 50, 130, 100), fill=0)
drawry.chord((200, 50, 250, 100), 0, 360, fill=0)
# epd.display(epd.getbuffer(HBlackimage), epd.getbuffer(HRYimage))

HBlackimage.save("h_hblackimage.png", "PNG")
HRYimage.save("h_hryimage.png", "PNG")
HRYimage = convertWhitePxToTransparent(HRYimage)
h_image = combineLayers(HBlackimage, HRYimage)
h_image.show()
h_image.save("h_test.png", 'PNG')
# test_screen_img = Image.new('RGB', (epd.width, epd.height), (255,255,255))
# Image.merge('RGB',(HRYimage, empty, empty)).save("h_test_screen_red.png", 'PNG')
# img = Image.new('RGB', (epd.width, epd.height), ())).convert('RGB')

# Split into 3 bands, R, G and B
# R, G, B = test_screen_img.split()
# R.show()


# Synthesize empty band, same size as original
empty = Image.new('L', (epd.width, epd.height))

# Make red image from red channel and two empty channels and save
# Image.merge('RGB',(HRYimage,empty,empty)).save("test_screen_red.png")
# red = Image.open("test_screen_red.png")

# Merge all three original RGB bands into new image
# Image.merge('RGB',(R,G,B)).save("_merged.jpg")
# endregion




# Block oben links

# def getBlocks


logging.info("c1:{}", content.appendContent(
    {"col": 1, "row": 1, "blocktitle": "HEUTE", "content": "HEUTE", "type": "title", "color": "black"}))
c2 = content.appendContent(
    {"col": 1, "row": 2, "blocktitle": "HEUTE", "content": "Post eingeschrieben abholen", "type": "bulletpoint",
     "color": "black"})
c3 = content.appendContent(
    {"col": 2, "row": 1, "blocktitle": "GEBURI", "content": "GEBURI", "type": "title", "color": "black"})
logging.info(c2)

content.__str__()
content.printContentLength()


def listfonts():
    import matplotlib
    system_fonts = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    font=""
    fnt = ImageFont.truetype(font, 60)