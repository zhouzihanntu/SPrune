import sys
import re

class Formatter:

    def formatCommentAndEnum(self, fileContent):
        block = ""
        blockStart = -1
        blockEnd = -1
        pattern4Enum = re.compile(r'\Wenum\s')
        pattern4InlineText = re.compile(r'\,\s*\".*\"')
        pattern4Comment = re.compile(r'//.*$')
        pattern4Comment1 = re.compile(r'(\/?\/\*((?!\*\/).)*\*\/)')
        pattern4Quote = re.compile(r'(\"|\')+[^\"\']*//[^\"\']*(\"|\')')
        for index, l in enumerate(fileContent):
            result4InlineText = pattern4InlineText.findall(l)
            l = pattern4InlineText.sub("", l)
            if not l.strip().startswith("/*"):
                if not l.strip().endswith("*/"):
                    l = pattern4Comment1.sub("", l)
                else:
                    l = pattern4Comment1.sub("", l) + "\r\n"

            fileContent[index] = l

            if block != "":
                pass
            elif l.strip().startswith("/*"):
                block = "comment"
                l = pattern4Comment.sub("", l)
                pass
            else:
                result = pattern4Enum.findall(l)
                if result and "{" in l:
                    blockStart = index
                    block = "enum"

            if block == "comment":
                #print(l)
                fileContent[index] = "\r\n"
                if l.strip().endswith("*/"):
                    block = ""
            elif block == "enum":
                result4Quote = pattern4Quote.findall(l)
                if not result4Quote:
                    l = pattern4Comment.sub("", l)
                fileContent[index] = l
                if blockStart != -1 and l.strip().endswith("}"):
                    blockEnd = index
                    if blockStart != blockEnd:
                        fileContent[blockStart] = " ".join(fileContent[blockStart:blockEnd + 1]).replace("\n", "") + "\r\n"
                        fileContent[blockStart + 1:blockEnd + 1] = ["\r\n"] * (blockEnd - blockStart)
                    block = ""
                    blockStart, blockEnd = -1, -1
            else:
                result4Quote = pattern4Quote.findall(l)
                if not result4Quote:
                    l = pattern4Comment.sub("", l)
                fileContent[index] = l
        return fileContent

    def formatFunction(self, fileContent):
        pattern4OneLineFunc = re.compile(r'\A(function\s+|modifier\s+|contract\s+|interface\s+|constructor\s*\()[^\{]*\{')
        #pattern4OneLineContract = re.compile(r'\A(function|modifier)\s+[^\{]*\{')
        block = []
        flag = 0
        end = 0
        for index, line in enumerate(fileContent[flag:]):
            if line.strip() == "_":
                line = line.replace("_", "_;")
                fileContent[index] = line

        while not end:
            for index, line in enumerate(fileContent[flag:]):
                result4OneLineFunc = pattern4OneLineFunc.findall(line.strip())
                if result4OneLineFunc and line.strip().endswith("}"):
                    #print(line)
                    strStart = line.find(line.strip())
                    preStr = line[0:strStart]
                    sLeftParenArray = line.strip().split("{")
                    sRightParenArray = []
                    for iL, sL in enumerate(sLeftParenArray):
                        if iL < len(sLeftParenArray) - 1:
                            sLeftParenArray[iL] = sL + "{"
                        if len(sLeftParenArray[iL].split("}")) > 1:
                            for iR, sR in enumerate(sLeftParenArray[iL].split("}")):
                                if iR < len(sLeftParenArray[iL].split("}")) - 1:
                                    sRightParenArray = sRightParenArray + [sR] + ["}"]
                        else:
                            sRightParenArray.append(sLeftParenArray[iL])
                    sSemiArray = []
                    for iS, sS in enumerate(sRightParenArray):
                        if len(sS.split(";")) > 1:
                            for iSemi, sSemi in enumerate(sS.split(";")):
                                if iSemi < len(sS.split(";")) - 1:
                                    sSemiArray = sSemiArray + [preStr + sSemi + ";\r\n"]
                        else:
                            if sS.split(";")[0].strip() == "_":
                                sSemiArray.append(preStr + "_;\r\n")
                            else:
                                sSemiArray.append(preStr + sS.split(";")[0] + "\r\n")
                    block = sSemiArray
                    fileContent = fileContent[0:flag + index] + block + fileContent[flag + index+1:]
                    flag = flag + index
                    block = []
                    break

                if index == len(fileContent) - flag - 1:
                    end = 1

        return fileContent

    def formatSpaceBeforeParen(self, fileContent):
        pattern4SpaceA = re.compile(r'(\w+)\s*(\()')
        pattern4LeftSpaceB = re.compile(r'(\s+\[\s*)|(\s*\[\s+)')
        pattern4RightSpaceB = re.compile(r'(\s+\]\s*)(?!\w)|(\s*\]\s+)(?!\w)')
        pattern4SpaceC = re.compile(r'(\w+)\s*(\{)')
        pattern4SpaceSubA = re.compile(r'\b(\s*)(\()')
        pattern4SpaceSubC = re.compile(r'\b(\s*)(\{)')
        for index, l in enumerate(fileContent):
            result4SpaceA = pattern4SpaceA.findall(l)
            result4LeftSpaceB = pattern4LeftSpaceB.findall(l)
            result4SpaceC = pattern4SpaceC.findall(l)
            if result4SpaceA:
                l = pattern4SpaceSubA.sub('(', l)
                fileContent[index] = l
            if result4LeftSpaceB:
                l = pattern4LeftSpaceB.sub("[", l)
                fileContent[index] = l
            result4RightSpaceB = pattern4RightSpaceB.findall(l)
            if result4RightSpaceB:
                l = pattern4RightSpaceB.sub("]", l)
                fileContent[index] = l
            if result4SpaceC:
                l = pattern4SpaceSubC.sub('{', l)
                fileContent[index] = l

        return fileContent

    def formatOperator(self, fileContent):
        pattern4AssignOp = re.compile(r'([^\(\s]*)\s*([\+\-\*\%\**\//])\=\s*([^\;\)]*)')
        for idx, line in enumerate(fileContent):
            result4AssignOp = pattern4AssignOp.findall(line)
            if result4AssignOp:
                line = pattern4AssignOp.sub( result4AssignOp[0][0] + ' = ' + result4AssignOp[0][0] + ' ' + result4AssignOp[0][1] + ' ' + result4AssignOp[0][2], line)
                fileContent[idx] = line
        return fileContent

    def formatFallbackFunction(self, fileContent):
        pattern4Function = re.compile(r'\W*function\W([^\(]*)')
        pattern4SpaceSub = re.compile(r'function(\s*)\(')
        for index, l in enumerate(fileContent):
            result4Function = pattern4Function.findall(l)
            result4SpaceSub = pattern4SpaceSub.findall(l)

            if result4SpaceSub and result4Function:
                l = pattern4SpaceSub.sub('function fallback(', l)
                fileContent[index] = l
        return fileContent

    def formatFunctionStat(self, fileContent):
        blockStart = -1
        blockEnd = -1
        pattern4UnusedFunc = re.compile(r'\Afunction\s+[^\{]*\;')
        #pattern4UnusedFunc = re.compile(r'\A(function\s.*\;|function\s.*\{[^\w]*\})')
        pattern4Func = re.compile(r'\A(function|modifier)\s+(\w+)\s*\(?')
        pattern4FuncWithArgvs = re.compile(r'(\Afunction|modifier)\s+\w+\s*\(')
        pattern4NonArgvsMod = re.compile(r'\Amodifier\s+(\w+)[^(]*')
        func = ""
        for index, l in enumerate(fileContent):
            result4UnusedFunc = pattern4UnusedFunc.findall(l.strip())
            result4Func = pattern4Func.findall(l.strip())
            result4NonArgvsMod = pattern4NonArgvsMod.findall(l.strip())
                
            if result4UnusedFunc:
                fileContent[index] = "\r\n"
            if result4Func and not result4UnusedFunc and not "{" in l:
                blockStart = index
                #print(l)
                func = result4Func[0][1]
            if blockStart != -1 and (l.strip().endswith("{") or "{" in l) or blockStart != -1 and l.strip().endswith(";"):
                blockEnd = index
                if blockStart != blockEnd:
                    string = " "
                    for f in fileContent[blockStart:blockEnd + 1]:
                        string = string + f.strip() + " "
                    firstLineStart = fileContent[blockStart].find(fileContent[blockStart].strip())
                    string = fileContent[blockStart][0:firstLineStart] + string

                    result4FuncWithArgvs = pattern4FuncWithArgvs.findall(string.strip())
                    if not result4FuncWithArgvs:
                        string = string[0:string.find(func) + len(func)] + "() " + string[string.find("{"):]
                    #print(string)
                    fileContent[blockStart] = string + "\r\n"
                    fileContent[blockStart + 1:blockEnd + 1] = ["\r\n"] * (blockEnd - blockStart)
                result4UnusedFunc = pattern4UnusedFunc.findall(fileContent[blockStart].strip())
                if result4UnusedFunc:
                    fileContent[blockStart] = "\r\n"
                func = ""
                blockStart, blockEnd = -1, -1
        return fileContent

    def formatContract(self, fileContent):
        blockStart = -1
        blockEnd = -1
        addLine = []
        count = 0
        pattern4Contract = re.compile(r'(contract\s+\w+\Wis\W|contract\s+\w+|constructor\s*\()|library\s+\w+')
        for index, l in enumerate(fileContent):
            result4Contract = pattern4Contract.match(l.strip())
            if result4Contract:
                #print(l)
                if l.count("{") == l.count("}") and l.strip().endswith("}"):
                    if len(l.split("{")) == 2:
                        fileContent[index + count] = l.split("{")[0] + "{" + "\r\n"
                        addLine.append(l.split("{")[1])
                        fileContent = fileContent[0:index + count+1] + addLine + fileContent[index + count+1:]
                        count = count + 1
                        addLine = []
                else:
                    blockStart = index
            #if blockStart != -1 and l.strip().endswith("{"):
            if blockStart != -1 and "{" in l:
                blockEnd = index
                if blockStart != blockEnd:
                    string = " "
                    for f in fileContent[blockStart:blockEnd + 1]:
                        string = string + f.strip() + " "
                    firstLineStart = fileContent[blockStart].find(fileContent[blockStart].strip())
                    string = fileContent[blockStart][0:firstLineStart] + string
                    fileContent[blockStart] = string + "\r\n"
                    fileContent[blockStart + 1:blockEnd + 1] = ["\r\n"] * (blockEnd - blockStart)

                blockStart, blockEnd = -1, -1

        return fileContent

    def formatEventAndEmit(self, fileContent):
        blockStart = -1
        blockEnd = -1
        pattern4EventAndEmit = re.compile(r'(event|emit)\s\w+\W*\(')
        pattern4MultiLineParen = re.compile(r'\w*\(')
        for index, l in enumerate(fileContent):
            result4EventAndEmit = pattern4EventAndEmit.findall(l.strip())
            result4MultiLineParen = pattern4MultiLineParen.findall(l.strip())
            if result4EventAndEmit:
                #print(result4EventAndEmit)
                #print(l)
                blockStart = index
            if blockStart != -1 and l.strip().endswith(";"):
                blockEnd = index

                if blockStart != blockEnd:
                    for i in range(blockStart, blockEnd+1):
                        if i == blockStart:
                            fileContent[i] = fileContent[i].rstrip()    
                        else:
                            fileContent[i] = fileContent[i].strip()
                    fileContent[blockStart] = " ".join(fileContent[blockStart:blockEnd + 1]).replace("\n", "") + "\r\n"
                    fileContent[blockStart + 1:blockEnd + 1] = ["\r\n"] * (blockEnd - blockStart)
                    #print(fileContent[blockStart])
                blockStart, blockEnd = -1, -1
        return fileContent

    def formatMultiLineParen(self, fileContent):
        blockStart = -1
        blockEnd = -1
        pattern4MultiLineParen = re.compile(r'\w*\(')
        leftParenCount = 0
        rightParenCount = 0
        for index, l in enumerate(fileContent):
            result4MultiLineParen = pattern4MultiLineParen.findall(l)
            if result4MultiLineParen and blockStart == -1 and l.count("(") > l.count(")"):
                blockStart = index

            if blockStart != -1:
                leftParenCount = leftParenCount + l.count("(")
                rightParenCount = rightParenCount + l.count(")")
            if blockStart != -1 and leftParenCount == rightParenCount and leftParenCount > 0:
                blockEnd = index
                if blockStart != blockEnd:
                    string = ""
                    for f in fileContent[blockStart:blockEnd + 1]:
                        string = string + f.strip()
                    firstLineStart = fileContent[blockStart].find(fileContent[blockStart].strip())
                    string = fileContent[blockStart][0:firstLineStart] + string
                    fileContent[blockStart] = string + "\r\n"
                    fileContent[blockStart + 1:blockEnd + 1] = ["\r\n"] * (blockEnd - blockStart)
                blockStart, blockEnd = -1, -1
                leftParenCount, rightParenCount = 0, 0
        return fileContent

    def formatLoop(self, fileContent):
        pattern4Loop = re.compile(r'((while|for)\s*\([^)]*\))')
        pattern4LoopParen = re.compile(r'((while|for)\s*\([^)]*\)\s*\{)')
        count = 0
        for idx, line in enumerate(fileContent):
            result4Loop = pattern4Loop.findall(line)
            result4LoopParen = pattern4LoopParen.findall(line)
            block = []
            if result4Loop:
                if result4LoopParen:
                    if line.count("{") == line.count("}"):
                        strStart = line.find(result4LoopParen[0][0]) + len(result4LoopParen[0][0])
                        block.append(line[:strStart] + "\r\n")
                        block.append(line.find(line.strip()) * " " + line[strStart:].rstrip()[:-1] + "\r\n")
                        block.append(line.find(line.strip()) * " " + "}\r\n")
                        #print(idx + count, count)
                        fileContent = fileContent[:idx + count] + block + fileContent[idx + count + 1:]
                    elif (line.count("{") > line.count("}") and len(result4LoopParen[0][0]) < len(line.strip())):
                        strStart = line.find(result4LoopParen[0][0]) + len(result4LoopParen[0][0])
                        block.append(line[:strStart] + "\r\n")
                        block.append(line.find(line.strip()) * " " + line[strStart:].rstrip() + "\r\n")
                        fileContent = fileContent[:idx + count] + block + fileContent[idx + count + 1:]
                    else:
                        pass
                else:
                    if len(result4Loop[0][0]) < len(line.strip()):
                        strStart = line.find(result4Loop[0][0]) + len(result4Loop[0][0])
                        fileContent[idx + count] = line[:strStart] + "\r\n"
                        fileContent.insert(idx + count+1, line.find(line.strip()) * " " + line[strStart:])
                    else:
                        pass
            if len(block):
                count = count + len(block) - 1
        return fileContent

    def formatIfStatement(self, fileContent):
        pattern4SingleIf = re.compile(r'\Aif\W[^{]*\;')
        pattern4If = re.compile(r'\Aif\W*\([^)]*\)')
        pattern4ElseIf = re.compile(r'\A\}\W*else if\W*\([^)]*\)')
        pattern4ElseIf2 = re.compile(r'\Aelse if\W*\([^)]*\)')
        pattern4Else = re.compile(r'\Aelse\W')
        pattern4SingleElse = re.compile(r'\Aelse\W[^{]*\;')
        block = []
        end = 0
        newFile = []
        needAddBracket = -1
        #if 1:
        for idx, line in enumerate(fileContent):
            
            modifiedLine = False
            result4SingleIf = pattern4SingleIf.findall(line.strip())
            result4If = pattern4If.findall(line.strip())
            result4ElseIf = pattern4ElseIf.findall(line.strip())
            result4ElseIf2 = pattern4ElseIf2.findall(line.strip())
            result4Else = pattern4Else.findall(line.strip())
            result4SingleElse = pattern4SingleElse.findall(line.strip())

            if result4SingleIf or (result4SingleElse and not result4If):
                if result4SingleIf:
                    string = (result4ElseIf2[0] if result4ElseIf2 else result4If[0])
                    stringStart = line.find(string)
                    stringEnd = stringStart + len(string)
                    while list(string).count('(') > list(string).count(')'):
                        nextChar = line[stringEnd]
                        string += nextChar
                        stringEnd += 1
                elif result4SingleElse and not result4If:
                    string = result4Else[0]
                    stringStart = line.find(string)
                    stringEnd = stringStart + len(string)
                    stringStart = line.find(line.strip())
                if '{' not in line:
                    lineStart = line.find(line.strip())
                    block.append(line[0:stringEnd] + '{\n')
                    statements = line[stringEnd:].split(';')
                    for s in statements:
                        if s.strip():
                            block.append(line[0:lineStart] + '\t' + s + ';\n')
                    block.append(line[0:lineStart] + '}\n')
                    newFile = newFile + block
                    modifiedLine = True
                elif '{' in line:
                    while '{' not in string:
                        nextChar = line[stringEnd]
                        string += nextChar
                        stringEnd += 1
                    lineStart = line.find(line.strip())
                    block.append(line[0:stringEnd] + '\n')
                    if '}' in line:
                        statements = line[stringEnd:].replace('}', '').split(';')
                        for s in statements:
                            if s.strip():
                                block.append(line[0:lineStart] + '\t' + s + ';\n')
                        block.append(line[0:lineStart] + '}\n')
                    elif '}' not in line:
                        statements = line[stringEnd:].split(';')
                        for s in statements:
                            if s != '\n':
                                block.append(line[0:lineStart] + '\t' + s + ';\n')
                    newFile = newFile + block
                    modifiedLine = True

            elif result4ElseIf:
                #print(line)
                pos = line.find('}')
                block.append(line[0:pos+1] + '\n')
                block.append(line[0:pos] + line[pos+1:])
                newFile = newFile + block
                modifiedLine = True

            elif (result4If or result4ElseIf2 or result4Else):
                if not ("{" in line):
                    newFile = newFile + [line.rstrip() + " {\n"] 
                    modifiedLine = True
                    needAddBracket = line.find(line.strip())
                    parenNotFound = 1
                    ifStartIdx = idx + 1
                    while parenNotFound:
                        if fileContent[ifStartIdx].strip():
                            if "{" == fileContent[ifStartIdx].strip():
                                fileContent[ifStartIdx] = "\r\n"
                                needAddBracket = -1
                            elif fileContent[ifStartIdx].strip().startswith("{")  and fileContent[ifStartIdx].strip().endswith("}"):
                                strStart = fileContent[ifStartIdx].find(fileContent[ifStartIdx].strip())
                                strEnd = strStart + len(fileContent[ifStartIdx])
                                line = fileContent[ifStartIdx][0:strStart] + fileContent[ifStartIdx].strip()[1:-1] + fileContent[ifStartIdx][strEnd:] + "\r\n"
                                fileContent[ifStartIdx] = line
                                #print(line)
                                #needAddBracket = -1
                            parenNotFound = 0    
                        else:
                            ifStartIdx = ifStartIdx + 1

                elif "}" in line and (line.find("{") < line.rindex("}")):

                    leftParenLoc = line.find("{") + 1
                    rightParenLoc = line.rindex("}")
                    stringStart = line.find(line.strip())
                    block.append(line[0:leftParenLoc] + "\n")
                    statements = line[leftParenLoc:rightParenLoc].split(';')
                    for s in statements:
                        if s.strip():
                            block.append(line[0:stringStart] + '\t' + s + ';\n')
                    block.append(line[0:stringStart] + '}\n')
                    newFile = newFile + block
                    modifiedLine = True
     
            if not modifiedLine:
                if needAddBracket > -1:
                    newFile += [line, " " * needAddBracket + "}\n"]
                    needAddBracket = -1
                else:
                    newFile += [line]
            block = []
        return newFile

    def formatIfElseParen(self, fileContent):
        pattern4IfElse = re.compile(r'if\W|else\W')
        pattern4Else = re.compile(r'\}\W*else')
        for idx, line in enumerate(fileContent):
            result4Else = pattern4Else.findall(line.strip())
            if result4Else:
                lineBuffer = line
                strPrefix = line[0:line.find("}")]
                line = strPrefix + "}" + "\r\n"
                fileContent[idx] = line
                fileContent.insert(idx + 1, strPrefix + lineBuffer[lineBuffer.find("}")+1:])
            result4IfElse = pattern4IfElse.findall(line.strip())
            if result4IfElse:
                strPrefix = line[0:line.find("{")]
                fileContent[idx] = strPrefix + "\r\n"
                strPrefix = line[0:line.find(line.strip())]
                fileContent.insert(idx + 1, strPrefix + line[line.find("{"):])
        return fileContent

    def formatMultiParen(self, fileContent):
        count = 0
        for idx, l in enumerate(fileContent):
            block = []
            if l.count("}") > 1 and l.strip().startswith("}"):
                strStart = l.find("}") + 1
                block.append(l[:strStart] + "\r\n")
                block.append(l.find(l.strip()) * " " + l[strStart:].rstrip() + "\r\n")
                fileContent = fileContent[:idx + count] + block + fileContent[idx + count + 1:]
            if len(block):
                count = count + len(block) - 1
        return fileContent
    #format space before "."
    def formatVarType(self, fileContent):
        pattern4Int = re.compile(r'(\W(int|uint)\W)')
        #pattern4Int2 = re.compile(r'(\A(int|uint)\W)')
        pattern4Byte = re.compile(r'(\W(byte)\W)')
        pattern4Point = re.compile(r'\s*(\.)\s*')
        pattern4Array = re.compile(r'\w(\[\d*\])\w')
        for idx, line in enumerate(fileContent):
            result4Int = pattern4Int.findall(line)
            if result4Int:
                #print(line)
                for singleResult in result4Int:
                    line = fileContent[idx]
                    subGoal = singleResult[0][0:-1] + "256" + singleResult[0][-1]
                    startIdx = line.find(singleResult[0])
                    endIdx = startIdx + len(singleResult[0])
                    fileContent[idx] = line[0:startIdx] +  subGoal + line[endIdx:] 
            result4Byte = pattern4Byte.findall(line)
            if result4Byte:
                for singleResult in result4Byte:
                    line = fileContent[idx]
                    subGoal = singleResult[0][0:-1] + "s1" + singleResult[0][-1]
                    startIdx = line.find(singleResult[0])
                    endIdx = startIdx + len(singleResult[0])
                    fileContent[idx] = line[0:startIdx] +  subGoal + line[endIdx:] 
            result4Point = re.search( r'\s*(\.)\s*', line)
            if result4Point:
                line = pattern4Point.sub(".", line)
                fileContent[idx] = line
            result4Array = re.search( r'\w(\[\d*\])\w', line)
            if result4Array:
                line = pattern4Array.sub(result4Array.group()[0:-1] + " " + result4Array.group()[-1], line)
                fileContent[idx] = line

        return fileContent

    def formatUsing(self,fileContent):
        pattern4Using = re.compile(r'\Ausing\s+\w+')
        pattern4Using2 = re.compile(r'\Afor\s+\w+')
        for idx, l in enumerate(fileContent):
            result4Using = pattern4Using.findall(l.strip())
            if result4Using:
                result4Using2 = pattern4Using2.findall(fileContent[idx+1].strip())
                if result4Using2:
                    l = l.rstrip() + " " + fileContent[idx+1].lstrip()
                    fileContent[idx] = l
                    fileContent[idx + 1] = "\r\n"

        return fileContent

    def formatStruct(self, fileContent):
        pattern4Struct = re.compile(r'\Astruct\s+(\w+)\s*\{')
        blockStart = -1
        blockEnd = -1
        leftParenCount = 0
        rightParenCount = 0
        for idx, line in enumerate(fileContent):
            result4Struct = pattern4Struct.findall(line.strip())
            if blockStart == -1 and result4Struct and line.count('{') > line.count('}'):
                blockStart = idx
                #print(line)
            if blockStart != -1:
                leftParenCount = leftParenCount + line.count("{")
                rightParenCount = rightParenCount + line.count("}")
            if blockStart != -1 and leftParenCount == rightParenCount and leftParenCount > 0:
                blockEnd = idx
                if blockStart != blockEnd:
                    string = ""
                    for f in fileContent[blockStart:blockEnd + 1]:
                        string = string + f.strip()
                    firstLineStart = fileContent[blockStart].find(fileContent[blockStart].strip())
                    string = fileContent[blockStart][0:firstLineStart] + string
                    fileContent[blockStart] = string + "\r\n"
                    fileContent[blockStart + 1:blockEnd + 1] = ["\r\n"] * (blockEnd - blockStart)
                blockStart, blockEnd = -1, -1
                leftParenCount, rightParenCount = 0, 0

        return fileContent

    def formatter(self, filename, fileContent):

        fileContent = self.formatCommentAndEnum(fileContent)
        
        fileContent = self.formatFunction(fileContent)
        
        fileContent = self.formatContract(fileContent)
        
        fileContent = self.formatFunction(fileContent)

        fileContent = self.formatFallbackFunction(fileContent)

        fileContent = self.formatFunctionStat(fileContent)

        fileContent = self.formatFunction(fileContent)
        
        fileContent = self.formatEventAndEmit(fileContent)
        
        fileContent = self.formatMultiLineParen(fileContent)

        fileContent = self.formatLoop(fileContent)
        
        fileContent = self.formatIfStatement(fileContent)

        # remove spaces before parens
        fileContent = self.formatSpaceBeforeParen(fileContent)

        fileContent = self.formatOperator(fileContent)
        
        fileContent = self.formatIfElseParen(fileContent)
        
        fileContent = self.formatMultiParen(fileContent)

        fileContent = self.formatVarType(fileContent)

        #jsbeautifier
        fileContent = self.formatUsing(fileContent)

        fileContent = self.formatStruct(fileContent)
        
        newFile = "formatted_" + filename
        op = open(newFile, "w+")
        
        pattern4Blank = re.compile(r'^[ \t]*\n|^[\r\n]|^[\n]')
        # Write
        for i in fileContent:
            result4Blank = pattern4Blank.findall(i)
            if not result4Blank and i.strip():
                op.write(i)
                #print(i)
        # Close files
        op.close()
