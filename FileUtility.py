# In this file, there are some general file utility functions.
# most of the functions are used to recognize the file name format
# and extract the data not shown in file names.

# GoPro video file name is in the format of AABBCCCC.MP4

# AA is the codex of the video, usually GX or GP.
# BB is the chapter number, usually 01, possibly 02, 03 or further.
# CCCC is the sequence number, usually 0001, 0002, 0003 or further.

# the iPhone video file name is in the format of IMG_CCCC.MOV
# XXXX is the sequence number, usually 0001, 0002, 0003 or further.

# The iPhone image file name is in the format of IMG_XXXX.HEIC or IMG_XXXX.JPG
# XXXX is the sequence number, usually 0001, 0002, 0003 or further.

# The targeted file name format is 
# YYYYMMDD_HHMMSS_XY_DDDDD_CCCC_BB_AA.*
# Date_Time_CameraAndDataType_CameraID_SequenceID_ChapterID_Codex.*,

# in which Date is the date of the video, 
# Time is the time of the video.
# When the chapter number BB is not 01, which is the case for the GoPro video, 
# the "Time" is going to be set to the same with the chapter 01.

# AA is the codex, CCCC is the sequence number, BB is the chapter number 
# For iPhone video and images, BB and AA are not applicable, so they are set to be 00.

DEBUG = False

from argparse import OPTIONAL
import os
import os.path
import time
import re
import datetime
import shutil
from enum import Enum

# from moviepy.editor import VideoFileClip

# the potential file extension for the video file
goproVideoFileExtensionList = [".MP4"]
goproImageFileExtensionList = [".JPG", ".PNG"]

goproUtilityFileExtensionList = [".THM", ".LRV"]

iphoneVideoFileExtensionList = [".MOV"]
iphoneImageFileExtensionList = [".HEIC", ".JPG"]

cameraVideoFileExtensionList = [".MOV"]
cameraImageFileExtensionList = [".HEIC", ".JPG"]

# define the camera and data type GoPro video, GoPro image, iPhone video, iPhone image, 
# and link them to abbreviations used in the file name. GV, GI, IV, II
class CameraAndDataType(Enum):
    '''the camera and data type GoPro video, GoPro image, iPhone video, iPhone image'''
    UNKNOWN = 0
    GoProVideo = 1
    GoProImage = 2
    iPhoneVideo = 3
    iPhoneImage = 4
    CameraVideo = 5
    CameraImage = 6

CameraAndDataTypeAbbreviation = {
    CameraAndDataType.UNKNOWN: "XX",
    CameraAndDataType.GoProVideo: "GV",
    CameraAndDataType.GoProImage: "GI",
    CameraAndDataType.iPhoneVideo: "IV",
    CameraAndDataType.iPhoneImage: "II",

    # The ones used for overriding CameraTypeAbbreviation
    CameraAndDataType.CameraVideo: "CV",
    CameraAndDataType.CameraImage: "CI"
}
CameraAndDataTypeAbbreviationReverse = {
    "XX": CameraAndDataType.UNKNOWN,
    "GV": CameraAndDataType.GoProVideo,
    "GI": CameraAndDataType.GoProImage,
    "IV": CameraAndDataType.iPhoneVideo,
    "II": CameraAndDataType.iPhoneImage,

    # The ones used for overriding CameraTypeAbbreviation
    "CV": CameraAndDataType.CameraVideo,
    "CI": CameraAndDataType.CameraImage
}


# define the codex for GoPro video and image, iPhone video and image
goproVideoCodexList = ["GX", "GP"]
# at this stage, there is no codex info for GoPro image, iPhone video and image.
goproImageCodexList = ["GS"]
iphoneVideoCodexList = ["IMG"]
iphoneImageCodexList = ["IMG"]
unknownCodexList = ["XX"]

# define the file type
class FileType(Enum):
    UNKNOWN = 0
    OldVersionProcessedGoProVideo = 1

    GOPRO_VIDEO = 2
    PROCESSED_GOPRO_VIDEO = 3

    GOPRO_IMAGE = 4
    PROCESSED_GOPRO_IMAGE = 5

    GOPRO_UTILITIES = 6

    IPHONE_VIDEO = 7
    PROCESSED_IPHONE_VIDEO = 8

    IPHONE_IMAGE = 9
    PROCESSED_IPHONE_IMAGE = 10

