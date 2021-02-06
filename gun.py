#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import re
import numpy as np
import os.path

# ------------------------------------------------------------------ #
# Project: Auto VFX 自动粘贴视效镜头
# Author: Joe Chan
# Version 1.0
# Date: 2021-02-06
#
# Description: 
#	Read VFX.xml, match the id with R1-R6.xml, grab the start, end, 
#	create a new track in VFX.xml according to reels
# ------------------------------------------------------------------ #

log = open("log.txt","w")

filesgood = True
L = ""
if not(os.path.exists("VFX.xml")):
	L = L + "没找到 VFX.xml\n"
	filesgood = False
if not(os.path.exists("R1.xml")):
	L = L + "没找到 R1.xml\n"
	filesgood = False
if not(os.path.exists("R2.xml")):
	L = L + "没找到 R2.xml\n"
	filesgood = False
if not(os.path.exists("R3.xml")):
	L = L + "没找到 R3.xml\n"
	filesgood = False
if not(os.path.exists("R4.xml")):
	L = L + "没找到 R4.xml\n"
	filesgood = False
if not(os.path.exists("R5.xml")):
	L = L + "没找到 R5.xml\n"
	filesgood = False

if not(filesgood):
	log.write(L)
	log.close()
	quit()

# Open original file
vfx = ET.parse('VFX.xml')
newvfx = ET.parse('VFX.xml')
reel1 = ET.parse('R1.xml')
reel2 = ET.parse('R2.xml')
reel3 = ET.parse('R3.xml')
reel4 = ET.parse('R4.xml')
reel5 = ET.parse('R5.xml')
if os.path.exists("R6.xml"):
	reel6 = ET.parse('R6.xml')
	foundreel6 = True
else:
	foundreel6 = False

# Get root
rootreel1 = reel1.getroot()
rootreel2 = reel2.getroot()
rootreel3 = reel3.getroot()
rootreel4 = reel4.getroot()
rootreel5 = reel5.getroot()
if foundreel6:
	rootreel6 = reel6.getroot()

rootvfx = vfx.getroot()
newrootvfx = newvfx.getroot()

# initialize all vfx items
vfxitems = 0
for elem1 in rootvfx.findall('sequence/media/video/track/clipitem'):
	vfxitems = vfxitems + 1

# Creates a list containing 8 lists, each of vfxitems items, all set to 0
w, h = 8, vfxitems;
vfxslot = [[0 for x in range(w)] for y in range(h)] 
# total 8: 0=id, 1=start, 2=end, 3=length, 4=reel, 5=found, 6=length_correct, 7=reel_length

# create list of vfx items, get the id, start, end
vfxitems = 0
for elem1 in rootvfx.findall('sequence/media/video/track/clipitem'):
	vfxid = elem1.get('id')
	vfxid1 = re.match(r"([a-zA-Z][a-zA-Z][a-zA-Z]_.*)_",vfxid)
	vfxslot[vfxitems][0] = vfxid1.group(1).upper()
	vfxslot[vfxitems][1] = elem1.find('start').text
	vfxslot[vfxitems][2] = elem1.find('end').text
	vfxslot[vfxitems][3] = int(elem1.find('end').text) - int(elem1.find('start').text)
	vfxitems = vfxitems + 1

if foundreel6:
	reel = [rootreel1, rootreel2, rootreel3, rootreel4, rootreel5, rootreel6]
else:
	reel = [rootreel1, rootreel2, rootreel3, rootreel4, rootreel5]

currentreel = 1
for rootreel in reel:
	newvfxtrack = ET.SubElement(newrootvfx.find('sequence/media/video'),'track')
	for elem in rootreel.findall('sequence/media/video/track/generatoritem'):
		for elem1 in rootvfx.findall('sequence/media/video/track/clipitem'):
			vfxid = elem1.get('id').upper()
			vfxid1 = re.match(r"([a-zA-Z][a-zA-Z][a-zA-Z]_.*)_",vfxid)
			if (vfxid1.group(1) == elem.find('name').text.upper()):
				for i in vfxslot:
					if (i[0] == elem.find('name').text.upper()):
						i[4] = currentreel
						i[5] = 1
						i[7] = int(elem.find('end').text) - int(elem.find('start').text)
						if (i[7] == i[3]):
							i[6] = 1
				elem1.find('start').text = elem.find('start').text
				elem1.find('end').text = elem.find('end').text
				newvfxtrack.append(elem1)
	newvfxtrackenable = ET.SubElement(newvfxtrack,'enabled')
	newvfxtrackenable.text = 'TRUE'
	newvfxtracklock = ET.SubElement(newvfxtrack,'locked')
	newvfxtracklock.text = 'FALSE'
	currentreel = currentreel + 1

newvfx.write('newVFX.xml')

found = 0
notfound = 0
for item in vfxslot:
	if (item[5] == 0):
		L = "没找到: " + item[0]
		log.write(L)
		log.write("\n")
		notfound = notfound + 1
	else:
		L = "找到: " + item[0] + " | Reel " + str(item[4])
		log.write(L)
		if (item[6] == 0):
			L = " | 视效长度: " + str(item[3]) + ", 镜头长度: " + str(item[7])
			log.write(L)
		log.write("\n")
		found = found + 1

if foundreel6:
	L = "\n共 6 本\n"
else:
	L = "\n共 5 本\n"
log.write(L)
L = "共找到: " + str(found) + "\n"
log.write(L)
L = "共找不到: " + str(notfound) + "\n"
log.write(L)
L = "总共: " + str(found+notfound) + " 视效"
log.write(L)
log.close()
