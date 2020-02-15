import os
import wget
import zipfile
listdir = os.listdir()

if not "model.bin" in listdir:
	model_url = 'http://vectors.nlpl.eu/repository/11/180.zip'
	m = wget.download(model_url)
	model_file = model_url.split('/')[-1]
	with zipfile.ZipFile(model_file, 'r') as archive:
		stream = archive.extract('model.bin')
	os.remove("180.zip")

if not "udpipe_syntagrus.model" in listdir:
	udpipe_url = 'https://rusvectores.org/static/models/udpipe_syntagrus.model'
	modelfile = wget.download(udpipe_url)
