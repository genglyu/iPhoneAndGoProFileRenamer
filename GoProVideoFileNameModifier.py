# GoPro video file name is in the format of AABBCCCC.MP4
# AA is the codex of the video, usually GX or GP.
# BB is the chapter number, usually 01, possibly 02, 03 or further.
# CCCC is the sequence number, usually 0001, 0002, 0003 or further.
# This script will rename the all video file names in the same folder to the format of Date_CameraID_CCCC_BB_Time_AA.MP4, 
# in which Date is the date of the video, AA is the codex, CCCC is the sequence number, BB is the chapter number 
# and Time is the time of the video.

import os
import os.path
import time
import re
import datetime
import shutil


def makeNewFileNameWithReplacedCameraID(fileName, oldCameraID, newCameraID):
    # replace the old camera ID in the file name with the new camera ID
    # fileName is the name of the file, without extension
    # oldCameraID is the old camera ID
    # newCameraID is the new camera ID

    # check if the file name contains the old camera ID
    if not oldCameraID in fileName:
        print("The file name " + fileName + " does not contain the old camera ID " + oldCameraID + ".")
        return fileName
    else:
        # replace the old camera ID with the new camera ID
        print("The file name " + fileName + " contains the old camera ID " + oldCameraID + ".")
        newFileName = fileName.replace(oldCameraID, newCameraID)
        return newFileName

def replaceAllCameraIDInFileNameInCurrentFolder(oldCameraID, newCameraID):
    # replace the old camera ID in all file names in the current folder with the new camera ID
    # oldCameraID is the old camera ID
    # newCameraID is the new camera ID
    # return nothing
    # get the list of all files in the current folder
    fileList = os.listdir(os.getcwd())
    for fileName in fileList:
        # check if the extension of the file is MP4
        if fileName[-4:].upper() == ".MP4":
            newFileName = makeNewFileNameWithReplacedCameraID(fileName, oldCameraID, newCameraID)
            # rename the file
            os.rename(fileName, newFileName)
    print("The camera ID in all file names in the current folder is replaced with the new camera ID.")

def checkTheFileNameFormat(fileName):
    # check if the file name is in the format of AABBCCCC.MP4
    # fileName is the name of the file, without extension
    # return True if the file name is in the format of AABBCCCC.MP4, otherwise return False
    
    # check if the file name is in the format of Date_CameraID_CCCC_BB_Time_AA.MP4
    # try split the file name into 6 parts.
    try:
        fileNameParts = re.split("_", fileName)
        # check if the there are 6 parts
        if len(fileNameParts) == 6:
            print ("The file name " + fileName + " is possibly processed already.")
            return False
    except:
        pass
    # chekc if the file name is in the format of AABBCCCC.MP4    
    if len(fileName) != 12:
        return False
    if not fileName[0:2].isalpha():
        return False
    if not fileName[2:4].isdigit():
        return False
    if not fileName[4:8].isdigit():
        return False
    if fileName[8:12] != ".MP4":
        return False
    return True

def getModifiedDateTime(filePath):
    # Get the modified date and time of the file. return two strings in the format of YYYYMMDD, HHMMSS
    # filePath is the path of the file
    # modifiedDate is the date of the file in the format of YYYYMMDD
    # modifiedTime is the time of the file in the format of HHMMSS
    
    # get the modified time of the file in seconds since the epoch
    fileModifiedTimeBySeconds = os.path.getmtime(filePath)
    # convert the modified time to a datetime object
    fileModifiedDateTime = datetime.datetime.fromtimestamp(fileModifiedTimeBySeconds)
    extractedDate = fileModifiedDateTime.strftime("%Y%m%d")
    extractedTime = fileModifiedDateTime.strftime("%H%M%S")
    
    print("File name is: " + filePath)
    print("The modified time of the file is: " + extractedDate)
    print("The modified date of the file is: " + extractedTime)
    
    return extractedDate, extractedTime


def getFileNameListByFileExtensionNotCaseSensitive(folderPath, fileExtension):
    fileNameList = []
    for fileName in os.listdir(folderPath):
        if fileName.lower().endswith(fileExtension.lower()):
            fileNameList.append(fileName)
    return fileNameList

def makeNewFileNameFromOldFileName(oldFileName, cameraID):
    # oldFileName is in the format of AABBCCCC.MP4
    # newFileName is in the format of Date_CCCC_BB_Time_AA.MP4
    # Date is the date of the video. CCCC is the sequence number. BB is the chapter number. Time is the time of the video. AA is the codex.
    # The date, time are extracted from the file info. The sequence number, chapter number and codex are extracted from the file name.
    
    # check if the file name is in the format of AABBCCCC.MP4
    if not checkTheFileNameFormat(oldFileName):
        print("The file name " + oldFileName + " is not in the format of AABBCCCC.MP4. Test in makeNewFileNameFromOldFileName")
        return oldFileName
    codex = oldFileName[0:2]
    chapterNumber = oldFileName[2:4]
    sequenceNumber = oldFileName[4:8]
    extension = oldFileName[8:]
    dateModified = getModifiedDateTime(oldFileName)
    newFileName = dateModified[0] + "_" + cameraID + "_" + sequenceNumber + "_" + chapterNumber + "_" + dateModified[1] + "_" + codex + extension
    return newFileName


def renameAllFilesInFolderFromGoProFormatToCustom(folderPath, fileExtension, cameraID):
    # Process all files in the folder with the specified file extension.
    # folderPath is the path of the folder
    # fileExtension is the file extension
    fileNameList = getFileNameListByFileExtensionNotCaseSensitive(folderPath, fileExtension)
    for fileName in fileNameList:
        if not checkTheFileNameFormat(fileName):
            print("The file name " + fileName + " is not in the format of AABBCCCC.MP4. Test in processAllFilesInFolder")
        else:
            newFileName = makeNewFileNameFromOldFileName(fileName, cameraID)
            print("Renaming " + fileName + " to " + newFileName)
            os.rename(fileName, newFileName)
            
def deleteFileByExtension(folderPath, fileExtension):
    # Delete all files in the folder with the specified file extension.
    # folderPath is the path of the folder
    # fileExtension is the file extension
    fileNameList = getFileNameListByFileExtensionNotCaseSensitive(folderPath, fileExtension)
    for fileName in fileNameList:
        print("Deleting " + fileName)
        os.remove(fileName)

def deleteTrashFiles(folderPath):
    #remove all files with the extension of .THM or .LRV
    deleteFileByExtension(folderPath, ".THM")
    deleteFileByExtension(folderPath, ".LRV")
            
