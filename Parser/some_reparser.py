#!/usr/bin/python
# -*- coding: utf8 -*-
# nlp.isa.ru:8007/cgi-bin/intellection.fcgi

from http import client as httplib
import os
import urllib
import json
import sys
import configparser as ConfigParser
import base64
import codecs

class Configuration:
	def __init__(self):
		self.webAddress = str()
		self.cgiPath = str()


configParser = ConfigParser.ConfigParser()
configParser.read("intellection_wrapper.cfg")
config = Configuration()
config.webAddress = configParser.get("Common", "webAddress")
config.cgiPath = configParser.get("Common", "cgiPath")

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

sentence = "Мама мыла раму."
d_data = {
	"jsonrpc": "2.0",
	"method": "processText",
	"params": {
		"format": "json",
		"argIdent": 0,
		"text": sentence,
		"syntax_parser": 1,
		"semsyn": False
	},
	"id": "1601908510"
}
send_data = json.dumps(d_data, ensure_ascii = True)
send_data = send_data.encode()

headers = {"Content-type": "text/json"}
params = urllib.parse.urlencode({"PROTOCOL": "JSONRPC"})
conn = httplib.HTTPConnection(config.webAddress)
conn.request("POST", config.cgiPath + "?" + params, send_data, headers)
response = conn.getresponse()
data = response.read()

conn.close()
data = data.decode('utf-8')
if response.status != 200:
	raise Exception("Got status {} because '{}'".format(response.status, response.reason))

json_format = json.loads(data)
json_result = json.loads(base64.b64decode(json_format["result"]["boost_serialization"]["datastream"]["content"]).decode('utf-8'))

print(json_result)
