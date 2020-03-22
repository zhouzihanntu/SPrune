import re
import copy
from utils.infos import Infos

class Replace:
	def variableDeduplication(self, fileContent, funcDict, contractDict, contractFunctionDict):
	    #print(contractFunctionDict)
	    fileContentCopy = copy.deepcopy(fileContent)
	    pattern4Variables = re.compile(
	        r'(\W|\A)(address|bool|string|int|int8|int16|int24|int32|int40|int48|int56|int64|int72|int80|int88|int96|int104|int112|int120|int128|int136|int144|int152|int160|int168|int176|int184|int192|int200|int208|int216|int224|int232|int240|int248|int256|uint|uint8|uint16|uint24|uint32|uint40|uint48|uint56|uint64|uint72|uint80|uint88|uint96|uint104|uint112|uint120|uint128|uint136|uint144|uint152|uint160|uint168|uint176|uint184|uint192|uint200|uint208|uint216|uint224|uint232|uint240|uint248|uint256|byte|bytes|bytes1|bytes2|bytes3|bytes4|bytes5|bytes6|bytes7|bytes8|bytes9|bytes10|bytes11|bytes12|bytes13|bytes14|bytes15|bytes16|bytes17|bytes18|bytes19|bytes20|bytes21|bytes22|bytes23|bytes24|bytes25|bytes26|bytes27|bytes28|bytes29|bytes30|bytes31|bytes32|fixed|(fixed[0-9]+x[0-9]+)|ufixed|(ufixed[0-9]+x[0-9]+))\s+(public\s+|private\s+|internal\s+)?(\w+)')
	    currVar = {}
	    for pair in funcDict.items():
	        #print(pair)
	        currContract = Infos().getCurrBlock(fileContent, contractDict[pair[0]]['idx'])
	        for function in pair[1]:
	            varList = []
	            pattern4Function = re.compile(r'function\s' + function + '\(([^()]*)\)')
	            for line in currContract:
	                result4Function = pattern4Function.findall(line['line'])
	                if result4Function:
	                    funcBlock = Infos().getCurrBlock(fileContent, line['idx'])
	                    for b in funcBlock:
	                        result4Variables = pattern4Variables.findall(b['line'])
	                        if result4Variables:
	                            for result in result4Variables:
	                                if result[-1] not in varList:
	                                    varList.append(result[-1])
	            if varList:
	                function = pair[0] + '|' + function
	                currVar[function] = varList
	    contractVarList = []
	    for funcVarPair in currVar.items():
	        for i, v in enumerate(funcVarPair[1]):
	            v = v.replace('_', 'line')
	            count = contractVarList.count(v)
	            contractVarList.append(v)
	            currVar[funcVarPair[0]][i] = {currVar[funcVarPair[0]][i]: v + "X" + str(count)}
	    for funcVar in currVar.items():
	        functionBlock = Infos().getCurrBlock(fileContent, contractFunctionDict[funcVar[0]]['idx'])
	        for code in functionBlock:
	            for varPair in funcVar[1]:
	                for p in varPair.items():
	                    l = fileContentCopy[code['idx']]
	                    #print(p)
	                    pattern4Argv = re.compile(r'[^\.\w]' + (p[0]) + '\W+')
	                    result4Argv = pattern4Argv.findall(l)
	                    if result4Argv:
	                        #print(result4Argv)
	                        for r in result4Argv:
	                            keyStart = r.find(p[0])
	                            keyEnd = r.find(p[0]) + len(p[0])
	                            subKey = r[0:keyStart] + p[1] + r[keyEnd:]
	                            l = l[0:l.find(r)] + subKey + l[l.find(r) + len(r):]
	                            #print(l)
	                        fileContentCopy[code['idx']] = l

	    deduplicatedFile = fileContentCopy

	    return deduplicatedFile

	def argvReplace(self, matchLine, callFunc, contractFuntionStr, currArgvs, countCall, contractFunctionDict, fileContent, varType):
	    pattern4Function = re.compile(r'\A(function|modifier)\W+' + callFunc + '\s?\(([^()]*)\)')
	    pattern4IfCallFunction = re.compile(r'(if|assert|require)\s*\(.*\W*(' + callFunc + '\s*\([^)]*\))')
	    pattern4MultiFunctionCall = re.compile(r'\W(' + callFunc + '\s*\([^)]*\))(\.\w+\([^)]*\))')
	    pattern4Assign = re.compile(r'[^\=]+\=[^\=]+' + callFunc + '\s*\(')
	    pattern4Return = re.compile(r'return\W')
	    argvs = []
	    argvDict = {}
	    functionBlock = Infos().getCurrBlock(fileContent, contractFunctionDict[contractFuntionStr]['idx'])

	    isIfCall = 0
	    isMultiCall = 0
	    isAssign = 0
	    isReturn = 0
	    for idx, item in enumerate(functionBlock):
	        functionBlock[idx] = item['line']
	        result4Function = pattern4Function.findall(item['line'].strip())
	        if result4Function:
	            argvs = result4Function[0][1].split(',')
	            
	            for idx, a in enumerate(argvs):
	                a = a.strip().split(' ')[-1].strip()
	                #a = re.sub(re.compile('^\s+|\s+$'), '', a).split(' ')[-1]
	                if a:
	                    argvs[idx] = a
	    #print(argvs)
	    #function call in if statement, assertion, require
	    result4IfCallFunction = pattern4IfCallFunction.findall(matchLine.strip())
	    pattern4CallExternalFunction = re.compile(r'([\w\.\[\]]+)\.(\w+\([^()]*\))')
	    #print(matchLine)
	    if result4IfCallFunction:
	        isIfCall = 1
	        typeStr = "bool "
	        if varType:
	            typeStr = varType + " "
	        
	        callStart = matchLine.find(result4IfCallFunction[0][1].strip())
	        callEnd = callStart + len(result4IfCallFunction[0][1].strip())
	        if matchLine[callStart-1] == ".":
	            result4CallExternalFunction = pattern4CallExternalFunction.findall(matchLine)
	            if result4CallExternalFunction:
	                callStart = matchLine.find(result4CallExternalFunction[0][0]+"."+result4CallExternalFunction[0][1])

	        subString1 = "substituteVariable" + "X" + callFunc + str(countCall)
	        subString2 = typeStr + subString1 + ";\n"
	        
	        modifiedIfLine = matchLine[0:callStart] + subString1 + matchLine[callEnd:] + "\n"
	        #print(subString2)
	        newMatchLine = subString1 + " = " + result4IfCallFunction[0][1].strip()
	        matchLine = newMatchLine
	        appendLineBeforeList = []
	        appendLineAfterList = []
	        appendLineBeforeList.append(subString2)
	        appendLineAfterList.append(modifiedIfLine)
	       #print(matchLine)

	    #function call in format like "A(b, c).call()"
	    result4MultiFunctionCall = pattern4MultiFunctionCall.findall(matchLine.strip())
	    if result4MultiFunctionCall:
	        isMultiCall = 1
	        suffixStr = result4MultiFunctionCall[0][1]
	        #print(matchLine)

	    result4Assign = pattern4Assign.findall(matchLine.strip())
	    if result4Assign:
	        #print(matchLine)
	        isAssign = 1
	        assignPrefix = result4Assign[0].split("=")[0]

	    result4Return = pattern4Return.findall(matchLine.strip())
	    if result4Return:
	        #print(matchLine)
	        isReturn = 1

	    #substitution   
	    #print("matchLine", matchLine)     
	     
	    if currArgvs:
	        if len(argvs) > len(currArgvs):
	            argvs = argvs[0:len(currArgvs)]
	        for idx, item in enumerate(argvs):
	            if item:
	                argvDict[item] = currArgvs[idx]
	        #print(argvDict)
	        pattern4ReturnBool = re.compile(r'return\s+\W*(true|false)\W')
	        pattern4ReturnLine = re.compile(r'(return)(\W+\s*.+\;)')
	        pattern4ReturnOneVal = re.compile(r'return\s+(.*)\;')
	        for index, line in enumerate(functionBlock[1:-1]):
	            #print(line)
	            result4ReturnBool = pattern4ReturnBool.findall(line.strip())
	            for pair in argvDict.items():
	                #print(pair)
	                pattern4Argv = re.compile(r'[^\.\w]' + pair[0] + '\W')
	                result4Argv = pattern4Argv.findall(line.strip())
	                if result4Argv and (pair[0] != pair[1]):
	                    for singleResult in result4Argv:
	                        l = functionBlock[index+1]
	                        subGoal = singleResult[0] + pair[1] + singleResult[-1]
	                        startIdx = l.find(singleResult)
	                        endIdx = startIdx + len(singleResult)
	                        functionBlock[index+1] = l[0:startIdx] +  subGoal + l[endIdx:]
	            #print(functionBlock[index+1])
	            result4ReturnLine = pattern4ReturnLine.findall(functionBlock[index+1].strip())
	            if result4ReturnLine:
	                if isAssign and not isMultiCall:
	                    #print(result4ReturnLine)
	                    functionBlock[index+1] = pattern4ReturnLine.sub( assignPrefix + '=' + result4ReturnLine[0][1], functionBlock[index+1])   
	                    #print(functionBlock[index+1])
	                elif isMultiCall:
	                    result4ReturnOneVal = pattern4ReturnOneVal.findall(line.strip())
	                    if result4ReturnOneVal:
	                        strStart = line.find(line.strip())
	                        functionBlock[index+1] = line[0:strStart] + result4ReturnOneVal[0].strip() + suffixStr + ";\n"
	                elif isReturn:
	                    pass
	                else:
	                    functionBlock[index+1] = ""
	                
	    else:
	        pass
	    
	    #while functionB has been call by functionA for multi-times
	    if countCall:
	        pattern4Variables = re.compile(r'(address|bool|string|int|int8|int16|int24|int32|int40|int48|int56|int64|int72|int80|int88|int96|int104|int112|int120|int128|int136|int144|int152|int160|int168|int176|int184|int192|int200|int208|int216|int224|int232|int240|int248|int256|uint|uint8|uint16|uint24|uint32|uint40|uint48|uint56|uint64|uint72|uint80|uint88|uint96|uint104|uint112|uint120|uint128|uint136|uint144|uint152|uint160|uint168|uint176|uint184|uint192|uint200|uint208|uint216|uint224|uint232|uint240|uint248|uint256|byte|bytes|bytes1|bytes2|bytes3|bytes4|bytes5|bytes6|bytes7|bytes8|bytes9|bytes10|bytes11|bytes12|bytes13|bytes14|bytes15|bytes16|bytes17|bytes18|bytes19|bytes20|bytes21|bytes22|bytes23|bytes24|bytes25|bytes26|bytes27|bytes28|bytes29|bytes30|bytes31|bytes32|fixed|(fixed[0-9]+x[0-9]+)|ufixed|(ufixed[0-9]+x[0-9]+))\s+(\w*)')
	        duplicatedVar = {}
	        for f in functionBlock[1:-1]:
	            result4Variables = pattern4Variables.findall(f.strip())
	            if result4Variables:
	                charIdx = 96 + countCall
	                duplicatedVar[result4Variables[0][-1]] = result4Variables[0][-1] + str(charIdx) + chr(charIdx)
	        for p in duplicatedVar.items():
	            pattern4Var = re.compile(r'[^\.\w]' + p[0] + '\W')
	            for index, line in enumerate(functionBlock[1:-1]):
	                result4Var = pattern4Var.findall(line.strip())
	                if result4Var and (p[0] != p[1]):
	                    for singleResult in result4Var:
	                        l = functionBlock[index+1]
	                        subGoal = singleResult[0] + p[1] + singleResult[-1]
	                        startIdx = l.find(singleResult)
	                        endIdx = startIdx + len(singleResult)
	                        functionBlock[index+1] = l[0:startIdx] +  subGoal + l[endIdx:]
	    
	    #print(functionBlock[1])
	    replacedBlock = functionBlock[1:-1]
	    if isIfCall:
	        replacedBlock = appendLineBeforeList + functionBlock[1:-1] + appendLineAfterList
	    #print(replacedBlock)
	    return replacedBlock

	def isIteratedFunc(self, contractFuntionStr, contractFunctionDict, deduplicatedFile):
	    pattern4Function = re.compile(r'\Afunction\W+([^\(]*)')
	    if contractFunctionDict.__contains__(contractFuntionStr):
	        searchBlock = Infos().getCurrBlock(deduplicatedFile, contractFunctionDict[contractFuntionStr]['idx'])
	        result4Function = pattern4Function.findall(searchBlock[0]['line'].strip())
	        currFunc = result4Function[0]
	        pattern4Iterate = re.compile(r'\W?' + currFunc + '\(')
	        for line in searchBlock[1:]:
	            result4Iterate = pattern4Iterate.findall(line['line'])
	            if result4Iterate:
	                return True
	    return False

	def functionReplace(self, contractDict, fileContent, modSearchOrder, modDict, contractFunctionDict, searchPath, contractElemLibDict, libFunctionDict):
	    pattern4Contract = re.compile(r'\Acontract\W+(\w*)')
	    pattern4Function = re.compile(r'\Afunction\W+([^\(]*)')
	    pattern4Library = re.compile(r'\Alibrary\s+(\w+)\s*\{')
	    pattern4Modifier = re.compile(r'\Amodifier\W+([^\(]*)')
	    pattern4Require = re.compile(r'\A(require|assert)\s*\(')
	    pattern4ElementaryTypeName = re.compile(r'(address|bool|string|int|int8|int16|int24|int32|int40|int48|int56|int64|int72|int80|int88|int96|int104|int112|int120|int128|int136|int144|int152|int160|int168|int176|int184|int192|int200|int208|int216|int224|int232|int240|int248|int256|uint|uint8|uint16|uint24|uint32|uint40|uint48|uint56|uint64|uint72|uint80|uint88|uint96|uint104|uint112|uint120|uint128|uint136|uint144|uint152|uint160|uint168|uint176|uint184|uint192|uint200|uint208|uint216|uint224|uint232|uint240|uint248|uint256|byte|bytes|bytes1|bytes2|bytes3|bytes4|bytes5|bytes6|bytes7|bytes8|bytes9|bytes10|bytes11|bytes12|bytes13|bytes14|bytes15|bytes16|bytes17|bytes18|bytes19|bytes20|bytes21|bytes22|bytes23|bytes24|bytes25|bytes26|bytes27|bytes28|bytes29|bytes30|bytes31|bytes32|fixed|(fixed[0-9]+x[0-9]+)|ufixed|(ufixed[0-9]+x[0-9]+))(\s+|\s*\()')
	    pattern4Instantiation1 = re.compile(r'\W\s*new\s+(\w*)\s*\(')
	    funcDict = {}
	    contract = ''
	    
	    saveContractList = []

	    for line in fileContent:
	        result4Contract = pattern4Contract.findall(line.strip())
	        result4Function = pattern4Function.findall(line.strip())
	        if result4Contract:
	            contract = result4Contract[0].strip()
	            funcDict.setdefault(contract, [])
	        if result4Function and contract:
	            func = result4Function[0].strip()
	            funcDict[contract].append(func)

	    #print(contractElemLibDict)

	    deduplicatedFile = self.variableDeduplication(fileContent, funcDict, contractDict, contractFunctionDict)
	    
	    dFileCopy = copy.deepcopy(deduplicatedFile)
	    contractVarDict = Infos().varTypeRecord(contractDict, deduplicatedFile)
	    #print(contractVarDict)

	    pattern4CallFunc = re.compile(r'(\w+\([^()]*\))')
	    pattern4Constructor = re.compile(r'constructor')
	    #pattern4CallExternalFunction = re.compile(r'([^\w\.\[\]]\w.+)\.(\w+\([^()]*\))')
	    pattern4CallExternalFunction = re.compile(r'([\w\.\[\]]+)\.(\w+\([^()]*\))')
	    callFunctionDict = {}
	    callModifierDict = {}
	    currContract = ''
	    currFunc = ''
	    calledFunctionList = []
	    delFunctionList = []
	    flag = 0
	    end = 0
	    while not end:
	        for idx, line in enumerate(dFileCopy[flag:]):
	            #print("o:", idx+flag)
	            #print(line)
	            varType = ""
	            result4Instantiation1 = pattern4Instantiation1.findall(line.strip())
	            result4CallFunc = pattern4CallFunc.findall(line.strip())
	            result4Constructor = pattern4Constructor.findall(line.strip())
	            result4Contract = pattern4Contract.findall(line.strip())
	            result4Library = pattern4Library.findall(line.strip())
	            result4Require = pattern4Require.findall(line.strip())
	            result4CurrFunction = pattern4Function.findall(line.strip())
	            result4CurrModifier = pattern4Modifier.findall(line.strip())
	            result4CallExternalFunction = pattern4CallExternalFunction.findall(line.strip())
	            result4ElementaryTypeName = pattern4ElementaryTypeName.findall(line.strip())
	            if result4Instantiation1 and result4Instantiation1[0] not in saveContractList:
	                saveContractList.append(result4Instantiation1[0])
	            if result4Contract:
	                currContract = result4Contract[0]
	            if result4Library:
	                currContract = ''
	            if result4CurrFunction and currContract:
	                currFunc = result4CurrFunction[0]
	                #print(currFunc)
	                callFunctionDict.setdefault(currContract + '|' + currFunc, [])
	                # generate modifier dict
	                if modSearchOrder.__contains__(currContract):
	                    for m in modSearchOrder[currContract]:
	                        mod = m.split('|')[1]
	                        patter4ModifierCall = re.compile(r'function\s(.*)\s' + mod + '\W')
	                        result4ModifierCall = patter4ModifierCall.findall(line.strip())
	                        if result4ModifierCall:
	                            #print(line)
	                            callModifierDict.setdefault(currContract + '|' + currFunc, [])
	                            if m not in callModifierDict[currContract + '|' + currFunc]:
	                                list = []
	                                for i in callModifierDict[currContract + '|' + currFunc]:
	                                    list.append(i.split('|')[1])
	                                if mod not in list:
	                                    callModifierDict[currContract + '|' + currFunc].append(m)
	            if result4Constructor:
	                currFunc = result4Constructor[0]

	            if result4CallExternalFunction and currContract and currFunc and not result4CurrFunction and not result4Contract:
	                caller = result4CallExternalFunction[0][0].strip()
	                if caller.count("[") > caller.count("]"):
	                    caller = caller.split("[")[-1]
	                callFunc = result4CallExternalFunction[0][1].split('(')[0]
	                NcontractList, contractDict, NlibDict, NlibFunctionDict, NmainContract, NmodDict, NnewContractFunctionDict, NcontractConstructorDict = Infos().findAllContracts(dFileCopy)
	                #contractVarDict = Infos().varTypeRecord(contractDict, dFileCopy)
	                if caller == 'super':
	                    for target in searchPath[currContract][1:]:
	                        searchStr = target + '|' + callFunc
	                        if contractFunctionDict.__contains__(searchStr):
	                            caller = target
	                            break
	                        else:
	                            pass
	                else:
	                    searchBlock = Infos().getCurrBlock(dFileCopy, contractDict[currContract]['idx'])
	                    for k in contractDict.keys():
	                        pattern4ContractRef = re.compile(r''+ k +'\s+(public\s+)?' + caller + '\s*\;')
	                        for s in searchBlock:
	                            result4ContractRef = pattern4ContractRef.findall(s['line'])
	                            if result4ContractRef:
	                                caller = k
	                                if k not in saveContractList:
	                                    saveContractList.append(k)

	                if contractDict.__contains__(caller):
	                    argvStr = result4CallExternalFunction[0][1].split('(')[1].replace(')', '')
	                    if argvStr:
	                        currArgvs = argvStr.split(',')
	                        for cArgvIdx, cArgv in enumerate(currArgvs):
	                            currArgvs[cArgvIdx] = cArgv.strip()
	                    else:
	                        currArgvs = []
	                    callFunctionDict.setdefault(currContract + '|' + currFunc, [])
	                    countCall = callFunctionDict[currContract + '|' + currFunc].count(callFunc)
	                    callFunctionDict[currContract + '|' + currFunc].append(callFunc)
	                    contractFuntionStr = caller + '|' + callFunc

	                    if contractFunctionDict.__contains__(contractFuntionStr):
	                        isIterated = False
	                        isIterated = self.isIteratedFunc(contractFuntionStr, contractFunctionDict, deduplicatedFile)
	                        if isIterated:
	                            continue
	                        	#print(line)
	                        contractVarList = [cvk for cvk in contractVarDict.keys()]
	                        for cVar in contractVarList:
	                        	if cVar.split("|")[0] == caller:
	                        		vName = cVar.split("|")[1]
	                        		if not contractVarDict.__contains__(currContract + "|" + vName):
	                        			vType = contractVarDict[cVar]["type"]
	                        			contractVarDict[currContract + "|" + vName] = {"var": vName, "type": vType}

	                        contractElemLibList = [celk for celk in contractElemLibDict.keys()]
	                        for cELib in contractElemLibList:
	                        	if cELib.split("|")[0] == caller:
	                        		ketStr = currContract + "|" + cELib.split("|")[1]
	                        		if not contractElemLibDict.__contains__(ketStr):
	                        			libFunc = contractElemLibDict[cELib]
	                        			contractElemLibDict[ketStr] = libFunc

	                        block = self.argvReplace(line, callFunc, contractFuntionStr, currArgvs, countCall, contractFunctionDict, deduplicatedFile, varType)
	                        if contractFuntionStr not in calledFunctionList:
	                            calledFunctionList.append(contractFuntionStr)
	                        # indent
	                        stringStart = len(line) - len(line.lstrip())
	                        lineStart = 0
	                        for bIdx, bLine in enumerate(block):
	                            if bLine and not lineStart:
	                                lineStart = len(bLine) - len(bLine.lstrip())
	                            block[bIdx] = line[0:stringStart] + bLine[lineStart-1:]
	                        dFileCopy = dFileCopy[0:flag + idx] + block + dFileCopy[flag + idx+1:]
	                        block = []
	                        flag = flag + idx
	                        break

	                    else:
	                        #interface call
	                        delFunc = {"dFunc": currContract + "|" + currFunc, "caller": caller}
	                        if delFunc not in delFunctionList:
	                            delFunctionList.append(delFunc)
	                else:
	                    nCaller = caller.split("[")[0]
	                    if contractVarDict.__contains__(currContract + "|" + nCaller):
	                        #library function replacement
	                        libFunctionStr = ""
	                        varType = contractVarDict[currContract + "|" + nCaller]["type"]
	                        if contractElemLibDict.__contains__(currContract + "|" + varType):
	                            for lFunc in contractElemLibDict[currContract + "|" + varType]:
	                                if lFunc.split("|")[1] == callFunc:
	                                    libFunctionStr = lFunc

	                        if libFunctionStr:
	                            argvStr = result4CallFunc[0].split('(')[1].replace(')','')
	                            currArgvs = []
	                            if argvStr:
	                                currArgvs = result4CallFunc[0].split('(')[1].replace(')','').split(',')
	                                for cArgvIdx, cArgv in enumerate(currArgvs):
	                                    currArgvs[cArgvIdx] = cArgv.strip()
	                            else:
	                                pass
	                            currArgvs.insert(0, caller.strip())
	                            callFunctionDict.setdefault(currContract + '|' + currFunc, [])
	                            countCall = callFunctionDict[currContract+ '|' + currFunc].count(callFunc)
	                            callFunctionDict[currContract+ '|' + currFunc].append(callFunc)
	                            
	                            if libFunctionDict.__contains__(libFunctionStr):
	                                block = self.argvReplace(line, callFunc, libFunctionStr, currArgvs, countCall, libFunctionDict, deduplicatedFile, varType)
	                                if libFunctionStr not in calledFunctionList:
	                                    calledFunctionList.append(libFunctionStr)
	                                # indent
	                                stringStart = len(line) - len(line.lstrip())
	                                lineStart = 0
	                                for bIdx, bLine in enumerate(block):
	                                    if bLine and not lineStart:
	                                        lineStart = len(bLine) - len(bLine.lstrip())
	                                    block[bIdx] = line[0:stringStart] + bLine[lineStart:]
	                                #print(block)
	                                dFileCopy = dFileCopy[0:flag + idx] + block + dFileCopy[flag + idx+1:]
	                                block = []
	                                flag = flag + idx
	                                break
	                    else:
	                        pass
	            

	            if result4CallFunc and not result4CallExternalFunction and not result4CurrFunction and not result4CurrModifier and currContract and currFunc and not result4ElementaryTypeName and not result4Contract:
	                #update index in contractFunctionDict
	                #print(currContract)
	                if result4CallFunc[0].split('(')[0] in funcDict[currContract]:
	                    callFunc = result4CallFunc[0].split('(')[0]
	                    argvStr = result4CallFunc[0].split('(')[1].replace(')','')
	                    if argvStr:
	                        currArgvs = result4CallFunc[0].split('(')[1].replace(')','').split(',')
	                        for cArgvIdx, cArgv in enumerate(currArgvs):
	                            currArgvs[cArgvIdx] = cArgv.strip()
	                    else:
	                        currArgvs = []
	                    callFunctionDict.setdefault(currContract + '|' + currFunc, [])
	                    countCall = callFunctionDict[currContract+ '|' + currFunc].count(callFunc)
	                    callFunctionDict[currContract+ '|' + currFunc].append(callFunc)
	                    contractFuntionStr = currContract+ '|' + callFunc
	                    isIterated = False
	                    isIterated = self.isIteratedFunc(contractFuntionStr, contractFunctionDict, deduplicatedFile)
	                    if contractFunctionDict.__contains__(contractFuntionStr) and not isIterated:
	                        #print(currArgvs)
	                        #print(contractFuntionStr)
	                        block = self.argvReplace(line, callFunc, contractFuntionStr, currArgvs, countCall, contractFunctionDict, deduplicatedFile, varType)
	                        if contractFuntionStr not in calledFunctionList:
	                            calledFunctionList.append(contractFuntionStr)
	                        # indent
	                        stringStart = len(line) - len(line.lstrip())
	                        lineStart = 0
	                        for bIdx, bLine in enumerate(block):
	                        	if bLine:
	                        		lineStart = len(bLine) - len(bLine.lstrip())
	                        	block[bIdx] = bLine
	                        	lineStart = 0
	                        dFileCopy = dFileCopy[0:flag + idx] + block + dFileCopy[flag + idx+1:]
	                        block = []
	                        flag = flag + idx
	                        break
	            block = []

	            if idx == len(dFileCopy) - flag - 1:
	                end = 1

	    contractList, contractDict, libDict, libFunctionDict, mainContract, modDict, newContractFunctionDict, contractConstructorDict = Infos().findAllContracts(dFileCopy)
	    #print(newContractFunctionDict)
	    # modifier call replacement
	    modBufferDict = {}
	    for pair in callModifierDict.items():
	        modBlock2 = []
	        
	        for modItem in pair[1]:
	            #modifiers without params
	            if not modDict[modItem]['modParams'] or not modDict[modItem]['modParams'][0]:
	                modBlock = Infos().getCurrBlock(dFileCopy, modDict[modItem]['idx'])
	                for mIdx, mBlk in enumerate(modBlock):
	                    modBlock[mIdx] = mBlk['line']
	                modBlock = modBlock[1:-1]
	            #modifiers with params
	            else:
	                funcLine = dFileCopy[newContractFunctionDict[pair[0]]['idx']]
	                #print(funcLine)
	                callMod = modItem.split('|')[1]
	                pattern4CallMod = re.compile(r'\s' + callMod + '\(([^()]*)\)')
	                result4CallMod = pattern4CallMod.findall(funcLine)
	                if result4CallMod:
	                    #print(result4CallMod)
	                    currArgvs = result4CallMod[0].split(',')
	                    for aIdx, a in enumerate(currArgvs):
	                        currArgvs[aIdx] = a.strip()
	                countCall = 0
	                modBlock = self.argvReplace(funcLine, callMod, modItem, currArgvs, countCall, modDict, dFileCopy, varType)
	            modBlock2.append({"content": modBlock})
	        modBufferDict[pair[0]] = {'content': modBlock2, 'idx': newContractFunctionDict[pair[0]]['idx']}
	    
	    contractList, contractDict, libDict, libFunctionDict, mainContract, modDict, newContractFunctionDict, contractConstructorDict = Infos().findAllContracts(dFileCopy)
	    sortedDict = sorted(modBufferDict.items(), key = lambda x:x[1]['idx'], reverse = True)
	    pattern4Sub = re.compile(r'\A\_\;')
	    for bPair in sortedDict:
	        funcIdx = newContractFunctionDict[bPair[0]]['idx']
	        for insertBlock in bPair[1]['content']:
	        	insertB = insertBlock['content']
		        funcBlock = Infos().getCurrBlock(dFileCopy, funcIdx)
		        insertFuncBlock = [f['line'] for f in funcBlock[1:-1]]
		        for insertIdx, insertL in enumerate(insertB):
		        	result4Sub = pattern4Sub.findall(insertL.strip())
		        	if result4Sub:
		        		insertB = insertB[0:insertIdx] + insertFuncBlock + insertB[insertIdx + 1:]
		        		break
		        dFileCopy = dFileCopy[0:funcIdx+1] + insertB + dFileCopy[funcBlock[-1]['idx']:]

	    #discard replaced modifier & function
	    contractList, contractDict, libDict, libFunctionDict, mainContract, modDict, newContractFunctionDict, contractConstructorDict = Infos().findAllContracts(dFileCopy)
	    pattern4PublicFunc = re.compile(r'\Wpublic\W')
	    discardList = []
	    for dFunc in delFunctionList:
	        print("Delete " + dFunc["dFunc"].split("|")[1] + " in contract " + dFunc["dFunc"].split("|")[0] + " due to calling of interface " + dFunc["caller"] + ".")
	        if dFunc["dFunc"] not in calledFunctionList:
	            calledFunctionList.append(dFunc["dFunc"])
	    for cFunc in calledFunctionList:
	        
	        if cFunc.split("|")[0] in saveContractList:
	            continue
	        dfuncIdx = ""
	        if newContractFunctionDict.__contains__(cFunc):
	            dfuncIdx = newContractFunctionDict[cFunc]['idx']
	        elif libFunctionDict.__contains__(cFunc):
	            dfuncIdx = libFunctionDict[cFunc]['idx']
	        if dfuncIdx: 
	            descardBlock = Infos().getCurrBlock(dFileCopy, dfuncIdx)
	            result4PublicFunc = pattern4PublicFunc.findall(descardBlock[0]['line'])
	            if not result4PublicFunc:
	                discardList.extend(descardBlock)
	    for cMod in modDict.items():
	        descardBlock = Infos().getCurrBlock(dFileCopy, cMod[1]['idx'])
	        discardList.extend(descardBlock)
	    removeList2 = []
	    for fileIdx, fileLine in enumerate(dFileCopy):
	        fileItem = {'line': fileLine, 'idx': fileIdx}
	        if fileItem in discardList:
	            removeList2.append(fileIdx)
	    for r in reversed(removeList2):
	        del dFileCopy[r]
	    
	    return dFileCopy
	    #return deduplicatedFile

