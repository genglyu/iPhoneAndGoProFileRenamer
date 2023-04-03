# generate testing files to test the GoProVideoFileNameModifier.py.
# The empty testing files are in the format of AABBCCCC.MP4, AABBCCCC.LRV and AABBCCCC.THM.
# AA is the codex of the video, usually GX or GP.
# BB is the chapter number, usually 01, possibly 02, 03 or further.
# CCCC is the sequence number, usually 0001, 0002, 0003 or further.

# The testing files shall include 10 * 3 AABBCCCC.MP4 files, 10 AABBCCCC.LRV files and 10 AABBCCCC.THM files.
# With 4 randomize the sequence numbers, the sequences has 1, 2, 3, 4 chapters respectively.

import os
import os.path
import time
import re
import datetime
import shutil


def makeEmptyFileInCurrentFolder(fileName, extension):
    # make an empty file in the current folder
    # fileName is the name of the file, without extension
    # extension is the extension of the file, with dot
    # return the full path of the file
    filePath = os.path.join(os.getcwd(), fileName + extension)
    file = open(filePath, "w")
    file.close()
    return filePath

def generateTestingFileNameList(chapterNumber, sequenceNumber):
    # generate a list of testing file names
    # chapterNumber is the number of chapters
    # sequenceNumber is the number of sequences
    # return the list of testing file names
    testingFileNameList = []
    for i in range(1, chapterNumber + 1):
        for j in range(1, sequenceNumber + 1):
            testingFileNameList.append("GP" + str(i).zfill(2) + str(j).zfill(4))
    return testingFileNameList

def generateTestingFiles(chapterNumber, sequenceNumber):
    # generate testing files
    # chapterNumber is the number of chapters
    # sequenceNumber is the number of sequences
    # return the list of testing file names
    testingFileNameList = generateTestingFileNameList(chapterNumber, sequenceNumber)
    for i in range(0, len(testingFileNameList)):
        makeEmptyFileInCurrentFolder(testingFileNameList[i], ".MP4")
        makeEmptyFileInCurrentFolder(testingFileNameList[i], ".LRV")
        makeEmptyFileInCurrentFolder(testingFileNameList[i], ".THM")
    return testingFileNameList

def main():
    # main function
    # generate testing files
    # return nothing
    testingFileNameList = generateTestingFiles(4, 10)
    print("The testing files are generated in the current folder.")
    print("The testing file names are:")
    for i in range(0, len(testingFileNameList)):
        print(testingFileNameList[i])

if __name__ == "__main__":
    main()
    