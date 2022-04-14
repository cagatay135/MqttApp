from django.shortcuts import render
from django.conf import settings

import json
import ast
from dotenv import load_dotenv
import os

import paho.mqtt.client as mqtt


load_dotenv()
HOST = os.getenv("MQTT_HOST")

MIN_ANOMALY = settings.MIN_ANOMALY
MAX_ANOMALY = settings.MAX_ANOMALY


def index(request):
    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe("anomaly_data")

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        data = ast.literal_eval(msg.payload.decode('utf-8'))

        payload = {
            'anomaly_data': data['anomaly_data'],
            'anomaly_status': str(data['anomaly_data'] > MAX_ANOMALY or data['anomaly_data'] < MIN_ANOMALY)
        }

        client.publish("anomaly_data_js_topic_cagatay_curuk", payload=json.dumps(
            payload, indent=2).encode('utf-8'), qos=0, retain=False)

        print(data)

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(HOST)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()

def chart(request):
    return render(request, 'chart.html', {})