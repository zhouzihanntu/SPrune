import re
import operator
from collections import deque

from utils.infos import Infos

class Slicing:
	# find lines that contain keyword in main contract
	def findBasicKeywords(self, fileContent, mainContract, contractDict, customTag):
	    keywords = deque()
	    reservedList = []
	    ignoreList = ['msg.sender', 'msg.value', 'this', 'uint256', 'new', 'sub', 'add', 'mul', 'div']

	    pattern4Lines = re.compile(r'\.(transfer|send|call)\(|(\W*(balance|balanceof|balanceOf|balances|balancesof|balancesOf)\[.*\]\s?\=[^\=])', flags=re.I)
	    pattern4Keyword = re.compile(r'.*\s([^\(]*\.(transfer|send|call))\((.*)\)')
	    pattern4Balance = re.compile(r'\Wbalance\[(.*)\]\s?\=[^\=]|\Wbalanceof\[(.*)\]\s?\=[^\=]|\Wbalances\[(.*)\]\s?\=[^\=]|\Wbalancesof\[(.*)\]\s?\=[^\=]', flags=re.I)

	    if customTag:
	        customStr4Lines = ''
	        customStr4Balance = ''
	        for c in customTag:
	            customStr4Lines = customStr4Lines + '|' + c
	            customStr4Balance = customStr4Balance + '|\W?' + c + '\[(.*)\]\s?\=[^\=]'
	        pattern4Lines = re.compile(r'\.(transfer|send|call)\(|(\W*(balance|balanceof|balanceOf|balances|balancesof|balancesOf' + customStr4Lines + ')\[.*\]\s?\=[^\=])', flags=re.I)
	        pattern4Balance = re.compile(r'\Wbalance\[(.*)\]\s?\=[^\=]|\Wbalanceof\[(.*)\]\s?\=[^\=]|\Wbalances\[(.*)\]\s?\=[^\=]|\Wbalancesof\[(.*)\]\s?\=[^\=]' + customStr4Balance , flags=re.I)
	    for contractPair in contractDict.items():
	        content = Infos().getCurrBlock(fileContent, contractPair[1]['idx'])
	        for line in content:
	            result = pattern4Lines.findall(line['line'])
	            key = pattern4Keyword.findall(line['line'])
	            balanceKey = pattern4Balance.findall(line['line'])
	            if result and key:
	                reservedList.append(line)
	                a = {'key': key[0][0], 'idx': line['idx'], 'contract': contractPair[0], 'contractIdx': contractPair[1]['idx'], 'searched': []}
	                if a not in keywords:
	                    if a['key'] not in ignoreList: keywords.append(a)
	                c = key[0][2].split(', ')
	                for item in c:
	                    i = {'key': item, 'idx': line['idx'], 'contract': contractPair[0], 'contractIdx': contractPair[1]['idx'], 'searched': []}
	                    if i not in keywords:
	                        if item not in ignoreList: keywords.append(i)
	            if balanceKey:
	                reservedList.append(line)
	                a = {'key': balanceKey[0][2], 'idx': line['idx'], 'contract': contractPair[0], 'contractIdx': contractPair[1]['idx'], 'searched': []}
	                if a not in keywords:
	                    #print(a)
	                    if a['key'] not in ignoreList: keywords.append(a)

	    for item in contractDict.keys():
	        for index, line in enumerate(fileContent):
	            if "new " + item in line:
	                addLine = {'line': line, 'idx': index}
	                if addLine not in reservedList:
	                    reservedList.append(addLine)

	    return keywords, reservedList

	def findCurrFunction(self, fileContent, idx):
	    pattern4Function = re.compile(r'\s*(function|modifier|contract|constructor)\(*\W')
	    pattern4SingleLine = re.compile(r'\W\sfunction\W.*\;')
	    pattern4MultiLine = re.compile(r'\W\sfunction\s')

	    block = []

	    currLine = {'line': fileContent[idx], 'idx': idx}
	    result4SingleLine = pattern4SingleLine.findall(currLine['line'])
	    result4MultiLine = pattern4MultiLine.findall(currLine['line'])
	    if result4SingleLine:
	        block.append(currLine)
	        return block
	    elif result4MultiLine and not result4SingleLine:
	        pattern4LeftParenthesis = re.compile(r'(\{)')
	        result4LeftParenthesis = pattern4LeftParenthesis.findall(fileContent[idx])
	        while not result4LeftParenthesis:
	            block.append({'line': fileContent[idx], 'idx': idx})
	            idx += 1
	            result4LeftParenthesis = pattern4LeftParenthesis.findall(fileContent[idx])
	        block2 = Infos().getCurrBlock(fileContent, idx)
	        for line in block2:
	            block.append(line)
	        return block

	    block = Infos().getCurrBlock(fileContent, idx)

	    result4Function = pattern4Function.findall(block[0]['line'])
	    while not result4Function:
	        block = Infos().getCurrBlock(fileContent, idx)
	        result4Function = pattern4Function.findall(block[0]['line'])
	        idx = block[0]['idx'] - 1

	    return block

	# save current whole function if reserved function contains "transfer, send, call" statements
	def findExactFunction(self, fileContent, reservedList):
	    pattern4Contract = re.compile(r'\W*contract\s')
	    pattern4Keyword = re.compile(r'.*\s(.*\.(transfer|send|call))\((.*)\)')
	    saveWholeFunc = 0
	    isContract = 0
	    saveList = []

	    for item in reservedList:
	        function = self.findCurrFunction(fileContent, item['idx'])
	        # if the function returns is a contract, do not exec the following "transfer, send, call" saving methods
	        result4Contract = pattern4Contract.findall(function[0]['line'])
	        if result4Contract:
	            isContract = 1
	        # save lines that contain "transfer, send, call"
	        for line in function:
	            result4Keyword = pattern4Keyword.findall(line['line'])
	            if result4Keyword:
	                saveWholeFunc = 1
	        if saveWholeFunc and not isContract:
	            for i in function:
	                if i not in reservedList and i not in saveList:
	                    saveList.append(i)
	        # save begin & end
	        if function[0] not in reservedList and function[0] not in saveList:
	            saveList.append(function[0])
	        if function[-1] not in reservedList and function[-1] not in saveList:
	            saveList.append(function[-1])
	        saveWholeFunc = 0
	        isContract = 0

	    for s in saveList:
	        reservedList.append(s)

	    return reservedList

	# locate the contracts that contains reserved functions(add the first and last line of contract to reservedList)
	def locateFunction(self, fileContent, reservedList, contractList):
	    contractSection = []
	    for contract in contractList:
	        currContract = Infos().getCurrBlock(fileContent, contract['idx'])
	        section = {'contract': contract['contract'], 'start': contract['idx'], 'end': currContract[-1]['idx']}
	        contractSection.append(section)

	    contractSaved = []
	    for contract in contractSection:
	        for line in reservedList:
	            if line['idx'] >= contract['start'] and line['idx'] <= contract['end']:
	                if contract not in contractSaved:
	                    contractSaved.append(contract)

	    for contract in contractSaved:
	        start = {'line': fileContent[contract['start']], 'idx': contract['start']}
	        end = {'line': fileContent[contract['end']], 'idx': contract['end']}
	        if start not in reservedList:
	            reservedList.append(start)
	        if end not in reservedList:
	            reservedList.append(end)

	    return reservedList

	#save contract global variables
	def saveGlobalVar(self, fileContent, reservedList, contractFunctionDict, contractDict):
	    pattern4Contract = re.compile(r'\Acontract\s(\w*)')
	    rContractList = []
	    for rLine in reservedList:
	        result4Contract = pattern4Contract.findall(rLine['line'].strip())
	        if result4Contract:
	            rContractList.append(result4Contract[0])
	    for contract in rContractList:
	        bufferList = []
	        contractBlock = Infos().getCurrBlock(fileContent, contractDict[contract]['idx'])

	        for function in contractFunctionDict.keys():
	            funcContract = function.split('|')[0]
	            if funcContract == contract:
	                funcBlock = Infos().getCurrBlock(fileContent, contractFunctionDict[function]['idx'])
	                bufferList.extend(funcBlock)
	        for line in contractBlock:
	            if line not in bufferList and line not in reservedList:
	                reservedList.append(line)

	    return reservedList
	 
	def saveInstantiated(self, fileContent, reservedList, saveList, contractList, contractDict, mainContract):
	    #print(contractDict)
	    for s in saveList:
	        #print(s)
	        if s != mainContract['contract']:
	            block = Infos().getCurrBlock(fileContent, contractDict[s]['idx'])
	            for b in block:
	                if b not in reservedList:
	                    reservedList.append(b)
	    return reservedList
	
	# find the lines that contain keywords in specify block and mark them, then search operators and functions throughout inherited contracts
	def findALLKeywords(self, fileContent, contractList, contractGraph, keywords, reservedList):
	    ignoreList = ['msg.sender', 'msg.value', 'this', 'uint256', 'new', 'sub', 'add', 'mul', 'div', 'require', 'returns',
	                  'assert']
	    asteriskList = []
	    exCalledFunc = []

	    while keywords:
	        key = keywords.popleft()
	        pattern4Assign1 = re.compile(r'\W' + key['key'] + '\W.*\s*\=\s*')
	        pattern4Assign2 = re.compile(r'\W' + key['key'] + '\W.*\s*\=\s*(.*)\((.*)\)')
	        searchField = getCurrBlock(fileContent, key['contractIdx'])
	        isFound = 0
	        # looking for assignment statement
	        matchedList = []
	        matchedline = {}
	        splitList = key['key'].split('.')
	        if len(splitList) == 2:
	            for item in searchField:
	                pattern4NewObj = re.compile(r'\W' + splitList[0] + '\W.*\=\snew\s(.*)\((.*)\)')
	                pattern4Enum = re.compile(r'\Wenum\s' + splitList[0] + '\W.*\{')
	                pattern4Instance = re.compile(r'\W(private|public)\s' + splitList[0] + '\W*.*\;')
	                pattern4Statement = re.compile(r'\W' + splitList[0] + '\W.*\=\s')
	                result4NewObj = pattern4NewObj.findall(item['line'])
	                result4Enum = pattern4Enum.findall(item['line'])
	                result4Instance = pattern4Instance.findall(item['line'])
	                result4Statement = pattern4Statement.findall(item['line'])
	                if result4NewObj:
	                    if key['idx'] not in asteriskList:
	                        asteriskList.append(key['idx'])
	                    argvs = result4NewObj[0][1].replace(' ', '').split(',')
	                    for a in argvs:
	                        k = key.copy()
	                        k['key'] = a
	                        k['idx'] = item['idx']
	                        keywords.append(k)
	                    key['key'] = splitList[1]
	                    key['contract'] = result4NewObj[0][0]
	                    for contract in contractList:
	                        if contract['contract'] == key['contract']:
	                            key['contractIdx'] = contract['idx']
	                    keywords.append(key)
	                    matchedline = item
	                    isFound = 1
	                elif result4Enum and not isFound:
	                    if splitList[1] in item['line']:
	                        matchedline = item
	                        isFound = 1
	                elif result4Instance and not isFound:
	                    #print(result4Instance, item)
	                    matchedline = item
	                    #print(matchedline)
	                    isFound = 1
	                elif result4Statement and not isFound:
	                    key['key'] = splitList[0]
	                    if key not in keywords:
	                        keywords.append(key)
	                    isFound = 1
	        elif not isFound:
	            # variables assignment
	            for item in searchField:
	                result4Assign1 = pattern4Assign1.findall(item['line'])
	                if result4Assign1:
	                    matchedList.append(item)
	                    #print(result4Assign1)
	            if len(matchedList) > 1:
	                block = findCurrFunction(fileContent, key['idx'])
	                for i in matchedList:
	                    if i in block:
	                        matchedline = i
	            elif len(matchedList) == 1:
	                matchedline = matchedList[0]
	            if matchedList:
	                isFound = 1
	            #print(matchedline, 's')

	        if matchedline and matchedline not in reservedList:
	            #print(matchedline)
	            reservedList.append(matchedline)
	            result4Assign2 = pattern4Assign2.findall(matchedline['line'])
	            if result4Assign2:
	                argvList = result4Assign2[0][1].split(',')
	                argvList.append(result4Assign2[0][0])
	                for argv in argvList:
	                    argv = argv.replace(' ', '')
	                    if argv not in ignoreList:
	                        a = {'key': argv, 'idx': matchedline['idx'],
	                             'contract': key['contract'], 'contractIdx': key['contractIdx'], 'searched': []}
	                        if a not in keywords:
	                            keywords.append(a)

	        # looking for function statement
	        if not isFound:
	            pattern4Assign3 = re.compile(r'function\s' + key['key'] + '\W')
	            for item in searchField:
	                result4Assign3 = pattern4Assign3.findall(item['line'])
	                if result4Assign3:
	                    isFound = 1
	                    if key['searched']:
	                        calledFunc = {'function': key['key'], 'contract': key['contract'], 'origin': key['searched'][0], 'idx': item['idx']}
	                        if calledFunc not in exCalledFunc:
	                            exCalledFunc.append(calledFunc)
	                    function = findCurrFunction(fileContent, item['idx'])
	                    pattern4Referent = re.compile(r'\s(\w*)\(')
	                    pattern4Exception = re.compile(r'\W(\w+\.\w+)\W')
	                    for func in function:
	                        # find referent function
	                        result4Referent = pattern4Referent.findall(func['line'])
	                        result4Exception = pattern4Exception.findall(func['line'])
	                        if result4Exception:
	                            for resultItem in result4Exception:
	                                if resultItem not in ignoreList:
	                                    appendFunc = {'key': resultItem, 'idx': func['idx'], 'contract': key['contract'],
	                                                  'contractIdx': key['contractIdx'], 'searched': []}
	                                    keywords.append(appendFunc)
	                        if result4Referent:
	                            for resultItem in result4Referent:
	                                pattern4Comment = re.compile(r'//.*' + resultItem)
	                                result4Comment = pattern4Comment.findall(func['line'])
	                                if resultItem and resultItem != key['key'] and resultItem not in ignoreList and not result4Comment:
	                                    appendFunc = {'key': resultItem, 'idx': func['idx'], 'contract': key['contract'],
	                                                  'contractIdx': key['contractIdx'], 'searched': []}
	                                    keywords.append(appendFunc)
	                        if func not in reservedList:
	                            reservedList.append(func)

	        # search keyword definition in other contracts
	        if not isFound:
	            if key['contract'] not in key['searched']:
	                key['searched'].append(key['contract'])
	            if len(key['searched']) >= len(contractList):
	                break
	            for item in key['searched']:
	                for inherit in contractGraph[item]:
	                    if inherit in key['searched']:
	                        continue
	                    key['contract'] = inherit
	                    for searchIdx in contractList:
	                        if searchIdx['contract'] == inherit:
	                            key['contractIdx'] = searchIdx['idx']
	                            keywords.append(key)
	                            #print(key)
	                    break
	    return reservedList, asteriskList, exCalledFunc

	def reserve(self, fileContent, mainContract, contractDict, contractList, contractFunctionDict, customTag, saveList):
		keywords, reservedList = self.findBasicKeywords(fileContent, mainContract, contractDict, customTag)

		for line in reservedList:
			funcBlock = self.findCurrFunction(fileContent, line['idx'])
			for func in funcBlock:
				if func not in reservedList:
					reservedList.append(func)

		reservedList = self.findExactFunction(fileContent, reservedList)

		# find relevant contracts
		reservedList = self.locateFunction(fileContent, reservedList, contractList)
	    # save contract global variables
	    
		reservedList = self.saveGlobalVar(fileContent, reservedList, contractFunctionDict, contractDict)
	    #save instantiated contract
		reservedList = self.saveInstantiated(fileContent, reservedList, saveList, contractList, contractDict, mainContract)

		reservedList = sorted(reservedList, key=operator.itemgetter('idx'))

		return reservedList
