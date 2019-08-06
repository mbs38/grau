#!/usr/bin/env python3
# grau, the geek reality assistance unit
# 
# Copyright (C) [2019]  [Max Brueggemann mail@maxbrueggemann.de]
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

###############################################################################

# set conf file paths here:
# csvfile = "/opt/grau/grau.csv"
csvfile = "grau.csv" 
# conffile = "/opt/grau/grau.cfg"
conffile = "grau.cfg"

###############################################################################

import configparser
import time
import paho.mqtt.client as mqtt
import argparse
import csv
import os
import re

config = configparser.ConfigParser()
config.read(conffile)
mqtt_host = str(config.get('broker', 'mqtt_host'))
mqtt_pass = str(config.get('broker', 'mqtt_pass'))
mqtt_user = str(config.get('broker', 'mqtt_user'))
mqtt_port = int(config.get('broker', 'mqtt_port'))

mqc=None
connected=False
thinglist=[]

class thing():
    def __init__(self,name,intopic,outtopic,onpayload,offpayload):
        self.name=name
        self.intopic=intopic
        self.outtopic=outtopic
        self.onpayload=onpayload
        self.offpayload=offpayload
        self.value=None
        
parser = argparse.ArgumentParser(description='Home control from the terminal')
parser.add_argument('command',type=str, choices=['on','off','setval','list','getval'], help='Command.')
parser.add_argument('objectname',nargs='?',type=str, help='Object name like \"lightOutdoors\", case insensitive')
parser.add_argument('value',nargs='?',type=str, help='value to be set using the command setval')

args=parser.parse_args()

def messagehandler(mqc,userdata,msg):
    for thing in thinglist:
        if msg.topic == thing.intopic:
            thing.value = str(msg.payload.decode("utf-8"))

def readConf():
    global csvfile
    with open(csvfile,"r") as csvfile:
        csvfile.seek(0)
        reader=csv.DictReader(csvfile)
        for row in reader:
            alias=row["alias"]               
            intopic = row["intopic"]
            outtopic = row["outtopic"]
            onpayload = row["onpayload"]
            offpayload = row["offpayload"]
            thinglist.append(thing(alias,intopic,outtopic,onpayload,offpayload))
                
def connecthandler(mqc,userdata,flags,rc):
    if rc == 0:
        mqc.initial_connection_made = True
#        mqc.subscribe("blah/+/state/+")
        global connected
        connected=True

def connect_mqtt():
    
    global mqc
    #Setup MQTT Broker
    clientid="grau" + "-" + str(time.time())
    mqc=mqtt.Client(client_id=clientid)
    mqc.on_connect=connecthandler
    mqc.on_message=messagehandler
    mqc.initial_connection_attempted = False
    mqc.initial_connection_made = False
    if len(mqtt_user)>0 and len(mqtt_pass)>0:
        mqc.username_pw_set(mqtt_user, mqtt_pass)
    try:
        mqc.connect(mqtt_host, mqtt_port, 60)
        mqc.initial_connection_attempted = True 
        mqc.loop_start()
    except:
        print("Error connecting to MQTT broker: " + mqtt_host + ":" + str(mqtt_port))
        exit()

def findByName(searchterm):
    outlist=[]
    if "*" not in searchterm:
        for thing in thinglist:
            if thing.name.lower() == searchterm.lower():
                outlist.append(thing)
    else:
        searchterm=searchterm.lower()
        #searchterm=re.sub("^[\*]",".*",searchterm) 
        #regex = "^"+re.sub("\\b[\*]",".+",searchterm)+"$"
        regex = "^"+re.sub("[\*]",".+",searchterm)+"$"
        for thing in thinglist:
            if re.search(regex,thing.name.lower()):
                outlist.append(thing)
    return outlist

def subscribe(thing):
    mqc.subscribe(thing.intopic)



readConf()

if args.command=='list':
    out =""
    if not args.objectname:
        for thing in thinglist:
            out = thing.name +" " + out
        print(out)
    else:
        results = findByName(args.objectname)
        if len(results)>0:
            for thing in results:
                out = thing.name +" " + out 
            print(out)
        else:
            print("\""+str(args.objectname)+"\" not found")

elif args.command=='on' or args.command=='off' or args.command=='setval':
    objects = findByName(str(args.objectname))
    if len(objects)>0:
        connect_mqtt()
        while not connected:
            pass
        for obj in objects:
            if args.command=='on':
                print(obj.name+" --> on")
                mqc.publish(obj.outtopic,"True",qos=1,retain=False)
            elif args.command=='off':
                print(obj.name+" --> off")
                mqc.publish(obj.outtopic,"False",qos=1,retain=False)
            elif args.command=='setval':
                if not args.value:
                    print("No value given.")
                    parser.print_help()
                else:
                    print(obj.name+" --> "+args.value)
                    mqc.publish(obj.outtopic,args.value,qos=1,retain=False)

    else:
        print("\""+str(args.objectname)+"\" not found")

elif args.command=='getval':
    connect_mqtt()
    while not connected:
        pass
    if not args.objectname:
        for thing in thinglist:
            subscribe(thing)
        time.sleep(1)
        for thing in thinglist:
            if thing.value is not None:
                print(thing.name+" = "+str(thing.value))
    else:
        results = findByName(args.objectname)
        if len(results)>0:
            for thing in results:
                subscribe(thing)
            time.sleep(1)
            for thing in thinglist:
                if thing.value is not None:
                    print(thing.name+" = "+str(thing.value))
        else:
            print("\""+str(args.objectname)+"\" not found")

if connected:
    mqc.loop_stop()
    mqc.disconnect()
