from utils.check import battleChecker, HpMpChecker, TurnChecker, DialogChecker
from utils.mqtt import MQTTClient
import pyautogui
import pygetwindow
import threading
import keyboard
import signal
import json
import time
import psutil


exitApp = False
class Client():
    fairyWindow = ""
    def __init__(self, name):
        fairyWindow = pygetwindow.getWindowsWithTitle("FairyLand")
        if len(fairyWindow) == 0:
            print("init error")
            return
        fairyWindow = fairyWindow[0]
        fairyWindow.moveTo(0, 0)

        print(name, 'is initing...')
        self.battleChecker = battleChecker()
        self.turnChecker = TurnChecker()
        if (name == 'yami'):
            self.mqtt = MQTTClient(name, True)
        else:
            self.mqtt = MQTTClient(name, False)
        self.dialogChecker = DialogChecker(self.battleChecker, self.mqtt)
        
        self.HpMpChecker = HpMpChecker(name, self.mqtt)
        self.teki = [(53,384), (113,439), (156,326), (220,386), (206,274), (269,334), (265,215), (326,275), (373,163), (434,224)]
        self.dialogLocation = [(384, 310), (384, 341), (384, 367), (384, 400)]
        self.mikata = (588, 460)
        self.name = name
        self.handleKey = threading.Thread(target=self.key)
        self.run = threading.Thread(target=self.main)
        self.run.daemon = True
        self.run.start()
        self.handleKey.start()
        self.threads = [self.run, self.handleKey, self.battleChecker.thread, self.HpMpChecker.thread, self.turnChecker.thread]
        print(name, 'is inited')
    def key(self):
        while True:
            key_stroke = keyboard.read_key()
            if key_stroke == 'esc':
                PROCNAME = "python.exe"
                for proc in psutil.process_iter():
                    # check whether the process name matches
                    if proc.name() == PROCNAME:
                        proc.kill()
            elif key_stroke == 'f2':
                self.mqtt.sendData('pause', '1')
            elif key_stroke == 'f3':
                self.mqtt.sendData('pause', '0')
            time.sleep(0.1)
    def clickDialog(self, x, y):
        pyautogui.moveTo(x, y)
        pyautogui.moveTo(x, y)
        pyautogui.mouseDown()
        pyautogui.mouseUp()
        time.sleep(0.5)
        pyautogui.moveTo(384, 310)
        pyautogui.moveTo(384, 310)
        pyautogui.mouseDown()
        pyautogui.mouseUp()
        pyautogui.mouseDown()
        pyautogui.mouseUp()
        unlock = self.mqtt.action
        unlock['perform'] = 1
        self.mqtt.dialog(json.dumps(unlock))

    def main(self):
        while True:
            if not self.battleChecker.battle:
                self.HpMpChecker.battle = False
                self.turnChecker.battle = False
                if self.mqtt.action is not None:
                    while self.mqtt.action['perform'] == 0:
                        num = self.mqtt.action['action']
                        self.clickDialog(self.dialogLocationp[num][0], self.dialogLocationp[num][1])

                if (self.name == 'yami'):
                    if not self.mqtt.pause and self.HpMpChecker.hp > 20 and self.HpMpChecker.mp > 20:
                        pyautogui.keyDown('f5')
                        pyautogui.keyUp('f5')
                if (self.HpMpChecker.hp < 20 or self.HpMpChecker.mp < 20):
                    self.mqtt.sendData('pause', '1')
                    pyautogui.keyDown('f7')
                    pyautogui.keyUp('f7')
            else:
                self.HpMpChecker.battle = True
                self.turnChecker.battle = True
                #if (self.name == 'yami'):
                    #pyautogui.keyDown('f6')
                    #pyautogui.keyUp('f6')
                if True:
                    for teki in self.teki:
                        exist = pyautogui.pixel(teki[0], teki[1]) == (255, 255, 255)
                        while exist:
                            print('teki in {}'.format(teki[0], teki[1]))
                            if (self.name == 'hika'):
                                if self.turnChecker.turns == 1 or self.turnChecker.turns % 3 == 0 or self.turnChecker.turns % 4 == 0:
                                    pyautogui.moveTo(teki[0], teki[1])
                                    pyautogui.keyDown('f6')
                                    pyautogui.keyUp('f6')
                                    pyautogui.keyDown('f6')
                                    pyautogui.keyUp('f6')
                                    pyautogui.keyDown('f6')
                                    pyautogui.keyUp('f6')
                                    pyautogui.mouseDown()
                                    pyautogui.mouseUp()
                                elif self.turnChecker.turns == 2 or self.turnChecker.turns % 7 == 0:
                                    pyautogui.moveTo(self.mikata[0], self.mikata[1])
                                    pyautogui.keyDown('f5')
                                    pyautogui.keyUp('f5')
                                    pyautogui.keyDown('f5')
                                    pyautogui.keyUp('f5')
                                    pyautogui.keyDown('f5')
                                    pyautogui.keyUp('f5')
                                    pyautogui.mouseDown()
                                    pyautogui.mouseUp()
                                else:
                                    pyautogui.keyDown('f8')
                                    pyautogui.keyUp('f8')
                            else:
                                pyautogui.moveTo(teki[0], teki[1])
                                pyautogui.keyDown('f6')
                                pyautogui.keyUp('f6')
                                pyautogui.keyDown('f6')
                                pyautogui.keyUp('f6')
                                pyautogui.keyDown('f6')
                                pyautogui.keyUp('f6')
                                pyautogui.mouseDown()
                                pyautogui.mouseUp()
                            exist = pyautogui.pixel(teki[0], teki[1]) == (255, 255, 255)
            time.sleep(0.3)

if __name__ == '__main__':
    try:
        m = Client('yami')
    except KeyboardInterrupt:
        print('exitnig.')
        exitApp = True
        raise
