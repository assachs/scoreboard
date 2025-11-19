#!/usr/bin/env -S python  -u
# Display a runtext with double-buffering.
import math
from time import sleep

import sys
sys.path.insert(0, '/home/pi/rpi-rgb-led-matrix/bindings/python/samples/')
sys.path.insert(0, '/home/pi/stomp_ws_py/')

from samplebase import SampleBase
from rgbmatrix import graphics

from stomp_ws.client import Client
import json
import os
import logging
import time
import signal
from threading import Thread
import threading
import socket
from scoreboardbasefunctions import *

class ScoreboardHalle(SampleBase):
    apikey = ''
    spiel = ''
    updatetime = 0
    pingtime = 0
    status = -1
    frame = None
    client = None
    auszeiten = [0,0]
    auszeitenvisible = False
    satzende = 0
    satzendevisible = False
    sbf = None

    noswitch = False;
    switchedsetup = False
    noswitchedback = False

    frontoffsetx = 0
    frontoffsety = 0
    backoffsetx = 192
    backoffsety = 0
    backcontent = "FULL"
    kill_now = False
    def __init__(self, *args, **kwargs):
        super(ScoreboardHalle, self).__init__(*args, **kwargs)
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)
        self.parser.add_argument("-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

        self.sbf = Scoreboardbasefunctions()
        self.sbf.readconfig("/home/pi/scoreboard/rgb/positions.json")


    def exit_gracefully(self, signum, frame):
        logger.info("Stopping, cleaning canvas")
        if not self.kill_now:
            self.kill_now = True
            offscreen_canvas = self.matrix.CreateFrameCanvas()
            offscreen_canvas.Clear()
            self.matrix.SwapOnVSync(offscreen_canvas)
            self.client.disconnect()

    def message(self, frame):
        self.frame = frame

        data = json.loads(frame.body)
        for z in data['teams'][0]['zusatzdaten']:
            if z['text'] == 'Auszeit':
                self.auszeiten[0] = round(time.time()) + 30
                self.auszeitenvisible = True

        for z in data['teams'][1]['zusatzdaten']:
            if z['text'] == 'Auszeit':
                self.auszeiten[1] = round(time.time()) + 30
                self.auszeitenvisible = True

        self.updatetime = time.time()
        self.pingtime = time.time()
        self.updateStatus()
        self.messageShow()

    def messageShow(self):
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        offscreen_canvas.Clear()

        minimizedback = False;
        if self.backcontent != "FULL":
            minimizedback = True;

        if self.frame is not None:
            self.draw_side_data(self.frame, offscreen_canvas,self.frontoffsetx, self.frontoffsety,False, False)
            self.draw_side_data(self.frame, offscreen_canvas,self.backoffsetx, self.backoffsety,True, minimizedback)
        else:
            self.draw_side_nodata(offscreen_canvas, self.frontoffsetx, self.frontoffsety)
            self.draw_side_nodata(offscreen_canvas, self.backoffsetx, self.backoffsety)
        self.draw_status(offscreen_canvas, self.backoffsetx, self.backoffsety)
        self.matrix.SwapOnVSync(offscreen_canvas)

    def draw_side_nodata(self, offscreen_canvas, offsetx, offsety):
        lines = [];
        lines.append(socket.gethostname() + " keine Daten")
        lines.append("-".join(self.spiel.split("-", 3)[:3]) + "-")
        lines.append("-".join(self.spiel.split("-", 3)[3:]))

        for adr in self.sbf.getAdresses():
            lines.append(adr)

        sideCanvas = SideCanvas(offsetx, offsety, offscreen_canvas, self.sbf)
        sideCanvas.drawTextList("nodata", "r", lines)

    @staticmethod
    def calc_teamname(team):
        teamname = team['bezeichnung']
        if len(teamname) > 16:
            teamname = teamname[:16].strip() + "."
        return teamname

    def draw_side_data(self,frame, offscreen_canvas, offsetx, offsety, backside, minimizedback):
        data = json.loads(frame.body)
        a = 0

        switch = False

        if not self.noswitch:
            switch = data['switched']

        if not self.noswitchedback and backside:
            switch = not switch

        if self.switchedsetup:
            switch = not switch

        if switch:
            a = a + 1

        teamA = data['teams'][a]
        teamB = data['teams'][(a+1)%2]
        saetzeA = teamA['saetze']
        saetzeB = teamB['saetze']
        baelleA = teamA['punkteAkt']
        baelleB = teamB['punkteAkt']
        teamlbez = self.calc_teamname(teamA)
        teamrbez = self.calc_teamname(teamB)

        sideCanvas = SideCanvas(offsetx, offsety, offscreen_canvas, self.sbf)

        if self.auszeiten[a] > time.time():
            sideCanvas.drawText("teamL.timeout", "y", str(round(self.auszeiten[a] - time.time())))

        if self.auszeiten[(a+1)%2] > time.time():
            sideCanvas.drawText("teamR.timeout", "y", str(round(self.auszeiten[(a+1)%2] - time.time())))

        if self.satzendevisible:
            satzende = round(self.satzende -  time.time())
            satzendem = math.floor(satzende / 60)
            satzendes = satzende % 60
            timestr = str(satzendem) + ":" + str(satzendes).zfill(2)
            self.sbf.drawtextCenter(offscreen_canvas, "teamnamen", 96 + offsetx, offsety + 25, 'y', timestr)

        sideCanvas.drawText( "teamL.saetze", "y", str(saetzeA))
        sideCanvas.drawText( "teamR.saetze", "y", str(saetzeB))

        sideCanvas.drawText( "teamL.baelle", "w", str(baelleA))
        sideCanvas.drawText( "teamR.baelle", "w", str(baelleB))

        sideCanvas.drawText( "teamL.name", "y", teamlbez)
        sideCanvas.drawText( "teamR.name", "y", teamrbez)

        sideCanvas.drawText("doppelpunkt", "w", ":")

        if teamA['service']:
            sideCanvas.drawLine("teamL.serviceline", "y")

        if teamB['service']:
            sideCanvas.drawLine("teamR.serviceline", "y")

    def draw_status(self, offscreen_canvas, offsetx, offsety):
        color = 'g'
        if self.status > 0:
            color = 'y'
            if self.status == 3:
                color = 'r'
        self.sbf.drawpoint(offscreen_canvas, offsetx, offsety + 63,color)

    def updateStatus(self):
        changed = False
        if (self.status == 0) and (time.time() > self.pingtime + 10):
            self.status = 1
            changed = True
        elif (self.status > 0) and not (time.time() > self.pingtime + 10):
            self.status = 0
            changed = True
        elif self.status == -1:
            self.status = 3
            changed = True

        if (self.auszeiten[0] > time.time() or self.auszeiten[1] > time.time()) and not self.auszeitenvisible:
            self.auszeitenvisible = True
            changed = True
        elif (self.auszeiten[0] <= time.time() and self.auszeiten[1] <= time.time()) and self.auszeitenvisible:
            self.auszeitenvisible = False
            changed = True

        if (self.satzende > time.time()) and not self.satzendevisible:
            self.satzendevisible = True
            changed = True
        elif (self.satzende <= time.time()) and self.satzendevisible:
            self.satzendevisible = False
            changed = True

        if changed or self.auszeitenvisible or self.satzendevisible or self.status==3:
            self.messageShow()

    def refresh(self):
        loop = 0
        while not self.kill_now:
            loop += 1
            loop = loop % 5
            if loop == 0:
                logger.info(str(threading.get_ident()) + " refresh")

            if self.status == -1 or loop == 0 or self.auszeitenvisible or self.satzendevisible:
                self.updateStatus()

            if self.auszeitenvisible or self.satzendevisible:
                sleep(0.2)
            else:
                sleep(1)
        logger.info(str(threading.get_ident()) +  " refresh finished")

    def ping(self):
        self.pingtime = time.time()

    def readconfig(self):
        with open("/etc/scoreboard/match.json") as json_file:
            json_data = json.load(json_file)
            self.spiel = json_data['spieluuid']
            self.apikey = json_data['apikey']
            self.noswitch = json_data['noswitch']
            self.switchedsetup = json_data['switchedsetup']
            self.noswitchedback = json_data['noswitchedback']

            if os.environ['PARALLEL'] == "2":
                self.backoffsetx = 0
                self.backoffsety = 64
            if os.environ['BACK'] == "STATUS":
                self.backoffsetx = 128
                self.backcontent = "STATUS"

    def connect(self, frame):
        logger.info(str(threading.get_ident()) + "OnConnect")
        self.readconfig()

        self.client.subscribe('/topic/' + self.spiel + '/spielstand', callback=self.message)

        self.updatetime = time.time()
        self.pingtime = time.time()

    def connectclient(self):
        logger.info(str(threading.get_ident()) + " entering connectclient")
        #client = Client("wss://bvv-tv-ws-test.bvv.volley.de:8088/tvgrafik/websocket")
        client = Client("wss://bvv-tv-ws.bvv.volley.de:8088/tvgrafik/websocket")

        self.client = client

        client.connect(login="name",
                       headers={"apikey": self.apikey},
                       timeout=0,
                       connectCallback=self.connect,
                       errorCallback=self.onerror,
                       pingCallback=self.ping)
        logger.info(str(threading.get_ident()) + " exiting connectclient")

    def onerror(self, frame):
        logger.error(str(threading.get_ident()) + " onError")
        logger.error(frame)
        self.status = 3
        if not self.kill_now:
            sleep(2)
            logger.info(str(threading.get_ident()) + " onError reconnect")
            self.connectclient()
            logger.info(str(threading.get_ident()) + " onError finished")


    def run(self):
        self.readconfig()
        thread = Thread(target=self.refresh)
        thread.daemon = True
        thread.start()
        logger.info(str(threading.get_ident()) +  " run connect")
        self.connectclient()
        logger.info(str(threading.get_ident()) +  " run connect finished")

# Main function

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    scoreboardHalle = ScoreboardHalle()
    scoreboardHalle.process()
    while not scoreboardHalle.kill_now:
        sleep(5)
    print("Stopped, Main Loop exited")
