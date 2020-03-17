import os
import sys
from utils.content import getContent
from utils.processer import Process


class batchProcess:

    def getCustomKeyword(self, keyInfo, file):
        keyword = ""
        for line in keyInfo:
            if line.strip().startswith(file):
                if len(line.strip().split("*")) > 1:
                    keyword = line.strip().split("*")[-1]
                    #print(keyword)
        return keyword

    def main(self, filename, argv):
        
        process = Process()
        if filename:
            print(filename)
            process.main(filename, argv)
        else:
            keyInfo = getContent("customKeywords.txt")
            path = sys.path[0]
            fileList = os.listdir(path)
            count = 0
            for file in fileList[0:500]:
                if file.endswith(".sol"):
                    #print(file)
                    argv = self.getCustomKeyword(keyInfo, file)
                    #print(argv)
                    process.main(file, argv)
                    count = count + 1
                    print(str(len(fileList) - count) + " contracts remaining.")
        
if __name__ == "__main__":
    filename = ""
    argv = ""
    #print(sys.argv)
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    if len(sys.argv) == 3:
        argv = sys.argv[2]
    batchProcess = batchProcess()
    batchProcess.main(filename, argv)