class FileInformation:
    '''The file information class'''
    def __init__(self, filePath):
        self.filePath = filePath
        self.fileType = FileType.UNKNOWN
        self.capturedDate = "00000000"
        self.capturedTime = "000000"
        self.cameraAndDataType = CameraAndDataType.UNKNOWN
        self.cameraID = "Camera"
        self.sequenceID = "0000"
        self.chapterID = "00"
        self.codex = "XX"
    def __str__(self):
        return "File path: " + self.filePath + "\n" \
            + "File type: " + str(self.fileType) + "\n" \
            + "Captured date: " + self.capturedDate + "\n" \
            + "Captured time: " + self.capturedTime + "\n" \
            + "Camera and data type: " + str(self.cameraAndDataType) + "\n" \
            + "Camera ID: " + self.cameraID + "\n" \
            + "Sequence ID: " + self.sequenceID + "\n" \
            + "Chapter ID: " + self.chapterID + "\n" \
            + "Codex: " + self.codex + "\n"

# ==================== Functions to get the file information ====================

def getFileInformation(
        filePath,
        defaultGoproCameraID: str = "11Mini", 
        defaultIphoneCameraID: str = "iPhone13") -> FileInformation:
    '''Get file information. Return a FileInformation object.
    if overrideCameraID is not set, other informaiton will be ignored.'''
    fileInformation = FileInformation(filePath)

    filenameWithExtension = os.path.basename(filePath)
    filenameWithoutExtension = os.path.splitext(filenameWithExtension)[0]

    fileInformation.fileType = evaluateFileType(filePath)

    if (fileInformation.fileType == FileType.UNKNOWN 
        or fileInformation.fileType == FileType.GOPRO_UTILITIES):
        return fileInformation

    if isFileProcessed(filePath):
        # a processed file name is in the format of
        # YYYYMMDD_HHMMSS_XY_DDDDD_CCCC_BB_AA.*
        # Date_Time_CameraAndDataType_CameraID_SequenceID_ChapterID_Codex.*
        filenameParts = re.split("_", filenameWithoutExtension)
        fileInformation.cameraAndDataType = CameraAndDataTypeAbbreviationReverse[filenameParts[2]]
        fileInformation.cameraID = filenameParts[3]
        fileInformation.sequenceID = filenameParts[4]
        fileInformation.chapterID = filenameParts[5]
        fileInformation.codex = filenameParts[6]
    else:
        # The captured date and time only need for generating formatted filename.
        try:
            fileInformation.capturedDate, fileInformation.capturedTime = getVideoCapturedDateAndTime(filePath)
        except:
            fileInformation.capturedDate, fileInformation.capturedTime = getModifiedDateAndTime(filePath)

        # need to find a way to figure out the cameraType and cameraID here
        # For instance, use the "where from" info for iPhone images
        if isGoProVideoFile(filePath):
            # a GoPro video file name is in the format of AABBCCCC.MP4
            fileInformation.cameraAndDataType = CameraAndDataType.GoProVideo

            fileInformation.codex = filenameWithoutExtension[0:2]
            fileInformation.sequenceID = filenameWithoutExtension[4:8]
            fileInformation.chapterID = filenameWithoutExtension[2:4]
            fileInformation.cameraID = defaultGoproCameraID
        elif isGoProImageFile(filePath):
            # a GoPro image file name is in the format of GS_xxxx.JPG, GS_xxxx.PNG
            fileInformation.cameraAndDataType = CameraAndDataType.GoProImage
            fileInformation.codex = filenameWithoutExtension[0:2]
            fileInformation.sequenceID = filenameWithoutExtension[3:7]
            fileInformation.cameraID = defaultGoproCameraID
        elif isIphoneVideoFile(filePath):
            # an iPhone video file name is in the format of IMG_xxxx.MOV
            fileInformation.cameraAndDataType = CameraAndDataType.iPhoneVideo
            fileInformation.codex = filenameWithoutExtension[0:3]
            fileInformation.sequenceID = filenameWithoutExtension[4:8]
            fileInformation.cameraID = defaultIphoneCameraID
        elif isIphoneImageFile(filePath):
            # an iPhone image file name is in the format of IMG_xxxx.JPG, IMG_xxxx.HEIC
            fileInformation.cameraAndDataType = CameraAndDataType.iPhoneImage
            fileInformation.codex = filenameWithoutExtension[0:3]
            fileInformation.sequenceID = filenameWithoutExtension[4:8]
            fileInformation.cameraID = defaultIphoneCameraID
        else:
            fileInformation.cameraAndDataType = CameraAndDataType.UNKNOWN
    return fileInformation
    
