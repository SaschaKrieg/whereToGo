#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Plugin für BitBar um in der Mac Menuleiste den Status der Homatice Sensoren der WCs anzuzeigen.
Created on 11.11.2016

@author: Sascha Krieg
'''
import os
import sys
import base64
import json
import codecs
import Tkinter, tkSimpleDialog
from whereToGo.lib import keyring
from whereToGo.lib import jsonrpclib

# ===============================================================================
# Parameter
# ===============================================================================
KEYRING_NAME = "whereToGo"
skriptdir=os.path.join(os.path.dirname(__file__), "whereToGo")
configFile=os.path.join(skriptdir, "whereToGoConfig.json")


#TODO distro erstellen testen
#TODO 3 OG ergänzen
# ===============================================================================
# Main
# ===============================================================================

def main(*argv):
    config=readConfig()
    if len(argv)>1:
        config['territory']=argv[1]
        writeConfig(json.dumps(config))
    else:
        createMenu(config)

def createMenu(config):
    openImage = getImage(config['openImageFile'])
    closeImage = getImage(config['closeImageFile'])
    timeoutImage = getImage(config['timeoutImageFile'])
    selectImage = getImage(config['selectImageFile'])
    transparentImage = getImage(config['transparentImageFile'])

    server = initSever(config['serverUser'],config['serverUrl'])
    territory = config['territory']
    territories = config['territories']
    try:
        status = getValueFromServer(server, territories[territory])
        if status:
            print("|image=" + openImage)
        else:
            print("|image=" + closeImage)
        createSubmenu(server, territories,territory,selectImage,transparentImage)
    except ConnectionException:
        print("|image=" + timeoutImage)

def createSubmenu(server,territories,territory,selectImage,transparentImage):
    print("---")
    for key,valueList in sorted(territories.items()):
        status = getValueFromServer(server, valueList)
        image=transparentImage
        if key==territory:
            image=selectImage
        basicMenuConfig='font="Consolas Bold" bash={} param1={} terminal=false refresh=true image={}'.format(__file__,key,image)
        if status:
            #chr(00) kleiner hack da bitBar Leerzeichen trimmt
            print('{}{:>12} - frei|color=green {}'.format(chr(00),key,basicMenuConfig))
        else:
            print('{}{:>12} - besetzt|color=red {}'.format(chr(00),key,basicMenuConfig))

def writeConfig(config):
    file = codecs.open(configFile, 'w', encoding="utf-8")
    file.write(config)
    file.close()

def readConfig():
    file = codecs.open(configFile, 'r', encoding="utf-8")
    filecontent=file.readlines()
    file.close()
    config=json.loads("".join(filecontent))
    return config

def getValueFromServer(server, valueList):
    status = False
    for value in valueList:
        try:
            if server.GetValueBoolean(value):
                status = True
        except:
            raise ConnectionException()
    return status

def initSever(user,url):
    pw = keyring.get_password(KEYRING_NAME, user)
    if pw is None:
        pw = askPassword()
        keyring.set_password(KEYRING_NAME, user, pw)
    api_endpoint = "http://{}:{}@{}/api/".format(user,pw,url)
    try:
        return jsonrpclib.Server(api_endpoint)
    except:
        raise ConnectionException()

def askPassword():
    root = Tkinter.Tk()  # dialog needs a root window, or will create an "ugly" one for you
    root.withdraw()  # hide the root window
    os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''') #let the dialog pop up to front
    password = tkSimpleDialog.askstring("Password", "Enter password for Hausautomation Autobot API (see TeamVault):", show='*', parent=root)
    root.destroy()  # clean up after yourself!
    return password

def getImage(imageName):
    imageFile = os.path.join(skriptdir,"images", imageName)
    with open(imageFile, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        image =encoded_string
    return image

class ConnectionException(Exception):
    def __init__(self,*args,**kwargs):
        Exception.__init__(self,*args,**kwargs)

# Programm starten
main(*sys.argv)
