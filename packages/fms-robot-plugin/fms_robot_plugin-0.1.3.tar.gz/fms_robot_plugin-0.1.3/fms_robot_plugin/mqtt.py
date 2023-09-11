from typing import Callable

import json
import logging
import paho.mqtt.client as mqtt


class MqttClient:
    def __init__(self, host: str, port: int):
        self.client = mqtt.Client()
        self.client.connect(host, port)

    def publish(self, topic: str, data: dict, serialize: bool = True):
        if serialize:
            data = json.dumps(data)

        self.client.publish(topic, data)


class MqttConsumer:
    def __init__(self, topic: str, host: str, port: int):
        self.topic = topic
        self.host = host
        self.port = port

    def consume(self, cb: Callable[[dict], None]):
        self.cb = cb

        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(self.host, self.port)
        client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic)

    def on_message(self, client, userdata, msg):
        try:
            print(msg.payload)
            payload = json.loads(msg.payload.decode("utf-8"))
            logging.info(f"[{self.topic}] {payload}")
            self.cb(payload)
        except Exception as e:
            logging.error(e)
