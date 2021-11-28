import pyautogui
import threading
import json
import time
import base64, io
import requests
from PIL import Image
SERVERURI = 'http://192.168.76.10'
PORT = ':3888'
def getPercent(numa, numb):
  if numa == 0 or numb == 0:
    return 200
  sum = numa + numb
  return int((numa / sum) * 100)

class battleChecker():
    def __init__(self):
        self.battle = False
        self.thread = threading.Thread(target=self.readBattle, args=())
        self.thread.start()
    def readBattle(self):
        while True:
            self.checkBattle()
            time.sleep(1)
    def checkBattle(self):
        battle = pyautogui.screenshot(region=(551, 27, 29, 1))
        battleCondition = self.checkBattleFrame(battle)
        if battleCondition > 80:
            self.battle = False
        else:
            self.battle = True
    def checkBattleFrame(self, battle):
        pixels = battle.load()
        width, height = battle.size

        all_pixel = {'correct': 0, 'incorrect': 0}
        for x in range(width):
            for y in range(height):
                cpixel = pixels[x, y]
                if cpixel[0] < 20 and cpixel[2] > 200:
                    all_pixel['correct'] = all_pixel['correct'] + 1
                else:
                    all_pixel['incorrect'] = all_pixel['incorrect'] + 1
        
        sum = all_pixel['correct'] + all_pixel['incorrect']
        return int((all_pixel['correct'] / sum) * 100)


class HpMpChecker():
    def __init__(self, name, MQTTClient):
        self.name = name
        self.baseX = 21
        self.baseHPy = 32
        self.baseMPy = 44
        self.hp = 999
        self.mp = 999
        self.mqtt = MQTTClient
        self.thread = threading.Thread(target=self.readStatus)
        self.battle = False
        self.thread.start()
    def readStatus(self):
        while True:
            if self.battle:
                thisFrameHp = pyautogui.screenshot(region=(self.baseX+6, self.baseHPy+21, 92, 1))
                thisFrameMp = pyautogui.screenshot(region=(self.baseX+6, self.baseMPy+21, 92, 1))
            else:
                thisFrameHp = pyautogui.screenshot(region=(self.baseX, self.baseHPy, 92, 1))
                thisFrameMp = pyautogui.screenshot(region=(self.baseX, self.baseMPy, 92, 1))
            self.hp = self.checkhp(thisFrameHp)
            self.mp = self.checkmp(thisFrameMp)
            status = {'hp': self.hp, 'mp': self.mp}
            
            self.mqtt.sendData('status', json.dumps(status))
            time.sleep(1)

    def checkhp(self, hp):
        pixels = hp.load()
        width, height = hp.size

        all_pixel = {'red': 0, 'white': 0}
        for x in range(width):
            for y in range(height):
                cpixel = pixels[x, y]
                if cpixel[2] > 200:
                    all_pixel['white'] = all_pixel['white'] + 1
                else:
                    all_pixel['red'] = all_pixel['red'] + 1
        return getPercent(all_pixel['red'], all_pixel['white'])
    def checkmp(self, mp):
        pixels = mp.load()
        width, height = mp.size
        all_pixel = {'blue': 0, 'white': 0}
        for x in range(width):
            for y in range(height):
                cpixel = pixels[x, y]
                if cpixel[0] > 100:
                    all_pixel['white'] = all_pixel['white'] + 1
                else:
                    all_pixel['blue'] = all_pixel['blue'] + 1
        
        
        return getPercent(all_pixel['blue'], all_pixel['white'])


class TurnChecker():
    def __init__(self):
        self.battle = False
        self.turns = 1
        self.thread = threading.Thread(target=self.readTurn)
        self.previousFrame = None
        self.thread.start()
    def readTurn(self):
        while True:
            if not self.battle:
                self.turns = 1
            else:
                if self.previousFrame is None:
                    self.previousFrame = pyautogui.pixel(59, 31)
                else:
                    frame = pyautogui.pixel(59, 31)
                    if self.previousFrame != frame and frame[0] > 188 and frame[0] < 200:
                        self.turns = self.turns + 1
                    self.previousFrame = frame
                print('now in turn {}'.format(self.turns))
            time.sleep(0.2)


class DialogChecker():
    def __init__(self, battleChecker, MQTTClient):
        self.lock = False
        self.battleChecker = battleChecker
        self.mqtt = MQTTClient
        self.thread = threading.Thread(target=self.readDialog)
        self.thread.start()
    def readDialog(self):
        while True:
            if not self.battleChecker.battle:
                dialog = pyautogui.screenshot(region=(241, 122, 302, 292))
                dialogsim = self.getDialogArea(dialog)
                if dialogsim > 50:
                    self.lock = True
                    dialog.save('dialog.png')
                    self.dialoging('dialog.png')
                    self.mqtt.sendData('dialog', json.dumps({'lock': True}))
            else:
                self.lock = False
            time.sleep(0.4)

    def getDialogArea(self, dialog):
        pixels = dialog.load()
        width, height = dialog.size
        
        all_pixel = {'yellow': 0, 'incorrect': 0}
        for x in range(width):
            for y in range(height):
                cpixel = pixels[x, y]
                if cpixel[0] > 200 and cpixel[1] > 100 and cpixel[2] > 75:
                    if cpixel[1] > 200 and cpixel[2] > 200:
                        all_pixel['incorrect'] = all_pixel['incorrect'] + 1
                    else:
                        all_pixel['yellow'] = all_pixel['yellow'] + 1
                else:
                    all_pixel['incorrect'] = all_pixel['incorrect'] + 1
        return getPercent(all_pixel['yellow'], all_pixel['incorrect'])
    def dialoging(self, screen):
        def tobase64(img):
            return base64.b64encode(img).decode('ascii')
        headers = {'Content-type': 'text/xml'}

        URI = '{server}{port}/api/v1/dialog/create'.format(server=SERVERURI, port=PORT, id=id)
        im = Image.open(screen)
        imgByteArr = io.BytesIO()
        im.save(imgByteArr, format="PNG")
        encode = tobase64(imgByteArr.getvalue())
        files = {
            'dialog_checker[image]': encode
        }
        response = requests.post(URI, files=files)
        if response.status_code == 200:
            return True
        else:
            return False