def evaluateFileType(filePath):
    '''evaluate the file type based on the file name and the file content'''
    # The targeted file name format is 
    # YYYYMMDD_HHMMSS_XY_DDDDD_CCCC_BB_AA.*
    # Date_Time_CameraAndDataType_CameraID_SequenceID_ChapterID_Codex.*,
    if isFileProcessed(filePath):
        filenameWithExtension = os.path.basename(filePath)
        filenameWithoutExtension = os.path.splitext(filenameWithExtension)[0]
        filenameParts = re.split("_", filenameWithoutExtension)
        if filenameParts[2] == CameraAndDataTypeAbbreviation[CameraAndDataType.GoProVideo]:
            return FileType.PROCESSED_GOPRO_VIDEO
        elif filenameParts[2] == CameraAndDataTypeAbbreviation[CameraAndDataType.GoProImage]:
            return FileType.PROCESSED_GOPRO_IMAGE
        elif filenameParts[2] == CameraAndDataTypeAbbreviation[CameraAndDataType.iPhoneVideo]:
            return FileType.PROCESSED_IPHONE_VIDEO
        elif filenameParts[2] == CameraAndDataTypeAbbreviation[CameraAndDataType.iPhoneImage]:
            return FileType.PROCESSED_IPHONE_IMAGE
    else:
        if isGoProVideoFile(filePath):
            return FileType.GOPRO_VIDEO
        elif isGoProImageFile(filePath):
            return FileType.GOPRO_IMAGE
        elif isIphoneVideoFile(filePath):
            return FileType.IPHONE_VIDEO
        elif isIphoneImageFile(filePath):
            return FileType.IPHONE_IMAGE
        elif isGoProUtilityFile(filePath):
            return FileType.GOPRO_UTILITIES
        else:
            return FileType.UNKNOWN

def getModifiedDateAndTime(filePath):
    '''Get the modified date and time of the file. return two strings in the format of YYYYMMDD, HHMMSS'''
    # modifiedDate is the date of the file in the format of YYYYMMDD
    # modifiedTime is the time of the file in the format of HHMMSS

    # get the modified time of the file in seconds since the epoch
    fileModifiedTimeBySeconds = os.path.getmtime(filePath)
    # convert the modified time to a datetime object
    fileModifiedDateTime = datetime.datetime.fromtimestamp(fileModifiedTimeBySeconds)
    extractedDate = fileModifiedDateTime.strftime("%Y%m%d")
    extractedTime = fileModifiedDateTime.strftime("%H%M%S")
    
    # print("File name is: " + filePath)
    # print("The modified time of the file is: " + extractedDate)
    # print("The modified date of the file is: " + extractedTime)
    
    return extractedDate, extractedTime

def getVideoCapturedDateAndTime(filePath):
    '''Get the date and time when the video was created. 
    return two strings in the format of YYYYMMDD, HHMMSS'''
    # get video duration by seconds
    videoClipDurationBySeconds = getVideoDurationBySeconds(filePath)
    # get the modified time of the file in seconds since the epoch
    fileModifiedTimeBySeconds = os.path.getmtime(filePath)
    # convert the captured time to a datetime object
    videoStartFilmingDateTime = datetime.datetime.fromtimestamp(fileModifiedTimeBySeconds - videoClipDurationBySeconds)

    extractedDate = videoStartFilmingDateTime.strftime("%Y%m%d")
    extractedTime = videoStartFilmingDateTime.strftime("%H%M%S")
    return extractedDate, extractedTime


import subprocess
def getVideoDurationBySeconds(filePath):
    '''Get the duration of the video in seconds'''
    # get the duration of the video in seconds
    result = subprocess.run(['ffprobe', 
                             '-v', 
                             'error', 
                             '-show_entries', 
                             'format=duration', 
                             '-of', 
                             'default=noprint_wrappers=1:nokey=1', 
                             filePath], 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.STDOUT)
    videoClipDurationBySeconds = float(result.stdout)
    return videoClipDurationBySeconds

# from moviepy.editor import VideoFileClip
# def getVideoDurationBySeconds(filePath):
#     '''Get the duration of the video in seconds'''
#     videoClip = VideoFileClip(filePath)
#     videoClipDurationBySeconds = videoClip.duration
#     return videoClipDurationBySeconds

# ==================== Functions to check the file and type ====================

