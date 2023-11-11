# delete all .MP4, .LRV, .THM files which are smaller than 10KB in the current folder.

import os
import os.path

from FileUtility import *

def deleteSmallFilesByExtension(folderPath, fileExtension, size):
    # Delete all files in the folder with the specified file extension.
    # folderPath is the path of the folder
    # fileExtension is the file extension
    # size is the size of the file in KB
    filePathList = getFilePathListByFileExtension(folderPath, fileExtension)
    for filePath in filePathList:
        fileSize = os.path.getsize(filePath)
        if fileSize < size * 1024:
            print("Deleting " + filePath)
            os.remove(filePath)

def main():
    # Delete all .MP4, .LRV, .THM files which are smaller than 10KB in the current folder.
    folderPath = os.getcwd()
    size = 10
    deleteSmallFilesByExtension(folderPath, ".MP4", size)
    deleteSmallFilesByExtension(folderPath, ".LRV", size)
    deleteSmallFilesByExtension(folderPath, ".THM", size)
    
if __name__ == "__main__":
    main()
    