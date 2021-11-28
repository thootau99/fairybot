import paho.mqtt.client as mqtt
import json

broker = '192.168.76.7'
port = 1883

class MQTTClient():
    def __init__(self, name, subscribe):
        self.broker = broker
        self.port = port
        self.name = name
        self.client = mqtt.Client(name)
        self.client.connect(broker, port)
        self.client.on_message = self.onMessage
        self.client.on_subscribe = self.onSubscribe
        self.pause = False
        self.characterStatus = {}
        self.pauseStatus = {}
        self.action = None
        if subscribe:
            self.subscribe()

    def onMessage(self, client, userdata, msg):
        if msg.topic == 'action':
            self.action = json.loads(msg.payload)
        else:
            [name, topic] = msg.topic.split('/')
            if topic == 'status':
                if name not in self.characterStatus:
                    value = json.loads(msg.payload)
                    self.characterStatus[name] = value
                else:
                    value = json.loads(msg.payload)
                    if (
                        value['hp'] != self.characterStatus[name]['hp'] or 
                        value['mp'] != self.characterStatus[name]['mp']):
                        self.characterStatus[name] = value
            elif topic == 'pause':
                value = json.loads(msg.payload)
                if value == 1 or value == '1':
                    self.pauseStatus[name] = True
                elif value == 0 or value == '0':
                    self.pauseStatus[name] = False
                for name in self.pauseStatus:
                    if self.pauseStatus[name] == True:
                        self.pause = True
                        return
                self.pause = False


    def onSubscribe(self, client, userdata, mid, granted_qos):
        print(mid)

    def sendData(self, topic, data):
        self.client.publish("{}/{}".format(self.name, topic), data)
    def dialog(self, data):
        self.client.publish("action", data)
    def subscribe(self):
        nodes = [("hika/status", 1), ("hika/pause", 1), ("wiza/status", 1), ("wiza/pause", 1), ("bosu/status", 1), ("bosu/pause", 1), ("yami/status", 1), ("yami/pause", 1), ("ken/status", 1), ("ken/pause", 1), ("action", 1)]
        self.client.subscribe(nodes)
        self.client.loop_start()