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


def parse(text):
	__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
	configParser = ConfigParser.ConfigParser()
	configParser.read(os.path.join(__location__, 'intellection_wrapper.cfg'))
	config = Configuration()
	config.webAddress = configParser.get("Common", "webAddress")
	config.cgiPath = configParser.get("Common", "cgiPath")

	#sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
	#sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

	d_data = {
		"jsonrpc": "2.0",
		"method": "processText",
		"params": {
			"format": "json",
			"argIdent": 0,
			"text": text,
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
	try:
		return json.loads(base64.b64decode(json_format["result"]["boost_serialization"]["datastream"]["content"]).decode('utf-8'))
	except:
		return None
def extract_semantic_relations(text):
	json_results = parse(text)
	if json_results is None:
		return []
	sem = json_results['sem']
	entities = sem['entities']
	words = dict()
	for i in entities:
		words[i['base']['id']] = i['span']
	relations = sem['relations']
	processed_relations = []
	for relation in relations:
		tp = relation['base']['tp']
		parent = words[relation['parent']['id']]
		child = words[relation['child']['id']]
		processed_relations.append({'tp' : tp,
				'parent' : parent,
				'child' : child
			})
	return processed_relations

if __name__ == '__main__':
	sentence = "Он будет чистым."
	relations = (extract_semantic_relations(sentence))
	for i in relations:
		print('\n')
		print('Type', i['tp'])
		begin, end = i['parent']['start'], i['parent']['end']
		print('Parent', sentence[begin:end])
		begin, end = i['child']['start'], i['child']['end']
		print('Child', sentence[begin:end])
