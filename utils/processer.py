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
        mergeFile = Merge()
        mainContract = mergeFile.mergeReduce(file, fFileContent, argvs)
        #print(mainContract)
        if mainContract == "NULLNULLNULL":
            isAbnormal = True
        if not isAbnormal:
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

            srcProcessedPath = path + "/" + file
            desProcessedPath = path + "/ProcessedContracts/" + file
            shutil.copy(srcProcessedPath, desProcessedPath)
            print(file, " has been moved to the ProcessedContracts directory.")

        else:
            srcProcessedPath = path + "/" + file
            desProcessedPath = path + "/abnormalContracts/" + file
            shutil.copy(srcProcessedPath, desProcessedPath)
            print(file, " has been moved to the abnormalContracts directory.")

        #remove formatted contract
        formattedFile = path + "/" + fFile
        #print(formattedFile)
        os.remove(formattedFile)
        os.remove(preFile)

        os.remove(srcProcessedPath)
        


if __name__ == "__main__":
    filename = sys.argv[1]
    argvs = ''
    if len(sys.argv) > 2:
        argvs = sys.argv[2]
    main(filename, argvs)
