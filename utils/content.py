import sys

def getContent(filename):
	fo = open(filename, "r+")
	fileContent = [l for l in fo.readlines()]
	fo.close()
	return fileContent