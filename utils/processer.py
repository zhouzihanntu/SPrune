import os
import sys
import shutil
import jsbeautifier


from utils.content import getContent
from utils.formatter import Formatter
from utils.merge import Merge
from utils.classify import Classifier 

class Process:
    def main(self, file, argvs):
        path = sys.path[0]

        print("****************************")
        print(file)
        res = jsbeautifier.beautify_file(file)
        preFile = "preformat_" + file
        op = open(preFile, "w+")
        op.write(res)
        op.close()

        oFileContent = getContent(preFile)
        formatFile = Formatter()
        formatFile.formatter(file, oFileContent)
        
        fFile = "formatted_" + file
        fFileContent = getContent(fFile)

        isAbnormal = False
        isHighRisk = False
        mergeFile = Merge()
        isAbnormal, isHighRisk = mergeFile.mergeReduce(file, fFileContent, argvs)
        print(isAbnormal, isHighRisk)
        
        srcProcessedPath = path + "/" + file
        if not isAbnormal and not isHighRisk:
            #classify processible contract
            classify = Classifier()
            mFile = "merged_" + file
            mFileContent = getContent(mFile)
            isProcessible = classify.classifier(mFileContent)
            print(isProcessible)
            srcProcessiblePath = path + "/" + mFile
            if isProcessible:
                dstProcessiblePath = path + "/Processible/" + mFile
                shutil.copy(srcProcessiblePath, dstProcessiblePath)
                print(mFile, " is processible and has been put in the Processible directory.")
                os.remove(srcProcessiblePath)
            else:
                os.remove(srcProcessiblePath)
            desProcessedPath = path + "/ProcessedContracts/" + file
            noteStr = "ProcessedContracts"
        elif not isAbnormal and isHighRisk:
            desProcessedPath = path + "/varRepeatContracts/" + file
            noteStr = "varRepeatContracts"
        elif isAbnormal and not isHighRisk:
            desProcessedPath = path + "/abnormalContracts/" + file
            noteStr = "abnormalContracts"

        shutil.copy(srcProcessedPath, desProcessedPath)
        print(file, " has been moved to the " + noteStr +" directory.")
        
        #remove formatted contract
        formattedFile = path + "/" + fFile
        os.remove(formattedFile)
        os.remove(preFile)
        os.remove(srcProcessedPath)
        


if __name__ == "__main__":
    filename = sys.argv[1]
    argvs = ''
    if len(sys.argv) > 2:
        argvs = sys.argv[2]
    main(filename, argvs)
