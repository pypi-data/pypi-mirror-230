from typing import Any, Callable

import json
import paho.mqtt.client as mqtt


class MqttClient:
    def __init__(self, host: str, port: int):
        self.client = mqtt.Client()
        self.client.connect(host, port)

    def publish(self, topic: str, data: Any, serialize: bool = True):
        if serialize:
            data = json.dumps(data)

        self.client.publish(topic, data)


class MqttConsumer:
    def __init__(self, topic: str, host: str, port: int):
        self.topic = topic
        self.host = host
        self.port = port

    def consume(self, cb: Callable[[dict], None], serialize: bool = True):
        self.cb = cb

        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message_callback(serialize)

        client.connect(self.host, self.port)
        client.loop_start()

    def on_connect(self, client, userdata, flags, rc):
        client.subscribe(self.topic)

    def on_message_callback(self, serialize: bool = True):
        def on_message(client, userdata, msg):
            payload = msg.payload.decode("utf-8")
            if serialize:
                payload = json.loads(payload)

            self.cb(payload)

        return on_message