def isFileProcessedOldFormat(filePath):
    '''check if the file name is in the format of
    YYYYMMDD_DDDDD_CCCC_BB_HHMMSS_AA
    (Date_CameraID_SequenceID_ChapterID_Time_Codex)'''
    filenameWithExtension = os.path.basename(filePath)
    try:
        # try split the file name into 6 parts.
        filenameParts = re.split("_", filenameWithExtension)
        # check if the there are 6 parts
        if not len(filenameParts) == 6:
            return False
        # check if the first part is a date like YYYYMMDD
        if not filenameParts[0].isdigit() or not len(filenameParts[0]) == 8:
            return False
        # camera ID is usually customized, so it is not checked here.
        # check if the third part is a sequence number like CCCC
        if not filenameParts[2].isdigit() or not len(filenameParts[2]) == 4:
            return False
        # check if the fourth part is a chapter number like BB
        if not filenameParts[3].isdigit() or not len(filenameParts[3]) == 2:
            return False
        # check if the fifth part is a time like HHMMSS (24 hour format)
        if not filenameParts[4].isdigit() or not len(filenameParts[4]) == 6:
            return False
        # check if the sixth part is a codex in the lists.
        if not filenameParts[5] in (goproVideoCodexList 
                                    + goproImageCodexList 
                                    + iphoneVideoCodexList 
                                    + iphoneImageCodexList):
            return False
        print("The file name " + filenameWithExtension + " is possibly processed in the old format already.")
        return True
    except:
        return False

def isFileProcessed(filePath):
    '''
    check if the file name is in the format of 
    YYYYMMDD_HHMMSS_XY_DDDDD_CCCC_BB_AA
    (Date_Time_CameraAndDataType_CameraID_SequenceID_ChapterID_Codex).* 
    '''
    filenameWithExtension = os.path.basename(filePath)
    # get the file without extension
    filenameWithoutExtension = os.path.splitext(filenameWithExtension)[0]
    try:
        # try split the file name into 7 parts.
        filenameParts = re.split("_", filenameWithoutExtension)
        # check if the there are 7 parts
        if not len(filenameParts) == 7:
            return False
        # check if the first part is a date like YYYYMMDD
        if not filenameParts[0].isdigit() or not len(filenameParts[0]) == 8:
            return False
        # check if the second part is a time like HHMMSS (24 hour format)
        if not filenameParts[1].isdigit() or not len(filenameParts[1]) == 6:
            return False
        # check if the third part is a camera and data type abbreviation
        if not filenameParts[2] in CameraAndDataTypeAbbreviation.values():
            return False
        # Considering camera ID is very likely to be customized, so it is not checked here.
        # check if the fifth part is a sequence number like CCCC
        if not filenameParts[4].isdigit() or not len(filenameParts[4]) == 4:
            return False
        # check if the sixth part is a chapter number like BB
        if not filenameParts[5].isdigit() or not len(filenameParts[5]) == 2:
            return False
        # check if the seventh part is a codex in the lists.
        if not filenameParts[6] in (goproVideoCodexList 
                                    + goproImageCodexList 
                                    + iphoneVideoCodexList 
                                    + iphoneImageCodexList):
            return False
        print("The file name " + filenameWithExtension + " is possibly processed already.")
        return True
    except:
        return False

def isGoProVideoFile(filePath):
    '''check if the file name is in the format of AABBCCCC.MP4, 
    which is the GoPro video file name format.'''
    # There is supposed to be a better way to check if the file is from GoPro.
    filenameWithExtension = os.path.basename(filePath)
    filenameWithoutExtension = os.path.splitext(filenameWithExtension)[0]
    fileExtension = os.path.splitext(filenameWithExtension)[1]
    if len(filenameWithoutExtension) != 8:
        return False
    # check if the first two characters are the codex
    if not filenameWithoutExtension[0:2] in goproVideoCodexList:
        return False
    # check if the next four characters are the sequence number
    if not filenameWithoutExtension[2:6].isdigit():
        return False
    # check if the last two characters are the chapter number
    if not filenameWithoutExtension[6:8].isdigit():
        return False
    # check if the file extension is in the goproVideoFileExtensionList
    if not fileExtension.upper() in goproVideoFileExtensionList:    
        return False
    if DEBUG:
        print("The file name " + filenameWithExtension + " is most likely a GoPro video file name.")
    return True

def isGoProImageFile(filePath):
    '''check if the file name is in the format of GS_xxxx.JPG, GS_xxxx.PNG'''
    # There is supposed to be a better way to check if the file is from GoPro.
    filenameWithExtension = os.path.basename(filePath)
    filenameWithoutExtension = os.path.splitext(filenameWithExtension)[0]
    fileExtension = os.path.splitext(filenameWithExtension)[1]
    if len(filenameWithoutExtension) != 7:
        return False
    # check if it can be split into two parts by "_"
    try:
        filenameParts = re.split("_", filenameWithoutExtension)
        # check if the first part is GS
        if not filenameParts[0] in goproImageCodexList:
            return False
        # check if the second part is a sequence number
        if not (filenameParts[1].isdigit() and len(filenameParts[1]) == 4):
            return False
        # check if the file extension is in the goproImageFileExtensionList
        if not fileExtension.upper() in goproImageFileExtensionList:    
            return False
        if DEBUG:
            print("The file name " + filenameWithExtension + " is most likely a GoPro regular image file name.")
        return True
    except:
        return False

