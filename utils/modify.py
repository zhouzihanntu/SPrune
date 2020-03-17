import re
import operator

from utils.infos import Infos

class Modify:
	# delete emit operation
	def deleteEmit(self, fileContent):
	    pattern4Emit = re.compile(r'emit\s+.*\;')
	    for item in fileContent:
	        result4Emit = pattern4Emit.findall(item.strip())
	        if result4Emit:
	            fileContent.remove(item)
	    return fileContent
	# delete multiply - divide
	def deleteMulDiv(self, fileContent):
	    pattern4MulDiv = re.compile(r'(\.(mul|div|safemul|safediv)\([^)]*\))', flags=re.I)
	    for index, item in enumerate(fileContent):
	        result4MulDiv = pattern4MulDiv.findall(item)
	        if result4MulDiv:
	            for i in result4MulDiv:
	                string = i[0]
	                stringStart = item.find(string)
	                stringEnd = stringStart + len(string)
	                while list(string).count('(') > list(string).count(')'):
	                    nextChar = item[stringEnd]
	                    string += nextChar
	                    stringEnd += 1
	                fileContent[index] = fileContent[index].replace(string, '')
	    return fileContent

	def replaceSuper(self, searchPath, contractFunctionDict, fileContent):
	    pattern4Contract = re.compile(r'\Acontract\W+(\w*)')
	    pattern4Library = re.compile(r'\Alibrary\s+(\w+)\s*\{')
	    pattern4Function = re.compile(r'\Afunction\W+([^\(]*)')
	    pattern4Super = re.compile(r'(super)\.(\w+)\(')
	    currContract = ""
	    currFunc =""
	    caller = ""
	    for idx, line in enumerate(fileContent):
	        result4Contract = pattern4Contract.findall(line.strip())
	        result4Library = pattern4Library.findall(line.strip())
	        result4Function = pattern4Function.findall(line.strip())
	        result4Super = pattern4Super.findall(line)
	        if result4Contract:
	            currContract = result4Contract[0]
	        if result4Library:
	            currContract = ''
	        if result4Function:
	            currFunc = result4Function[0]
	        if result4Super:
	            callFunc = result4Super[0][1]
	            for target in searchPath[currContract][1:]:
	                searchStr = target + '|' + callFunc
	                if contractFunctionDict.__contains__(searchStr):
	                    caller = target
	                    break
	            fileContent[idx] = pattern4Super.sub(caller + "." + callFunc + "(", line)
	    return fileContent

	#generate contract-event list & delete event statement
	def eventList(self, fileContent, searchPath, contractDict):
	    contractEventList = {}
	    contractEventDict = {}
	    pattern4Contract = re.compile(r'(contract|interface)\s+(\w*)')
	    pattern4Event = re.compile(r'event\s+(\w*)')
	    currContract = ''
	    currList = []
	    delList = []
	    eventLine = []
	    for index, line in enumerate(fileContent):
	        result4Contract = pattern4Contract.findall(line)
	        result4Event = pattern4Event.findall(line)
	        if result4Contract:
	            currContract = result4Contract[0][1]
	            currList = []
	        if result4Event and currContract:
	            currList.append(result4Event[0])
	            eventLine.append({'line': line, 'idx': index})
	            contractEventList[currContract] = currList
	    for contract in contractDict.keys():
	        allPath = []

	        for inheritC in searchPath[contract]:
	            if contractEventList.__contains__(inheritC):
	                path = contractEventList[inheritC]
	                allPath.extend(path)
	        contractEventDict[contract] = allPath
	        contractBlock = Infos().getCurrBlock(fileContent, contractDict[contract]['idx'])
	        patternStr = ''
	        for a in allPath:
	            patternStr = patternStr + '|' + a
	        if allPath:
	            pattern4EventCall = re.compile(r'\W('+ patternStr[1:] +')\(')
	            for cLine in contractBlock:
	                result4EventCall = pattern4EventCall.findall(cLine['line'])
	                if result4EventCall:
	                    delList.append(cLine)
	                    #print(result4EventCall)
	                    #print(cLine)
	    delList = delList + eventLine
	    removeList = []
	    for fileIdx, fileLine in enumerate(fileContent):
	        fileItem = {'line': fileLine, 'idx': fileIdx}
	        if fileItem in delList:
	            removeList.append(fileIdx)
	    for r in reversed(removeList):
	        del fileContent[r]

	    return fileContent

	def moveConstructFunc(self, contractFunctionDict, mainContract, fileContent):
	    mainBlock = Infos().getCurrBlock(fileContent, mainContract['idx'])
	    minIdx = mainBlock[-1]['idx']
	    constructFuncIdx = -1
	    for item in contractFunctionDict.keys():
	        if item.split("|")[0] == mainContract['contract']:
	            if contractFunctionDict[item]['idx'] < minIdx:
	                minIdx = contractFunctionDict[item]['idx']
	            if item.split("|")[1] == mainContract['contract']:
	                constructFuncIdx = contractFunctionDict[item]['idx']

	    if constructFuncIdx != -1 and minIdx < constructFuncIdx:
	        funcBlock = Infos().getCurrBlock(fileContent, constructFuncIdx)
	        for f in funcBlock:
	            del fileContent[f['idx']]
	            fileContent.insert(minIdx, f['line'])
	            minIdx = minIdx +1

	    return fileContent

	def EPluribusUnum(self, modSearchOrder, functionSearchOrder, contractList, contractDict, modDict, contractFunctionDict, mainContract, contractConstructorDict, statementDict, searchPath, fileContent):
	    contractInsertion = {}
	    contractFuncInsertion = {}
	    contractStatInsertion = {}
	    constructorInsertion = {}
	    pattern4Constructor = re.compile(r'constructor\s*\(.*\{')
	    #print(contractFunctionDict)
	    for contractItem in contractList:
	        contract = contractItem['contract']
	        funcList = []
	        for contractFunc in contractFunctionDict.keys():
	            if contractFunc.split('|')[0] == contract:
	                funcList.append(contractFunc.split('|')[1])
	        if functionSearchOrder[contract]:
	            contractFuncInsertion.setdefault(contract, [])
	            for func in functionSearchOrder[contract]:
	                fName = func.split('|')[1]
	                if fName not in funcList:
	                    funcList.append(fName)
	                    #print(func)
	                    blockBuffer = Infos().getCurrBlock(fileContent, contractFunctionDict[func]['idx'])
	                    contractFuncInsertion[contract] = contractFuncInsertion[contract] + blockBuffer
	        #modifier
	        modList = []
	        for contractMod in modDict.keys():
	            if contractMod.split('|')[0] == contract:
	                modList.append(contractMod.split('|')[1])
	        if modSearchOrder[contract]:
	            contractFuncInsertion.setdefault(contract, [])
	            for mod in modSearchOrder[contract]:
	                mName = mod.split('|')[1]
	                if mName not in modList:
	                    modList.append(mName)
	                    blockBuffer = Infos().getCurrBlock(fileContent, modDict[mod]['idx'])
	                    contractFuncInsertion[contract] = contractFuncInsertion[contract] + blockBuffer
	        #statements
	        statList = []
	        consList = []
	        for searchC in searchPath[contract]:
	            #print(searchC)
	            #contractFuncInsertion.setdefault(contract, [])
	            contractStatInsertion.setdefault(contract, [])
	            if searchC != contract and statementDict.__contains__(searchC):
	                statList = statementDict[searchC] + statList
	                if contractConstructorDict.__contains__(searchC):
	                    constructorInsertion.setdefault(contract, [])
	                    consList = contractConstructorDict[searchC]["context"][1:-1] + consList
	        if statList:
	            contractStatInsertion[contract] = statList + contractStatInsertion[contract]
	        if consList:
	            constructorInsertion[contract] = consList + constructorInsertion[contract]
	        #constructor

	    contractSeq = []
	    
	    for key in contractList:
	        contractSeq.append(key['contract'])
	    for c in reversed(contractSeq):
	        bBuffer = Infos().getCurrBlock(fileContent, contractDict[c]['idx'])
	        headInsertNode = bBuffer[0]['idx']
	        tailInsertNode = bBuffer[-1]['idx']
	        statementNodeCount = 0

	        if contractFuncInsertion.__contains__(c):
	            for line in contractFuncInsertion[c]:
	                fileContent.insert(tailInsertNode, line['line'])
	                tailInsertNode = tailInsertNode + 1
	        if statementDict.__contains__(c):
	            sInsertNodeAdd = bBuffer[0]['idx']
	            statementNodeCount = statementNodeCount + len(statementDict[c])
	            for s in statementDict[c]:
	                del fileContent[s['idx']]
	                fileContent.insert( sInsertNodeAdd + 1, s['line'])
	                sInsertNodeAdd = sInsertNodeAdd + 1
	        if contractConstructorDict.__contains__(c):
	            constructorInsertNode = contractConstructorDict[c]['idx'] + 1
	            if constructorInsertion.__contains__(c) and constructorInsertion[c]:
	                constructorNodeCount = len(constructorInsertion[c])
	                for line in constructorInsertion[c]:
	                    fileContent.insert(constructorInsertNode, line['line'])
	                    constructorInsertNode = constructorInsertNode + 1
	        if contractStatInsertion[c]:
	            for line in contractStatInsertion[c]:
	                fileContent.insert(headInsertNode + 1, line['line'])
	                headInsertNode = headInsertNode + 1

	    return fileContent

	def delConstructor(self, fileContent, contractConstructorDict, mainContract):
	    constructorDelList = []
	    for item in contractConstructorDict.keys():
	        if item != mainContract['contract']:
	            constructorDelList = constructorDelList + contractConstructorDict[item]['context']
	    constructorDelList = sorted(constructorDelList, key=operator.itemgetter('idx'))
	    for d in reversed(constructorDelList):
	        del fileContent[d['idx']]
	    return fileContent

	def saveRelContract(self, mainContract, contractDict, fileContent):
	    saveList = []
	    saveList.append(mainContract['contract'])
	    pattern4contractInheritance = re.compile(r'contract\s+' + mainContract['contract'] + '(.*)\{')
	    pattern4Instantiation1 = re.compile(r'\W\s*new\s+(\w*)\s*\(')
	    pattern4ElementaryTypeName = re.compile(r'(address|bool|string|int|int8|int16|int24|int32|int40|int48|int56|int64|int72|int80|int88|int96|int104|int112|int120|int128|int136|int144|int152|int160|int168|int176|int184|int192|int200|int208|int216|int224|int232|int240|int248|int256|uint|uint8|uint16|uint24|uint32|uint40|uint48|uint56|uint64|uint72|uint80|uint88|uint96|uint104|uint112|uint120|uint128|uint136|uint144|uint152|uint160|uint168|uint176|uint184|uint192|uint200|uint208|uint216|uint224|uint232|uint240|uint248|uint256|byte|bytes|bytes1|bytes2|bytes3|bytes4|bytes5|bytes6|bytes7|bytes8|bytes9|bytes10|bytes11|bytes12|bytes13|bytes14|bytes15|bytes16|bytes17|bytes18|bytes19|bytes20|bytes21|bytes22|bytes23|bytes24|bytes25|bytes26|bytes27|bytes28|bytes29|bytes30|bytes31|bytes32|fixed|(fixed[0-9]+x[0-9]+)|ufixed|(ufixed[0-9]+x[0-9]+))(\s+|\s*\(|\[)')

	    fileContent[mainContract['idx']] = pattern4contractInheritance.sub('contract ' + mainContract['contract'] + ' {', fileContent[mainContract['idx']])
	    #print(mainContract)
	    for line in fileContent:
	        #if "new " in line:
	        #    print(line)
	        #print(line)
	        result4Instantiation1 = pattern4Instantiation1.findall(line.strip())
	        result4ElementaryTypeName = pattern4ElementaryTypeName.findall(line.strip())
	        if result4Instantiation1 and (result4Instantiation1[0] not in saveList) and not result4ElementaryTypeName:
	            saveList.append(result4Instantiation1[0])
	            #print(line)
	        for contract in contractDict.keys():
	            pattern4Instantiation2 = re.compile(r'' + contract +'\s+\w+.*\=\s*' + contract + '\W*\(')
	            result4Instantiation2 = pattern4Instantiation2.findall(line)
	            if result4Instantiation2 and contract not in saveList:
	                #print(line)
	                saveList.append(contract)
	    delLineList = []
	    for contract in contractDict.keys():
	        if contract not in saveList:
	            #print(fileContent[contractDict[contract]['idx']])
	            blockBuffer = Infos().getCurrBlock(fileContent, contractDict[contract]['idx'])
	            for bLine in blockBuffer:
	                if bLine not in delLineList:
	                    delLineList.append(bLine)

	    delLineList = sorted(delLineList, key=operator.itemgetter('idx'))
	    #print(delLineList)
	    for d in reversed(delLineList):
	        del fileContent[d['idx']]
	    #print(saveList)
	    return fileContent, saveList
