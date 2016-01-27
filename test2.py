#! /usr/bin/env python
import json
import splunklib.client as client
HOST = "splunk.levaja.lab"
PORT = 8089
USERNAME = "admin"
PASSWORD = "P@ssw0rd"

service = client.connect(host=HOST,port=PORT,username=USERNAME,password=PASSWORD)
myindex = service.indexes["main"]

mysocket = myindex.attach(sourcetype='Device42', host='d42')

data = "{'foo':'bar'}"
mysocket.send(data)
mysocket.close()