def isGoProUtilityFile(filePath):
    '''check if the filename extension is in the goproUtilityFileExtensionList'''
    filenameWithExtension = os.path.basename(filePath)
    if os.path.splitext(filenameWithExtension)[1].upper() in goproUtilityFileExtensionList:
        if DEBUG:
            print("The file " + filenameWithExtension + " is most likely a GoPro utility file.")
        return True

def isIphoneVideoFile(filePath):
    '''check if the file name is in the format of IMG_xxxx.MOV'''
    # There is supposed to be a better way to check if the file is from iPhone.
    filenameWithExtension = os.path.basename(filePath)
    filenameWithoutExtension = os.path.splitext(filenameWithExtension)[0]
    fileExtension = os.path.splitext(filenameWithExtension)[1]
    if len(filenameWithoutExtension) != 8:
        return False
    # check if it can be split into two parts by "_"
    try:
        filenameParts = re.split("_", filenameWithoutExtension)
        # check if the first part is IMG
        if not filenameParts[0] == "IMG":
            return False
        # check if the second part is a sequence number
        if not (filenameParts[1].isdigit() and len(filenameParts[1]) == 4):
            return False
        # check if the file extension is in the iphoneVideoFileExtensionList
        if not fileExtension.upper() in iphoneVideoFileExtensionList:    
            return False
        if DEBUG:
            print("The file name " + filenameWithExtension + " is most likely an iPhone video file name.")
        return True
    except:
        return False 

def isIphoneImageFile(filePath):
    '''check if the file name is in the format of IMG_xxxx.JPG, IMG_xxxx.HEIC'''
    # There is supposed to be a better way to check if the file is from iPhone.
    filenameWithExtension = os.path.basename(filePath)
    filenameWithoutExtension = os.path.splitext(filenameWithExtension)[0]
    fileExtension = os.path.splitext(filenameWithExtension)[1]
    if len(filenameWithoutExtension) != 8:
        return False
    # check if it can be split into two parts by "_"
    try:
        filenameParts = re.split("_", filenameWithoutExtension)
        # check if the first part is IMG
        if not filenameParts[0] == "IMG":
            return False
        # check if the second part is a sequence number
        if not (filenameParts[1].isdigit() and len(filenameParts[1]) == 4):
            return False
        # check if the file extension is in the iphoneImageFileExtensionList
        if not fileExtension.upper() in iphoneImageFileExtensionList:    
            return False
        if DEBUG:
            print("The file name " + filenameWithExtension + " is most likely an iPhone image file name.")
        return True
    except:
        return False   



# ==================== More general functions ====================
def isThereSubFolder(folderPath):
    '''check if there is any sub folder in the folder'''
    for filename in os.listdir(folderPath):
        if os.path.isdir(os.path.join(folderPath, filename)):
            return True
    return False

def isAirdropSubFolder(folderPath):
    '''check if the folder is an airdrop sub folder, which contains only one file sharing the same name (without extension) with the folder.'''
    # check if the folder only contains one file
    if len(os.listdir(folderPath)) == 1:
        # check if the file name is the same with the folder name
        if os.path.basename(folderPath) == os.path.splitext(os.listdir(folderPath)[0])[0]:
            return True
    return False

def isThereAirdropSubFolder(folderPath):
    '''check if there is any airdrop sub folder in the folder'''
    for filename in os.listdir(folderPath):
        if os.path.isdir(os.path.join(folderPath, filename)):
            if isAirdropSubFolder(os.path.join(folderPath, filename)):
                return True
    return False

def getSubFolderListAsAirdropSubFolderListAndOtherSubFolderList(folderPath):
    '''get the sub folder list in the folder, and divide them into two lists, airdrop sub folders and other sub folders.'''
    airdropSubFolderList = []
    otherSubFolderList = []
    for filename in os.listdir(folderPath):
        if os.path.isdir(os.path.join(folderPath, filename)):
            if isAirdropSubFolder(os.path.join(folderPath, filename)):
                airdropSubFolderList.append(filename)
            else:
                otherSubFolderList.append(filename)
    return airdropSubFolderList, otherSubFolderList

def getSubFolderList(folderPath):
    '''get the sub folder list in the folder.'''
    subFolderList = []
    for filename in os.listdir(folderPath):
        if os.path.isdir(os.path.join(folderPath, filename)):
            subFolderList.append(filename)
    return subFolderList

