import os
import sys
import copy
import re
from collections import deque
import operator

from utils.modify import Modify
from utils.infos import Infos
from utils.varCheck import VarCheck
from utils.replace import Replace
from utils.slicing import Slicing

class Merge:

	def mergeReduce(self, filename, fileContent, argvs):
	    if argvs:
	        customTag = argvs.split(',')
	    else:
	        customTag = []
	    modifyF = Modify()
	    
	    fileContent = modifyF.deleteEmit(fileContent)
	    fileContent = modifyF.deleteMulDiv(fileContent)
	    
	    # STEP 1 Merge
	    getInfo = Infos()
	    contractList, contractDict, libDict, libFunctionDict, mainContract, modDict, contractFunctionDict, contractConstructorDict = getInfo.findAllContracts(fileContent)
	    #print(mainContract)
	    isAbnormal = False
	    if mainContract == "NULLNULLNULL":
	    	isAbnormal = True
	    if isAbnormal:
	    	return isAbnormal, False

	    contractGraph = {}
	    for item in contractList:
	        contractGraph[item['contract']] = item['inherit']
	    
	    searchPath = getInfo.inheritChain(contractList, contractGraph)

	    fileContent = modifyF.replaceSuper(searchPath, contractFunctionDict, fileContent)
	    
	    modSearchOrder, functionSearchOrder = getInfo.subChain(modDict, contractFunctionDict, searchPath)
	    fileContent = modifyF.eventList(fileContent, searchPath, contractDict)
	    
	    #update dict info due to delete of event statement
	    contractList, contractDict, libDict, libFunctionDict, mainContract, modDict, contractFunctionDict, contractConstructorDict = getInfo.findAllContracts(fileContent)
	    fileContent = modifyF.moveConstructFunc(contractFunctionDict, mainContract, fileContent)

	    contractList, contractDict, libDict, libFunctionDict, mainContract, modDict, contractFunctionDict, contractConstructorDict = getInfo.findAllContracts(fileContent)
	    statementDict, contractGlobalVar = getInfo.varStatement(contractList, contractDict, modDict, contractFunctionDict, contractConstructorDict, fileContent)

	    isHighRisk = False
	    checkVar = VarCheck()
	    isHighRisk = checkVar.check(contractDict, contractFunctionDict, statementDict, searchPath, fileContent)
	    if isHighRisk:
	    	return isAbnormal, isHighRisk

	    fileContent = modifyF.EPluribusUnum(modSearchOrder, functionSearchOrder, contractList, contractDict, modDict, contractFunctionDict, mainContract, contractConstructorDict, statementDict, searchPath, fileContent)
	    
	    #delete constructor
	    contractList, contractDict, libDict, libFunctionDict, mainContract, modDict, contractFunctionDict, contractConstructorDict = getInfo.findAllContracts(fileContent)
	    fileContent = modifyF.delConstructor(fileContent, contractConstructorDict, mainContract)

	    contractList, contractDict, libDict, libFunctionDict, mainContract, modDict, contractFunctionDict, contractConstructorDict = getInfo.findAllContracts(fileContent)
	    contractElemLibDict = getInfo.libBindingDict(fileContent, libDict, libFunctionDict, contractDict)
	    
	    replaceF = Replace()
	    fileContent = replaceF.functionReplace(contractDict, fileContent, modSearchOrder, modDict, contractFunctionDict, searchPath, contractElemLibDict, libFunctionDict)
	    
	    contractList, contractDict, libDict, libFunctionDict, mainContract, modDict, contractFunctionDict, contractConstructorDict = getInfo.findAllContracts(fileContent)
	    fileContent, saveList = modifyF.saveRelContract(mainContract, contractDict, fileContent)
	    
	    contractList, contractDict, libDict, libFunctionDict, mainContract, modDict, contractFunctionDict, contractConstructorDict = getInfo.findAllContracts(fileContent)
	    # STEP 2 Slicing
	    Slicer = Slicing()
	    reservedList = Slicer.reserve(fileContent, mainContract, contractDict, contractList, contractFunctionDict, customTag, saveList)
	    
	    #step 4

	    newFile = "merged_" + filename
	    op = open(newFile, "w+")

	    # Write
	    op.write(str(contractList.index(mainContract)) + "\n")
	    op.write(mainContract['contract']+"\n")
	   
	    for i in reservedList:
	        if i['line'].strip():
	            op.write(i['line'])
	    
	    #for i in fileContent:
	    #    op.write(i)

	    #Close files
	    op.close()

	    return False, False

