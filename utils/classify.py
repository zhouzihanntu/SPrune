import sys
import re

class Classifier:

	def isLoop(self, lineStr):
		isLoop = False
		pattern4Loop = re.compile(r'\A(for|while)\s*\(.+\)')
		result4Loop = pattern4Loop.findall(lineStr)
		if result4Loop:
			isLoop = True
		return isLoop

	def isArrayParam(self, lineStr):
		isArrayParam = False
		pattern4ArrayParam = re.compile(r'\Afunction\s+\w+\([^\)]*(\w+\[\d*\]\s\w+).*\)')
		result4ArrayParam = pattern4ArrayParam.findall(lineStr)
		if result4ArrayParam:
			isArrayParam = True
		return isArrayParam

	def isStructType(self, lineStr):
		isStructType = False
		pattern4Struct = re.compile(r'\Astruct\s+\w+')
		result4Struct = pattern4Struct.findall(lineStr)
		if result4Struct:
			isStructType = True
		return isStructType

	def classifier(self, fileContent):
		for idx, l in enumerate(fileContent):
			line = l.strip()
			if (self.isLoop(line) or self.isArrayParam(line) or self.isStructType(line)):
				return False
		return True