def mergeAirdropSubFolders(sourceFolderPath, destinationFolderPath = None):
    '''Move the content of the airdrop subfolders of the source folder to the destination folder, and delete the sub folders.'''
    destinationFolderPath = sourceFolderPath if destinationFolderPath is None else destinationFolderPath
    # get the sub folder list
    airdropSubFolderList, otherSubFolderList = getSubFolderListAsAirdropSubFolderListAndOtherSubFolderList(sourceFolderPath)
    # move the content of the airdrop sub folder to the destination folder
    for subFolderName in airdropSubFolderList:
        subFolderPath = os.path.join(sourceFolderPath, subFolderName)
        for filename in os.listdir(subFolderPath):
            shutil.move(os.path.join(subFolderPath, filename), os.path.join(destinationFolderPath, filename))
        # delete the sub folder
        os.rmdir(subFolderPath)

def mergeSubFolders(sourceFolderPath, destinationFolderPath = None):
    '''Move the content of the subfolders of the source folder to the destination folder, and delete the sub folders.'''
    destinationFolderPath = sourceFolderPath if destinationFolderPath is None else destinationFolderPath
    # get the sub folder list
    subFolderList = getSubFolderList(sourceFolderPath)
    # move the content of the sub folder to the destination folder
    for subFolderName in subFolderList:
        subFolderPath = os.path.join(sourceFolderPath, subFolderName)
        for filename in os.listdir(subFolderPath):
            shutil.move(os.path.join(subFolderPath, filename), os.path.join(destinationFolderPath, filename))
        # delete the sub folder
        os.rmdir(subFolderPath)


def getFilenameListExcludingFileExtension(folderPath, fileExtension, isCaseSensitive = False):
    ''' Get the file name list in the folder, excluding the file extension.'''
    filenameList = []
    if isCaseSensitive:
        for filename in os.listdir(folderPath):
            if not filename.endswith(fileExtension):
                filenameList.append(filename)
    else:
        for filename in os.listdir(folderPath):
            if not filename.lower().endswith(fileExtension.lower()):
                filenameList.append(filename)
    return filenameList

def getFilePathListExcludingFileExtension(folderPath, fileExtension, isCaseSensitive = False):
    '''get the file path list in the folder, excluding the file extension.'''
    filePathList = []
    if isCaseSensitive:
        for filename in os.listdir(folderPath):
            if not filename.endswith(fileExtension):
                filePathList.append(os.path.join(folderPath, filename))
    else:
        for filename in os.listdir(folderPath):
            if not filename.lower().endswith(fileExtension.lower()):
                filePathList.append(os.path.join(folderPath, filename))
    return filePathList

def getFilenameListByFileExtension(folderPath, fileExtension, isCaseSensitive = False):
    ''' Get the file name list in the folder, with the file extension.'''
    filenameList = []
    if isCaseSensitive:
        for filename in os.listdir(folderPath):
            if filename.endswith(fileExtension):
                filenameList.append(filename)
    else:
        for filename in os.listdir(folderPath):
            if filename.lower().endswith(fileExtension.lower()):
                filenameList.append(filename)
    return filenameList

def getFilePathListByFileExtension(folderPath, fileExtension, isCaseSensitive = False):
    '''get the file path list in the folder, with the file extension.'''
    filePathList = []
    if isCaseSensitive:
        for filename in os.listdir(folderPath):
            if filename.endswith(fileExtension):
                filePathList.append(os.path.join(folderPath, filename))
    else:
        for filename in os.listdir(folderPath):
            if filename.lower().endswith(fileExtension.lower()):
                filePathList.append(os.path.join(folderPath, filename))
    return filePathList

def deleteFileByExtension(folderPath, fileExtension):
    # Delete all files in the folder with the specified file extension.
    fileNameList = getFilenameListByFileExtension(folderPath, fileExtension)
    for fileName in fileNameList:
        print("Deleting " + fileName)
        os.remove(os.path.join(folderPath, fileName))


def deleteGoproTrashFiles(folderPath):
    #remove all files with the extension of .THM or .LRV
    deleteFileByExtension(folderPath, ".THM")
    deleteFileByExtension(folderPath, ".LRV")


# ==================== Key functions ====================

