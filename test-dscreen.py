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
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 18)

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
c2 = content.appendContent(
    {"col": 1, "row": 2, "blocktitle": "HEUTE", "content": "Post eingeschrieben abholen", "type": "bulletpoint",
     "color": "black"})
c3 = content.appendContent(
    {"col": 2, "row": 1, "blocktitle": "GEBURI", "content": "GEBURI", "type": "title", "color": "black"})
rowheight = 24
for c in content.content:
    drawblack.text((epd.coloffset[c['col']-1], c['row']*rowheight), c['content'], font=font24, fill=0)
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
for c in content.content:
    drawblack.text((epd.coloffset[c['col']-1], c['row']*rowheight), c['content'], font=font24, fill=0)
HRYimage = convertWhitePxToTransparent(HRYimage)
h_d_img = combineLayers(HBlackimage, HRYimage)
h_d_img.show()


