import json
import os
import threading
import time

from paho.mqtt.client import MQTT_LOG_INFO, MQTT_LOG_NOTICE, MQTT_LOG_WARNING, MQTT_LOG_ERR, MQTT_LOG_DEBUG
from paho.mqtt import client as mqtt
from easysmart.device.base_device import BaseDevice


# def print(msg):
#     # write msg to log file
#     with open('log.txt', 'a') as f:
#         f.write(msg + '\n')


def on_log(client, userdata, level, buf):
    if level == MQTT_LOG_INFO:
        head = 'INFO'
    elif level == MQTT_LOG_NOTICE:
        head = 'NOTICE'
    elif level == MQTT_LOG_WARNING:
        head = 'WARN'
    elif level == MQTT_LOG_ERR:
        head = 'ERR'
    elif level == MQTT_LOG_DEBUG:
        head = 'DEBUG'
    else:
        head = level
    print('%s: %s' % (head, buf))


def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    # client.subscribe(topic, 0)


def on_message(client, userdata, msg):
    print('topic:' + msg.topic + ' ' + str(msg.payload))
    try:
        data = json.loads(msg.payload)
    except:
        data = str(msg.payload)
    print(f'{data}')


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected disconnection %s' % rc)


class Manager:

    def __init__(self):
        self.client_id = 'MQTT_MAIN' + os.urandom(6).hex()
        self.client = mqtt.Client(self.client_id, protocol=mqtt.MQTTv311, clean_session=False)
        self.client.on_log = on_log
        self.client.on_connect = on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = on_disconnect
        self.client.connect('mqttserver.local', 1883, 60)
        self.client.loop_start()
        self.client.subscribe('#', 0)
        self.client.subscribe('/dpub/#', 1)
        self.client.subscribe('/all/', 1)
        self.client.subscribe('/test/', 1)
        self.client.publish('/test', 'hello world', 0)

        self.devices = {}

    def subscribe(self, *args, **kwargs):
        return self.client.subscribe(*args, **kwargs)

    def publish(self, topic, payload=None, qos=0, retain=False, properties=None):
        return self.client.publish(topic, payload, qos, retain, properties)

    def loop_forever(self):
        self.client.loop_start()
        self.thread_main()

    def loop_start(self):
        # self._thread_terminate = False
        # self._thread = threading.Thread(target=self.thread_main)
        # self._thread.daemon = True
        # self._thread.start()
        return self.client.loop_start()

    def thread_main(self):
        """
        主线程
        :return: None
        """
        while True:
            time.sleep(1)
            self._seconds_work()

    def _seconds_work(self):
        """
        每秒被调用一次
        :return: None
        """
        # print('seconds work')
        # print 当前设备列表
        print('devices:')
        need_del = []
        for k, v in self.devices.items():
            print(f'{k}: {v}')
            if time.time() - v.last_active_time > 30:
                print(f'device {k} offline')
                need_del.append(k)
        for k in need_del:
            self.devices.pop(k)



    def on_message(self, client, userdata, msg):
        print('topic:' + msg.topic + ' ' + str(msg.payload))
        try:
            data = json.loads(msg.payload)
        except:
            data = str(msg.payload)
            print(f'json.loads error: {data}')
            return
        print(f'{data}')
        self.msg_process(msg, data)
        try:
            self.msg_process(msg, data)
        except Exception as e:
            print(f'on_message error: {e}\n{msg}\n{data}')

    def msg_process(self, msg, data):
        # 如果topic形式为 /dpub/{mac}
        if msg.topic.startswith('/dpub/'):
            mac = msg.topic[6:]
            if mac not in self.devices:
                if data.get('method') == 'report':
                    self.devices[mac] = BaseDevice(mac, data.get('device_type', ''), mqtt_client=self.client)
                    print(f'new device {mac}')
                else:
                    print(f'unknown device {mac} 等待该设备的report信息')
                    return
            method = data.get('method')
            if method == 'report':
                new_data = data.copy()
                new_data.pop('method')
                for k, v in new_data.items():
                    self.devices[mac].update(k, v)
            elif method == 'update':
                key = data.get('key')
                value = data.get('value')
                if key and value:
                    self.devices[mac].update(key, value)

    def get_device(self, mac=None, device_type=None):
        devices = []
        for k, v in self.devices.items():
            if mac and mac != k:
                continue
            if device_type and device_type != v.device_type:
                continue
            devices.append(v)
        return devices


if __name__ == '__main__':
    m = Manager()
    m.loop_start()