def getFormattedFilename(fileInformation: FileInformation, 
                         overrideCameraTypeAbbreviation = None,
                         overrideCameraID = None):
    '''Get the formatted file name based on the file information'''
    # get the extension of the file
    # if the file is a 
    # GoPro video file, GoPro image file, iPhone video file or iPhone image file, 
    # make a formatted filename
    if fileInformation.fileType == FileType.GOPRO_VIDEO \
        or fileInformation.fileType == FileType.GOPRO_IMAGE \
        or fileInformation.fileType == FileType.IPHONE_VIDEO \
        or fileInformation.fileType == FileType.IPHONE_IMAGE:

        if overrideCameraTypeAbbreviation:
            cameraTypeAbbreviation = overrideCameraTypeAbbreviation
        else:
            cameraTypeAbbreviation = CameraAndDataTypeAbbreviation[fileInformation.cameraAndDataType]
        if overrideCameraID:
            cameraID = overrideCameraID
        else:
            cameraID = fileInformation.cameraID

        fileExtension = os.path.splitext(fileInformation.filePath)[1]
        formattedFilenameWithExtension = fileInformation.capturedDate + "_" \
            + fileInformation.capturedTime + "_" \
            + cameraTypeAbbreviation + "_" \
            + cameraID + "_" \
            + fileInformation.sequenceID + "_" \
            + fileInformation.chapterID + "_" \
            + fileInformation.codex + fileExtension
    else:
        formattedFilenameWithExtension = None
        print("Error while trying to get the formatted file name for " \
              + fileInformation.filePath + ".")
        print("The file type is not supported.")
    return formattedFilenameWithExtension

def getOriginalName(fileInformation):
    '''Get the original name of the file based on the file information'''
    # get the extension of the file
    fileExtension = os.path.splitext(fileInformation.filePath)[1]
    
    if fileInformation.fileType == FileType.PROCESSED_GOPRO_VIDEO: # AABBCCCC.MP4
        originalNameWithExtension = fileInformation.codex \
                                    + fileInformation.sequenceID \
                                    + fileInformation.chapterID \
                                    + fileExtension
    elif fileInformation.fileType == FileType.PROCESSED_GOPRO_IMAGE: # GS_xxxx.JPG, GS_xxxx.PNG
        originalNameWithExtension = fileInformation.codex \
                                    + "_" + fileInformation.sequenceID \
                                    + fileExtension
    elif fileInformation.fileType == FileType.PROCESSED_IPHONE_VIDEO: # IMG_xxxx.MOV
        originalNameWithExtension = fileInformation.codex + "_" \
                                    + fileInformation.sequenceID \
                                    + fileExtension
    elif fileInformation.fileType == FileType.PROCESSED_IPHONE_IMAGE: # IMG_xxxx.JPG, IMG_xxxx.HEIC
        originalNameWithExtension = fileInformation.codex + "_" \
                                    + fileInformation.sequenceID \
                                    + fileExtension
    else:
        originalNameWithExtension = None
        print("Error while trying to get the original file name for " \
              + fileInformation.filePath + ".")
        print("The file type is not supported.")
    return originalNameWithExtension

# ==================== Functions to rename the file ====================

def checkFilesInFolder(folderPath, printDetailedList = False):
    '''check the files in the folder and print the file type'''
    # if a gopro video group is found, it is added to the dictionary, 
    # sequence number as key, chapter number as value list.
    goproVideoGroupDict = {}

    # count the number of different files in the folder
    goproVideoFileCount = 0
    goproImageFileCount = 0
    goproUtilityFileCount = 0

    iphoneVideoFileCount = 0
    iphoneImageFileCount = 0
    
    unknownFileCount = 0

    unknownFileList = []

    for filename in os.listdir(folderPath):
        filePath = os.path.join(folderPath, filename)

        fileType = evaluateFileType(filePath)
        
        if fileType == FileType.GOPRO_VIDEO:
            goproVideoFileCount += 1
            # a GoPro video file name is in the format of AABBCCCC.MP4
            filenameWithoutExtension = os.path.splitext(filename)[0]
            codex = filenameWithoutExtension[0:2]
            sequenceID = filenameWithoutExtension[2:6]
            chapterID = filenameWithoutExtension[6:8]
            if sequenceID in goproVideoGroupDict:
                goproVideoGroupDict[sequenceID].append(chapterID)
            else:
                goproVideoGroupDict[sequenceID] = [chapterID]
        elif fileType == FileType.GOPRO_IMAGE:
            goproImageFileCount += 1
        elif fileType == FileType.GOPRO_UTILITIES:
            goproUtilityFileCount += 1
        elif fileType == FileType.IPHONE_VIDEO:
            iphoneVideoFileCount += 1
        elif fileType == FileType.IPHONE_IMAGE:
            iphoneImageFileCount += 1
        else:
            unknownFileCount += 1
            unknownFileList.append(filename)
    # remove the goproVideoGroupDict elements if its chapterID list lens is 1
    for sequenceID in list(goproVideoGroupDict):
        if len(goproVideoGroupDict[sequenceID]) == 1:
            del goproVideoGroupDict[sequenceID]
        else:
            goproVideoGroupDict[sequenceID].sort()

    # print the file type count
    print("The file checking result in the folder " + folderPath + ":")

    print("GoPro video file count: " + str(goproVideoFileCount))
    # if there are gopro video groups, print the gopro video group info
    if len(goproVideoGroupDict) > 0:
        print("GoPro video group count: " + str(len(goproVideoGroupDict)))
        if printDetailedList:
            for sequenceID in goproVideoGroupDict:
                print("Sequence ID: " + sequenceID)
                print("Chapter ID list: " + str(goproVideoGroupDict[sequenceID]))
    print("GoPro image file count: " + str(goproImageFileCount))
    print("GoPro utility file count: " + str(goproUtilityFileCount))
    print("iPhone video file count: " + str(iphoneVideoFileCount))
    print("iPhone image file count: " + str(iphoneImageFileCount))
    print("Unknown file count: " + str(unknownFileCount))
    print("Unknown file list: \n" + str(unknownFileList))


