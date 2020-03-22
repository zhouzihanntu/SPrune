import re

from utils.infos import Infos

class VarCheck:
	def getVarDict(self, contractDict, contractFunctionDict, statementDict, fileContent):
		globalVarDict, funcVarDict = {}, {}
		pattern4Struct = re.compile(r'\Astruct\s+(\w+)\s*\{')
		#pattern4Function = re.compile(r'\Afunction\W+([^\(]*)')
		pattern4Variables = re.compile(r'(\W|\A)(address\s+payable|address|bool|string|int|int8|int16|int24|int32|int40|int48|int56|int64|int72|int80|int88|int96|int104|int112|int120|int128|int136|int144|int152|int160|int168|int176|int184|int192|int200|int208|int216|int224|int232|int240|int248|int256|uint|uint8|uint16|uint24|uint32|uint40|uint48|uint56|uint64|uint72|uint80|uint88|uint96|uint104|uint112|uint120|uint128|uint136|uint144|uint152|uint160|uint168|uint176|uint184|uint192|uint200|uint208|uint216|uint224|uint232|uint240|uint248|uint256|byte|bytes|bytes1|bytes2|bytes3|bytes4|bytes5|bytes6|bytes7|bytes8|bytes9|bytes10|bytes11|bytes12|bytes13|bytes14|bytes15|bytes16|bytes17|bytes18|bytes19|bytes20|bytes21|bytes22|bytes23|bytes24|bytes25|bytes26|bytes27|bytes28|bytes29|bytes30|bytes31|bytes32|fixed|(fixed[0-9]+x[0-9]+)|ufixed|(ufixed[0-9]+x[0-9]+))(\[\])?\s+(memory\s+|constant\s+|storage\s+|payable\s+)?(public\s+|private\s+|internal\s+)?(memory\s+|constant\s+|storage\s+|payable\s+)?(\w+)')
		getInfo = Infos()
		for contract in contractDict.items():
			bufferBlock = []
			funcVarDict[contract[0]] = []
			globalVarDict[contract[0]] = []
			for function in contractFunctionDict.items():
				if function[0].split('|')[0] == contract[0]:
					functionBlock = getInfo.getCurrBlock(fileContent, function[1]['idx'])
					bufferBlock = bufferBlock + functionBlock
					result4ArgvVar = pattern4Variables.findall(functionBlock[0]['line'].strip())
					lengthArgvs = len(result4ArgvVar)
					while lengthArgvs:
						if result4ArgvVar[0][-1] not in funcVarDict[contract[0]]:
							funcVarDict[contract[0]].append(result4ArgvVar[0][-1])
						result4ArgvVar = result4ArgvVar[1:]
						lengthArgvs = lengthArgvs - 1
					for funcLine in functionBlock[1:]:
						result4LocalVar = pattern4Variables.findall(funcLine['line'].strip())
						lengthLocalVar = len(result4LocalVar)
						while lengthLocalVar:
							if result4LocalVar[0][-1] not in funcVarDict[contract[0]]:
								funcVarDict[contract[0]].append(result4LocalVar[0][-1])
							result4LocalVar = result4LocalVar[1:]
							lengthLocalVar = lengthLocalVar - 1
			if statementDict.__contains__(contract[0]):
				for statLine in statementDict[contract[0]]:
					result4Struct = pattern4Struct.findall(statLine['line'].strip())
					#result4Function = pattern4Function.findall(statLine['line'].strip())
					#if result4Struct or result4Function:
					if result4Struct:
						continue
					result4GlobalVar = pattern4Variables.findall(statLine['line'].strip())
					lengthGlobalVar = len(result4GlobalVar)
					#if result4GlobalVar:
					#	print(result4GlobalVar, result4GlobalVar[0][-1])
					#	print(statLine['line'])
					while lengthGlobalVar:
						if result4GlobalVar[0][-1] not in globalVarDict[contract[0]]:
							globalVarDict[contract[0]].append(result4GlobalVar[0][-1])
						result4GlobalVar = result4GlobalVar[1:]
						lengthGlobalVar = lengthGlobalVar - 1
		return globalVarDict, funcVarDict
	
	def check(self, contractDict, contractFunctionDict, statementDict, searchPath, fileContent):
		globalVarDict, funcVarDict = self.getVarDict(contractDict, contractFunctionDict, statementDict, fileContent)
		for child in globalVarDict.items():
			#print(child)
			for parent in searchPath[child[0]][1:]:
				#print(parent)
				for pGlobVar in globalVarDict[parent]:
					if pGlobVar in child[1]:
						print("repeat var in parent-child: ", pGlobVar)
						return True
			for fVar in funcVarDict[child[0]]:
				if fVar in child[1]:
					print("repeat var in contract-function: ", fVar)
					return True
		return False