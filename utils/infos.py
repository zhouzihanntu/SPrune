import re
#import os
from collections import deque


class Infos:
	# get the whole function/contract of lines which contain keywords
	def getCurrBlock(self, fileContent, idx):
	    currBlock = []
	    parenthesisQueue = deque()
	    pattern4Parenthesis = re.compile(r'(\{|\})')
	    pattern4LeftParenthesis = re.compile(r'(\{)')
	    pattern4RightParenthesis = re.compile(r'(\})')
	    n = idx

	    while not parenthesisQueue:
	        if idx >= len(fileContent):
	            break
	        result4Parenthesis = pattern4LeftParenthesis.findall(fileContent[idx])
	        if result4Parenthesis:
	            for i in result4Parenthesis:
	                parenthesisQueue.append(i)
	        result4Parenthesis = pattern4RightParenthesis.findall(fileContent[idx])
	        if not parenthesisQueue and result4Parenthesis:
	            currBlock.append({'line': fileContent[n], 'idx': n})
	            return currBlock
	        idx -= 1
	    currBlock.append({'line': fileContent[idx + 1], 'idx': idx + 1})
	    idx += 2

	    while parenthesisQueue:
	        if idx >= len(fileContent):
	            break
	        currBlock.append({'line': fileContent[idx], 'idx': idx})
	        result4Parenthesis = pattern4Parenthesis.findall(fileContent[idx])
	        
	        if result4Parenthesis:
	            for i in result4Parenthesis:
	                if not parenthesisQueue and i == '{':
	                    parenthesisQueue.append(i)
	                    continue
	                last = parenthesisQueue.pop()
	                if last == '{' and i == '}':
	                    continue
	                elif last == '{' and i == '{':
	                    parenthesisQueue.append(last)
	                    parenthesisQueue.append(i)
	        idx += 1

	    return currBlock

	def findAllContracts(self, fileContent):
	    contractList = []
	    pattern = re.compile(r'\Acontract (.*) is (.*)\{')
	    pattern2 = re.compile(r'\A(contract|interface)\s+(.*)\{') #take contract and interface as the same
	    pattern4Contract = re.compile(r'\Acontract\s+(\w+)')
	    pattern4Library = re.compile(r'\Alibrary\s+(\w+)\s*\{')
	    pattern4Function = re.compile(r'\Afunction\W([^\(]*)')
	    pattern4Modifier = re.compile(r'\Amodifier\s(\w+)')
	    pattern4ModifierParams = re.compile(r'\Amodifier\s\w+\s?\(([^)]*)\)')
	    pattern4Constructor = re.compile(r'\Aconstructor\s*\(.*\{')
	    currContract = ''
	    modName = ''
	    modParams = []
	    modDict = {}
	    libDict = {}
	    libFunctionDict = {}
	    contractFunctionDict = {}
	    contractConstructorDict = {}
	    mainContract = ''
	    for idx, line in enumerate(fileContent):
	        result = pattern.findall(line.strip())
	        result2 = pattern2.findall(line.strip())
	        if result:
	            contract = result[0][0].strip()
	            inherit = result[0][1].split(',')
	            for i, e in enumerate(inherit):
	                inherit[i] = e.strip()
	            item = {'contract': contract, 'inherit': inherit, 'idx': idx}
	            contractList.append(item)
	        elif result2:
	            contract = result2[0][1].strip()
	            inherit = ''
	            item = {'contract': contract, 'inherit': inherit, 'idx': idx}
	            contractList.append(item)
	        
	        result4Library = pattern4Library.findall(line.strip())
	        result4Contract = pattern4Contract.findall(line.strip())
	        result4Function = pattern4Function.findall(line.strip())
	        #generate library dict
	        if result4Library:
	            #print(result4Library)
	            libName = result4Library[0]
	            libDict[libName] = {'library': libName, 'idx': idx}
	        elif result4Contract:
	            libName = ""

	        #generate modifier list and contract-function dict & contract-constructor dict
	        if result4Contract:
	        	currContract = result4Contract[0]
	        elif result4Library:
	            currContract = ''
	        result4Modifier = pattern4Modifier.findall(line.strip())
	        result4Constructor = pattern4Constructor.findall(line.strip())
	        if result4Modifier and currContract:
	            modName = currContract + '|' + result4Modifier[0]
	            result4ModifierParams = pattern4ModifierParams.findall(line.strip())
	            if result4ModifierParams:
	                modParams = result4ModifierParams[0].split(',')
	                for i, p in enumerate(modParams):
	                    modParams[i] = p.strip().split(' ')[-1]
	            modDict[modName] = {'modParams': modParams, 'idx': idx}
	            modName, modParams = '', []
	        #print(line)
	        if result4Function and currContract:
	            #print(result4Function)
	            funcName = currContract + '|' + result4Function[0].strip()
	            contractFunctionDict[funcName] = {'idx': idx}
	        elif result4Function and libName:
	            funcName = libName + '|' + result4Function[0]
	            libFunctionDict[funcName] = {'idx': idx}
	        if result4Constructor and currContract:
	            constructorBlock = self.getCurrBlock(fileContent, idx)
	            contractConstructorDict[contract] = {"context": constructorBlock, "idx": idx}

	    # find main contract
	    deleteList = []
	    # find out extended contracts
	    for item in contractList:
	        for i in contractList:
	            if item['contract'] in i['inherit']:
	                if item not in deleteList:
	                    deleteList.append(item)
	    # find out instatiated contract
	    for item in contractList:
	        pattern4Instance = re.compile(r'new\s+' + item['contract'] + '\W')
	        for line in fileContent:
	            result4Instance = pattern4Instance.findall(line)
	            if result4Instance and (item not in deleteList):
	                    deleteList.append(item)

	    for contract in contractList:
	        if contract not in deleteList:
	            #print(contract)
	            contractBlock = self.getCurrBlock(fileContent, contract['idx'])
	            result4Contract = pattern4Contract.findall(contractBlock[0]['line'].strip())
	            if result4Contract:
	                mainContract = contract
	    #print("*****")
	    #print(contractList)
	    #print(deleteList)
	    contractDict = {}
	    for contract in contractList:
	        contractDict[contract['contract']] = {'inherit': contract['inherit'], 'idx': contract['idx']}
	    if not mainContract:
	        print("Cannot find main contract.")
	        #os.system("pause")
	        mainContract = "NULLNULLNULL"
	    
	    return contractList, contractDict, libDict, libFunctionDict, mainContract, modDict, contractFunctionDict, contractConstructorDict

	#generate contract inherit chain
	def inheritChain(self, contractList, contractGraph):
	    #print(contractGraph)
	    searchPath = {}
	    visitedContract = []
	    stack = []
	    for c in contractList:
	        stack.append(c['contract'])
	        while stack:
	            p = stack.pop()
	            if p not in visitedContract:
	                visitedContract.append(p)
	            if contractGraph.__contains__(p) and contractGraph[p]:
	                for i in contractGraph[p]:
	                    if i not in visitedContract:
	                        stack.append(i)
	        searchPath[c['contract']] = visitedContract
	        visitedContract = []
	    return searchPath

	#modifier & function substitution
	def subChain(self, modDict, contractFunctionDict, searchPath):
	    modSearchOrder = {}
	    functionSearchOrder = {}
	    for pair in searchPath.items():
	        modOrder = []
	        funcOrder = []
	        for C in pair[1]:
	            for mod in modDict.keys():
	                modC = mod.split('|')[0]
	                if modC == C:
	                    modOrder.append(mod)
	            for func in contractFunctionDict.keys():
	                funcC = func.split('|')[0]
	                if funcC == C:
	                    funcOrder.append(func)
	        modSearchOrder[pair[0]] = modOrder
	        functionSearchOrder[pair[0]] = funcOrder

	    return modSearchOrder, functionSearchOrder

	def varStatement(self, contractList, contractDict, modDict, contractFunctionDict, contractConstructorDict, fileContent):
	    statementDict = {}
	    contractGlobalVar = {}
	    pattern4Variables = re.compile(
	        r'(\W|\A)(address|bool|string|int|int8|int16|int24|int32|int40|int48|int56|int64|int72|int80|int88|int96|int104|int112|int120|int128|int136|int144|int152|int160|int168|int176|int184|int192|int200|int208|int216|int224|int232|int240|int248|int256|uint|uint8|uint16|uint24|uint32|uint40|uint48|uint56|uint64|uint72|uint80|uint88|uint96|uint104|uint112|uint120|uint128|uint136|uint144|uint152|uint160|uint168|uint176|uint184|uint192|uint200|uint208|uint216|uint224|uint232|uint240|uint248|uint256|byte|bytes|bytes1|bytes2|bytes3|bytes4|bytes5|bytes6|bytes7|bytes8|bytes9|bytes10|bytes11|bytes12|bytes13|bytes14|bytes15|bytes16|bytes17|bytes18|bytes19|bytes20|bytes21|bytes22|bytes23|bytes24|bytes25|bytes26|bytes27|bytes28|bytes29|bytes30|bytes31|bytes32|fixed|(fixed[0-9]+x[0-9]+)|ufixed|(ufixed[0-9]+x[0-9]+))\s+(public\s+|private\s+|internal\s+)?(constant\s+)?(\w+)')
	    pattern4MapVar = re.compile(r'(\W|\A)mapping\s*\(.*(public|private|internal)?\s+(\w+)')
	    for contract in contractList:
	        contractBlock = self.getCurrBlock(fileContent, contractDict[contract['contract']]['idx'])
	        for contractFunc in contractFunctionDict.keys():
	            if contractFunc.split('|')[0] == contract['contract']:
	                funcBlock = self.getCurrBlock(fileContent, contractFunctionDict[contractFunc]['idx'])
	                for f in funcBlock:
	                    if f in contractBlock:
	                        contractBlock.remove(f)
	        for contractMod in modDict.keys():
	            if contractMod.split('|')[0] == contract['contract']:
	                modBlock = self.getCurrBlock(fileContent, modDict[contractMod]['idx'])
	                for m in modBlock:
	                    if m in contractBlock:
	                        contractBlock.remove(m)
	        for contractCons in contractConstructorDict.keys():
	            if contractCons == contract['contract']:
	                consBlock = contractConstructorDict[contractCons]['context']
	                for c in consBlock:
	                    if c in contractBlock:
	                        contractBlock.remove(c)
	        statementDict[contract['contract']] = contractBlock[1:-1]
	        
	        gVarList = []
	        for statementLine in contractBlock[1:-1]:
	        	result4Variables = pattern4Variables.findall(statementLine['line'].strip())
	        	result4MapVar = pattern4MapVar.findall(statementLine['line'].strip())
	        	if result4Variables and not result4Variables[0][-2] and result4Variables[0][-1] not in gVarList:
	        		gVarList.append(result4Variables[0][-1])
	        	elif result4MapVar:
	        		gVarList.append(result4MapVar[0][-1])
	        contractGlobalVar[contract['contract']] = gVarList
	    return statementDict, contractGlobalVar

	def libBindingDict(self, fileContent, libDict, libFunctionDict, contractDict):
	    contractElemLibDict = {}
	    pattern4Using = re.compile(r'using\s+(\w+)\s+for\s+([^\s\;]+)')
	    for contract in contractDict.keys():
	        contractBlock = self.getCurrBlock(fileContent, contractDict[contract]['idx'])
	        for cLine in contractBlock:
	            result4Using = pattern4Using.findall(cLine['line'])
	            if result4Using:
	                keyStr = contract + "|" + result4Using[0][1]
	                libFunc = []
	                for lf in libFunctionDict.keys():
	                    if lf.split("|")[0] == result4Using[0][0]:
	                        libFunc.append(lf)
	                contractElemLibDict[keyStr] = libFunc
	    return contractElemLibDict

	def varTypeRecord(self, contractDict, fileContent):
	    contractVarDict = {}
	    pattern4Variables = re.compile(
	        r'(\W|\A)(address|bool|string|int|int8|int16|int24|int32|int40|int48|int56|int64|int72|int80|int88|int96|int104|int112|int120|int128|int136|int144|int152|int160|int168|int176|int184|int192|int200|int208|int216|int224|int232|int240|int248|int256|uint|uint8|uint16|uint24|uint32|uint40|uint48|uint56|uint64|uint72|uint80|uint88|uint96|uint104|uint112|uint120|uint128|uint136|uint144|uint152|uint160|uint168|uint176|uint184|uint192|uint200|uint208|uint216|uint224|uint232|uint240|uint248|uint256|byte|bytes|bytes1|bytes2|bytes3|bytes4|bytes5|bytes6|bytes7|bytes8|bytes9|bytes10|bytes11|bytes12|bytes13|bytes14|bytes15|bytes16|bytes17|bytes18|bytes19|bytes20|bytes21|bytes22|bytes23|bytes24|bytes25|bytes26|bytes27|bytes28|bytes29|bytes30|bytes31|bytes32|fixed|(fixed[0-9]+x[0-9]+)|ufixed|(ufixed[0-9]+x[0-9]+))\s+(public\s+|private\s+|internal\s+)?(constant\s+)?(\w+)')
	    pattern4VarAssign = re.compile(r'\Avar\s+(\w+)\s*\=\s*(\w+)\W')
	    pattern4Function = re.compile(r'\A(function|modifier)\W([^\(]*)')
	    pattern4MapVar = re.compile(r'(\W|\A)(mapping\s*\(\w+\s*\=\>\s*((\w+)|mapping\s*\(\w+\s*\=\>\s*(\w+)\))\))\s+(public\s+|private\s+|internal\s+)?(\w+)')
	    for contract in contractDict.keys():
	        contractBlock = Infos().getCurrBlock(fileContent, contractDict[contract]['idx'])
	        for cLine in contractBlock:
	            vName = ""
	            vType = ""
	            result4Variables = pattern4Variables.findall(cLine['line'].strip())
	            result4VarAssign = pattern4VarAssign.findall(cLine['line'].strip())
	            result4Function = pattern4Function.findall(cLine['line'].strip())
	            result4MapVar = pattern4MapVar.findall(cLine['line'].strip())
	            if result4Variables and not result4Function:
	                vName = result4Variables[0][-1]
	                vType = result4Variables[0][1]
	            elif result4MapVar and not result4Function:
	                if result4MapVar[0][3]:
	                    vType = result4MapVar[0][3]
	                elif result4MapVar[0][4]:
	                    vType = result4MapVar[0][4]
	                vName = result4MapVar[0][-1]
	            if vName and vType:
	                if contractVarDict.__contains__(contract + "|" + vName):
	                    pass
	                else:
	                    contractVarDict[contract + "|" + vName] = {"var": vName, "type": vType}
	            if result4VarAssign:
	            	vName = result4VarAssign[0][0]
	            	if contractVarDict.__contains__(contract + "|" + result4VarAssign[0][1]):
	            		vType = contractVarDict[contract + "|" + result4VarAssign[0][1]]["type"]
	            		contractVarDict[contract + "|" + vName] = {"var": vName, "type": vType}
	    return contractVarDict