def renameFileToFormattedFilename(filePath,
                                  overrideCameraTypeAbbreviation = None,
                                  overrideCameraID = None,
                                  defaultGoproCameraID = "11Mini",
                                  defaultIphoneCameraID = "iPhone13"):
    '''rename the file to a formatted file name based on the file information'''
    # get the file information


    fileInformation = getFileInformation(filePath,
                                         defaultGoproCameraID,
                                         defaultIphoneCameraID)
    # get the formatted file name
    formattedFilenameWithExtension = getFormattedFilename(fileInformation, 
                                                          overrideCameraTypeAbbreviation,
                                                          overrideCameraID)    
    # rename the file
    if formattedFilenameWithExtension:
        try:
            os.rename(filePath, os.path.join(os.path.dirname(filePath), formattedFilenameWithExtension))
            if DEBUG:
                print("The file " + filePath + " is renamed to " + formattedFilenameWithExtension)
            # return the new file path
            return os.path.join(os.path.dirname(filePath), formattedFilenameWithExtension)
        except:
            print("Error while trying to rename the file " + filePath + " to " + formattedFilenameWithExtension)
    else:
        print("Error while trying to rename the file " + filePath + ".")
    return None

def renameFileToOriginalName(filePath):
    '''rename the file to the original name based on the file information'''
    # get the file information
    fileInformation = getFileInformation(filePath)
    # get the original file name
    originalNameWithExtension = getOriginalName(fileInformation)
    # rename the file
    if originalNameWithExtension:
        try:
            os.rename(filePath, os.path.join(os.path.dirname(filePath), originalNameWithExtension))
            if DEBUG:
                print("The file " + filePath + " is renamed to " + originalNameWithExtension)
            # return the new file path
            return os.path.join(os.path.dirname(filePath), originalNameWithExtension)
        except:
            print("Error while trying to rename the file " + filePath + " to " + originalNameWithExtension)
    else:
        print("Error while trying to rename the file " + filePath + ".")
    return

def renameFilesInFolderToFormattedName(sourceFolder,
                        destinationFolder,
                        overrideCameraTypeAbbreviation = None,
                        overrideCameraID = None,
                        defaultGoproCameraID = "11Mini",
                        defaultIphoneCameraID = "iPhone13"):
    '''rename the files in the folder to formatted file names'''
    if DEBUG:
        print("Start rename the video filename to the formatted name from: \n" 
            + sourceFolder + "\n to: \n" + destinationFolder)
    # get the file path list
    filePathList = getFilePathListExcludingFileExtension(sourceFolder, ".py")
    if DEBUG:
        print("The file path list is: " + str(filePathList))
    # rename the files in the folder
    for filePath in filePathList:
        if DEBUG:
            print("renameFilesInFolderToFormattedName starts renaming the file " + filePath)
        newFilePath = renameFileToFormattedFilename(filePath, 
                                                    overrideCameraTypeAbbreviation,
                                                    overrideCameraID,
                                                    defaultGoproCameraID,
                                                    defaultIphoneCameraID)
        # move the file to the destination folder
        if destinationFolder and (sourceFolder != destinationFolder):
            try:
                shutil.move(newFilePath, destinationFolder)
            except:
                print("Error while trying to move the file " + filePath + " to " + destinationFolder)

def renameFilesInFolderToOriginalName(sourceFolder,
                                      destinationFolder):
        '''rename the files in the folder to original file names'''
        # get the file path list
        filePathList = getFilePathListExcludingFileExtension(sourceFolder, ".py")
        if DEBUG:
            print("The file path list is: " + str(filePathList))
        # rename the files in the folder
        for filePath in filePathList:
            newFilePath = renameFileToOriginalName(filePath)
            # move the file to the destination folder
            if destinationFolder and (sourceFolder != destinationFolder):
                try:
                    shutil.move(newFilePath, destinationFolder)
                except:
                    print("Error while trying to move the file " + filePath + " to " + destinationFolder)
