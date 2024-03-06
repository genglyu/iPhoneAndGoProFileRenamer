# In this file, there are some general file utility functions.
# most of the functions are used to recognize the file name format
# and extract the data not shown in file names.

# GoPro video file name is in the format of CCPPSSSS.MP4

# CC is the codex of the video, usually GX or GP.
# PP is the chapter number, usually 01, possibly 02, 03 or further.
# SSSS is the sequence number, usually 0001, 0002, 0003 or further.

# the iPhone video file name is in the format of IMG_SSSS.MOV
# SSSS is the sequence number, usually 0001, 0002, 0003 or further.

# The iPhone image file name is in the format of IMG_SSSS.HEIC or IMG_SSSS.JPG
# SSSS is the sequence number, usually 0001, 0002, 0003 or further.

# The targeted file name format is 
# YYYYMMDD_HHMMSSTT_IIIII_NN_OriginalFilename.*
# Date_Time_CameraAndDataType_CameraID_UniqueID_OriginalFilename.*

DEBUG = True

from argparse import OPTIONAL
import os
import os.path
import time
import re
import datetime
import shutil
from enum import Enum
import re
import subprocess
import json

# check if ffmpeg is installed and can be used through the subprocess module
isFFmpegInstalled = False
isMoviepyInstalled = False
try:
    cmd = ['ffmpeg', '-version']
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # Check for errors
    if result.returncode != 0:
        print(f"Error running ffmpeg: {result.stderr}")
    else:
        isFFmpegInstalled = True
except Exception as e:
    print(f"Error: {e}")
    isFFmpegInstalled = False
# try to import moviepy, if failed, give a warning
if isFFmpegInstalled:
    try:
        from moviepy.editor import VideoFileClip
        isMoviepyInstalled = True
    except Exception as e:
        print(f"Error: {e}")
        isMoviepyInstalled = False
        print("Warning: moviepy is not installed. The video duration will be calculated by ffmpeg, which is not very efficient.")

# ==================== The modules are prepared ====================

# the potential file extension for the video file
videoFileExtensionList = [".MP4", ".MOV", ".MPG", ".MPEG", ".AVI", ".WMV", ".FLV", ".F4V", ".SWF", ".MKV", ".WEBM", ".HTML5"]
imageFileExtensionList = [".JPG", ".JPEG", ".PNG", ".HEIC", ".GIF", ".BMP", ".TIFF", ".TIF", ".ICO", ".CUR", ".ANI", ".WEBP", ".CR2"]
# the files might appear in the camera folder, but are not useful. Like the thumbnails, or the system files.
uselessFileExtensionList = [".THM", ".LRV" # GoPro utility files
                            # might add more in the future
                            ]
class FilenameType(Enum):
    '''The filename patterns for filenames without extensions'''

    Unknown = 0 # the file name is not recognized

    GxPPSSSS = 1 # Gopro video files: GX010001.mp4, 
                # x -> Codex, usually "H" or "X", respectively for AVC, HEVC
                # PP -> chapter number, 2 digits, from 01 to 99
                # SSSS -> sequence number, 4 digits, from 0001 to 9999
    
    IMG_SSSS = 2 # iPhone images & videos, & Canon camera images, 
                    # SSSS -> file id, 4 digits, from 0001 to 9999
    MVI_SSSS = 3 # Canon camera video, 
                    # SSSS -> file id, 4 digits, from 0001 to 9999
    DSCFSSSS = 4 # Fuji camera images & videos, 
                    # SSSS -> file id, 4 digits, from 0001 to 9999
    

    FormattedV1 = 101 # YYYYMMDD_IIIII_SSSS_PP_HHMMSS_CC, in which
                        # YYYYMMDD -> date, 8 digits, YYYY -> year (0000 to 9999), MM -> month (01 to 12), DD -> day (01 to 31), 
                        # IIIII -> cameraID, string of any length, might contain letters and digits, uppercase and lowercase can be mixed.
                        # SSSS -> sequence number, 4 digits, from 0001 to 9999
                        # PP -> chapter number, 2 digits, from 00 to 99
                        # HHMMSS -> time, 6 digits, HH -> hour (00 to 23), MM -> minute (00 to 59), SS -> second (00 to 59)
                        # CC -> the codex, 2 captial letters, "GX" or "GH".
    
    FormattedV2 = 102 # YYYYMMDD_HHMMSS_XY_IIIII_SSSS_PP_CC, in which
                        # YYYYMMDD -> date, 8 digits, YYYY -> year (0000 to 9999), MM -> month (01 to 12), DD -> day (01 to 31),
                        # HHMMSSTT -> time, 8 digits, HH -> hour (00 to 23), MM -> minute (00 to 59), SS -> second (00 to 59), TT -> millisecond (00 to 99)
                        # XY -> camera and data type, 2 letters, "GV" for GoPro video, "GI" for GoPro image, "IV" for iPhone video, "II" for iPhone image, "CV" for camera video, "CI" for camera image.
                        # IIIII -> cameraID, string of any length, might contain letters and digits, uppercase and lowercase can be mixed.
                        # SSSS -> sequence number, 4 digits, from 0001 to 9999
                        # PP -> chapter number, 2 digits, from 00 to 99
                        # CC -> the codex, 2 or 3 captial letters, "GX" or "GH" for GoPro video, "GS" for GoPro image, "IMG" for iPhone video and image (might also be Canon images), "MVI" for Canon camera video, "DSCF" for Fuji camera video and image.

    FormattedV3 = 103 # YYYYMMDD_HHMMSSTT_IIIII(?:_NN)(OriginalFilenameWithoutExtension), in which
                        # YYYYMMDD -> date, 8 digits, YYYY -> year (0000 to 9999), MM -> month (01 to 12), DD -> day (01 to 31)，
                        # HHMMSSTT -> time, 8 digits, HH -> hour (00 to 23), MM -> minute (00 to 59), SS -> second (00 to 59), TT -> time less than one second，
                        # IIIII -> cameraID, string of any length, might contain letters and digits, uppercase and lowercase can be mixed
                        # NN -> unique ID, 2 digits, from 01 to 99, used to distinguish files with the same date and time，
                        # OriginalFilename -> the original file name, string of any length.
    FormattedV4 = 104 # YYYYMMDD_HHMMSSTT_IIIII(?:_NN)-OriginalFilenameWithoutExtension, in which
                        # Everything is the same with FormattedV3, except that the OriginalFilename is separated by a dash "-".
                        # The reason is that
                        # YYYYMMDD -> date, 8 digits, YYYY -> year (0000 to 9999), MM -> month (01 to 12), DD -> day (01 to 31)，
                        # HHMMSSTT -> time, 8 digits, HH -> hour (00 to 23), MM -> minute (00 to 59), SS -> second (00 to 59), TT -> time less than one second，
                        # IIIII -> cameraID, string of any length, might contain letters and digits, uppercase and lowercase can be mixed
                        # NN -> unique ID, 2 digits, from 01 to 99, used to distinguish files with the same date and time，
                        # OriginalFilename -> the original file name, string of any length.
    V3FromGoproMediaLib = 1003 # YYYYMMDD_HHMMSSTT_IIIII(?:_NN)_OriginalFilenameWithoutExtension_
                        # the formatted V3 files will be renamed to this format when they are imported to the GoPro Media Library, cause the "(" and ")" are replaced by "_".
                        # Sometimes, it is a potential problem when the original filename contains "_".
                        # YYYYMMDD -> date, 8 digits, YYYY -> year (0000 to 9999), MM -> month (01 to 12), DD -> day (01 to 31)，
                        # HHMMSSTT -> time, 8 digits, HH -> hour (00 to 23), MM -> minute (00 to 59), SS -> second (00 to 59), TT -> time less than one second，
                        # IIIII -> cameraID, string of any length, might contain letters and digits, uppercase and lowercase can be mixed
                        # NN -> unique ID, 2 digits, from 01 to 99, used to distinguish files with the same date and time，
                        # OriginalFilename -> the original file name, string of any length.

FilenamePattern = {
    FilenameType.GxPPSSSS: r'^G(H|X)\d{4}$',
    FilenameType.IMG_SSSS: r'^IMG_\d{4}$',
    FilenameType.MVI_SSSS: r'^MVI_\d{4}$',
    FilenameType.DSCFSSSS: r'^DSCF\d{4}$',

    FilenameType.FormattedV1: r'^([0-9]{4})(0[1-9]|1[0-2])([0-2][0-9]|3[0-1])_([a-zA-Z0-9]+)_\d{4}_([0-9]{2})_([0-1][0-9]|2[0-3])([0-5][09])([0-5][0-9])_G(H|X)$',
    FilenameType.FormattedV2: r'^([0-9]{4})(0[1-9]|1[0-2])([0-2][0-9]|3[0-1])_([0-1][0-9]|2[0-3])([0-5][0-9])([0-5][0-9])_([a-zA-Z]{2})_([a-zA-Z0-9]+)_\d{4}_([0-9]{2})_([0-1][0-9]|2[0-3])([0-5][09])([0-5][09])_(GX|GH|GS|IMG|MVI|DSCF)$',
    FilenameType.FormattedV3: r'^([0-9]{4})(0[1-9]|1[0-2])([0-2][0-9]|3[0-1])_([0-1][0-9]|2[0-3])([0-5][0-9])([0-5][0-9])([0-9]{2})_([a-zA-Z0-9]+)(_[0-9]{2})?\(([^\)]*)\)$',
    FilenameType.FormattedV4: r'^([0-9]{4})(0[1-9]|1[0-2])([0-2][0-9]|3[0-1])_([0-1][0-9]|2[0-3])([0-5][0-9])([0-5][0-9])([0-9]{2})_([a-zA-Z0-9]+)(_[0-9]{2})?-([^\)]*)$',

    FilenameType.V3FromGoproMediaLib: r'^([0-9]{4})(0[1-9]|1[0-2])([0-2][0-9]|3[0-1])_([0-1][0-9]|2[0-3])([0-5][0-9])([0-5][0-9])([0-9]{2})_([a-zA-Z0-9]+)(_[0-9]{2})?_([^\)]*)_$'
}

def validateString(pattern, testString):
    result = re.match(pattern, testString)
    return result is not None

class FileType(Enum):
    '''the data type video, image'''
    Unknown = 0
    Video = 1
    Image = 2
    KnownButUseless = 3

# ==================== Functions to get the file information ====================
def getModifiedDateAndTime(filePath):
    '''Get the modified date and time of the file. 
    Return two strings in the format of YYYYMMDD, HHMMSSTT'''
    # modifiedDate is the date of the file in the format of YYYYMMDD
    # modifiedTime is the time of the file in the format of HHMMSS

    # get the modified time of the file in seconds since the epoch
    fileModifiedTimeBySeconds = os.path.getmtime(filePath)
    # convert the modified time to a datetime object
    fileModifiedDateTime = datetime.datetime.fromtimestamp(fileModifiedTimeBySeconds)
    # extract the date in the format of YYYYMMDD
    extractedDate = fileModifiedDateTime.strftime("%Y%m%d")
    # extract the time in the format of HHMMSSTT
    extractedTime = fileModifiedDateTime.strftime("%H%M%S")
    timeLessThanOneSecond = fileModifiedTimeBySeconds % 1
    extractedTime = extractedTime + format(timeLessThanOneSecond, ".6f")[2:4]

    if DEBUG:
        print("File name is: " + filePath)
        print("The modified time of the file is: " + extractedDate)
        print("The modified date of the file is: " + extractedTime)
    return extractedDate, extractedTime

def getVideoCapturedDateAndTime(filePath):
    '''Get the date and time when the video was created. 
    Return two strings in the format of YYYYMMDD, HHMMSSTT'''
    
    videoDurationBySeconds = None
    # get video duration by seconds
    if isFFmpegInstalled:
        # get the duration of the video in seconds through ffmpeg
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
        videoDurationBySeconds = float(result.stdout)
    elif isMoviepyInstalled:
        # use moviepy to get the video duration, not very efficient
        videoDurationBySeconds = VideoFileClip(filePath).duration
    else:
        print("Error: ffmpeg and moviepy are not installed, so modified time is used instead of capture starting time.")
        videoDurationBySeconds = 0.0

    # get the modified time of the file in seconds since the epoch
    fileModifiedTimeBySeconds = os.path.getmtime(filePath)
    # get the captured time of the video in seconds since the epoch
    videoCapturedTimeBySeconds = fileModifiedTimeBySeconds - videoDurationBySeconds
    videoCapturedTimeBySecondsDecimalPart = videoCapturedTimeBySeconds % 1
    # convert the captured time to a datetime object
    videoCapturedDateTime = datetime.datetime.fromtimestamp(videoCapturedTimeBySeconds)
    # extract the date in the format of YYYYMMDD
    extractedDate = videoCapturedDateTime.strftime("%Y%m%d")
    # extract the time in the format of HHMMSSTT, in 24-hour format
    extractedTime = videoCapturedDateTime.strftime("%H%M%S") + format(videoCapturedTimeBySecondsDecimalPart, ".6f")[2:4]
    if DEBUG:
        print("File name is: " + filePath)
        print("The captured date of the video is: " + extractedTime)
        print("The captured time of the video is: " + extractedDate)
    return extractedDate, extractedTime


def getFileMetadata(filePath):
    # if the code is running on macOS, use the mdls command to get the metadata

    # if the code is running on Windows or linux, use the exiftool command to get the metadata
    try:
        cmd = ['exiftool', '-json', filePath]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # Check for errors
        if result.returncode != 0:
            print(f"Error running exiftool: {result.stderr}")
            return None
        # Parse the JSON output
        metadata = json.loads(result.stdout)
        return metadata
    except Exception as e:
        print(f"Error: {e}")
        return None

# ==================== Functions to check the file and type ====================

def isVideoFile(filePath):
    '''check if the file is a video file'''
    fileExtension = os.path.splitext(filePath)[1]
    if fileExtension.upper() in videoFileExtensionList:
        return True
    else:
        return False

def isImageFile(filePath):
    '''check if the file is an image file'''
    fileExtension = os.path.splitext(filePath)[1]
    if fileExtension.upper() in imageFileExtensionList:
        return True
    else:
        return False

def isVideoOrImageFile(filePath):
    '''check if the file is a video or image file'''
    fileExtension = os.path.splitext(filePath)[1]
    if fileExtension.upper() in videoFileExtensionList:
        return True
    elif fileExtension.upper() in imageFileExtensionList:
        return True
    else:
        return False

def isUselessFile(filePath):
    '''check if the filename extension is in the uselessFileExtensionList'''
    filenameWithExtension = os.path.basename(filePath)
    if os.path.splitext(filenameWithExtension)[1].upper() in uselessFileExtensionList:
        if DEBUG:
            print("The file " + filenameWithExtension + " is most likely a GoPro utility file.")
        return True

# ==================== More of the general functions ====================
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

def getFilePathList(folderPath):
    '''get the file path list in the folder.'''
    filePathList = []
    for filename in os.listdir(folderPath):
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

def deleteTinyFileByExtension(folderPath, fileExtension, fileMinimumSizeinMB = 1):
    # Delete all files in the folder with the specified file extension and size.
    fileNameList = getFilenameListByFileExtension(folderPath, fileExtension)
    for fileName in fileNameList:
        fileSize = os.path.getsize(os.path.join(folderPath, fileName))
        if fileSize < fileMinimumSizeinMB * 1024 * 1024:
            print("Deleting " + fileName)
            os.remove(os.path.join(folderPath, fileName))

def deleteInvisibleFile(folderPath):
    # Delete all invisible files in the folder    
    # check if the code is running on macOS or Linux
    if os.name == "posix":
        # Invisible files are the files whose name starts with "." in macOS and Linux
        for filename in os.listdir(folderPath):
            if filename.startswith("."):
                print("Deleting " + filename)
                os.remove(os.path.join(folderPath, filename))
    # check if the code is running on Windows
    elif os.name == "nt":
        # Invisible files are the files whose attribute is hidden in Windows
        for filename in os.listdir(folderPath):
            if os.path.isfile(os.path.join(folderPath, filename)):
                if bool(os.stat(os.path.join(folderPath, filename)).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN):
                    print("Deleting " + filename)
                    os.remove(os.path.join(folderPath, filename))
    else:
        print("The operating system is not recognized.")
    

def deleteTrashFiles(folderPath):
    #remove all files with the extension of .THM or .LRV
    deleteFileByExtension(folderPath, ".THM")
    deleteFileByExtension(folderPath, ".LRV")
    deleteTinyFileByExtension(folderPath, ".MP4", 1)
    deleteInvisibleFile(folderPath)

# ==================== Functions to rename the file ====================
def checkFilenameType(filenameWithoutExtension):
    '''check the filename type, return the filename type'''
    if DEBUG:
        print("Checking the filename type of " + filenameWithoutExtension + ".")
    for filenameType in FilenameType:
        if filenameType != FilenameType.Unknown:
        # check if the filename matches the pattern
            if validateString(FilenamePattern[filenameType], filenameWithoutExtension):
                return filenameType
    return FilenameType.Unknown

def getFormattedNameV4(filePath, destinationFolderPath = None, overrideCameraID = None, defaultCameraID = "Cid"):
    '''Rename the file to the formatted name in the format of YYYYMMDD_HHMMSSTT_IIIII(?:_NN)-OriginalFilename'''
    # get the file information
    filename = os.path.basename(filePath)
    filenameWithoutExtension, fileExtension = os.path.splitext(filename)
    destinationFolderPath = os.path.dirname(filePath) if destinationFolderPath is None else destinationFolderPath

    capturedDate = None
    capturedTime = None
    cameraID = None
    uniqueID = 1
    originalFilenameWithoutExtension = None

    # get the captured date and time
    if isVideoFile(filePath):
        capturedDate, capturedTime = getVideoCapturedDateAndTime(filePath)
    elif isImageFile(filePath):
        capturedDate, capturedTime = getModifiedDateAndTime(filePath)
    else:
        if DEBUG:
            print("The file is not a video or image file.")
        return None
    
    # get the filename type
    filenameType = checkFilenameType(filenameWithoutExtension)
    if filenameType == FilenameType.FormattedV1:
        # get the original filename
        originalFilenameWithoutExtension, cameraID = getOriginalFilenameFromFormattedV1(filenameWithoutExtension)
    elif filenameType == FilenameType.FormattedV2:
        # get the original filename
        originalFilenameWithoutExtension, cameraID = getOriginalFilenameFromFormattedV2(filenameWithoutExtension)
    elif filenameType == FilenameType.FormattedV3:
        # get the original filename
        originalFilenameWithoutExtension, cameraID = getOriginalFilenameFromFormattedV3(filenameWithoutExtension)
    elif filenameType == FilenameType.V3FromGoproMediaLib:
        # get the original filename
        originalFilenameWithoutExtension, cameraID = getOriginalFilenameFromFormattedV3FromGoproMediaLib(filenameWithoutExtension)
    elif filenameType == FilenameType.FormattedV4:
        # get the original filename
        originalFilenameWithoutExtension, cameraID = getOriginalFilenameFromFormattedV4(filenameWithoutExtension)
    else:
        # in this case, the original filename is the same with the filename without extension cause it is not formatted yet.
        originalFilenameWithoutExtension = filenameWithoutExtension
    
    # get the camera ID. If overrideCameraID is None, use the camera ID in the filename.
    # Potentially, we can try to figure out the camera ID from the file metadata.
    # But this is not implemented yet.
    # cameraID = getCameraIDFromMetadata(filePath)

    if overrideCameraID is None:
        if cameraID is None:
            cameraID = defaultCameraID
    else:
        cameraID = overrideCameraID
    
    # get the potential formatted filename
    potentialFormattedFilename = capturedDate + "_" + capturedTime + "_" + cameraID \
        + "-" + originalFilenameWithoutExtension + fileExtension

    # check if the potential formatted filename has a file with the same name in the destination folder
    while os.path.isfile(os.path.join(destinationFolderPath, potentialFormattedFilename)):
        # check if the file in the destination folder is the same with the file in the source folder
        if os.path.samefile(filePath, os.path.join(destinationFolderPath, potentialFormattedFilename)):
            if DEBUG:
                print("The file is the same with the file in the destination folder.")
            return None
        else:
            # if there is a file with the same name, increase the unique ID by 1
            uniqueID = uniqueID + 1
            # get a new potential formatted filename
            # if the unique ID is an integer larger than 1, add the unique ID to the filename
            if uniqueID > 1 and uniqueID % 1 == 0 and uniqueID < 100:
                potentialFormattedFilename = capturedDate + "_" + capturedTime + "_" + cameraID \
                    + "_" + str(uniqueID).zfill(2) + "-" + originalFilenameWithoutExtension + fileExtension
            else:
                if DEBUG:
                    print("The unique ID is not an integer larger than 1 and smaller than 100.")
                return None
    return potentialFormattedFilename


def getOriginalFilenameFromFormattedV1(filenameWithoutExtension):
    '''Get the original filename from the formatted name in the format of YYYYMMDD_IIIII_SSSS_PP_HHMMSS_CC.
    Will return None if the filename is not in the format of FormattedV1.
    if the filename is in the format of FormattedV1, return the original filename and the camera ID.'''
    # get the file information
    if checkFilenameType(filenameWithoutExtension) == FilenameType.FormattedV1:
        date, cameraID, sequenceNumber, chapterNumber, time, codex = filenameWithoutExtension.split("_")
        return codex+chapterNumber+sequenceNumber, cameraID
    else:
        if DEBUG:
            print("The filename (without extension) " + filenameWithoutExtension + " is not in the format of FormattedV1.")
        return None, None
    
def getOriginalFilenameFromFormattedV2(filenameWithoutExtension):
    '''Get the original filename from the formatted name in the format of YYYYMMDD_HHMMSS_XY_IIIII_SSSS_PP_CC'''
    # get the file information
    if checkFilenameType(filenameWithoutExtension) == FilenameType.FormattedV2:
        date, time, cameraAndDataType, cameraID, sequenceNumber, chapterNumber, codex = filenameWithoutExtension.split("_")
        originalFilenameWithoutExtension = None
        if cameraAndDataType == "GV":
            originalFilenameWithoutExtension = codex + chapterNumber + sequenceNumber
        elif cameraAndDataType == "GI":
            pass 
        elif (cameraAndDataType == "IV" or cameraAndDataType == "II") and codex == "IMG":
            originalFilenameWithoutExtension = "IMG_" + sequenceNumber
        elif cameraAndDataType == "CV" and codex == "MVI":
            originalFilenameWithoutExtension = "MVI_" + sequenceNumber
        elif cameraAndDataType == "CI" and codex == "DSCF":
            originalFilenameWithoutExtension = "DSCF" + sequenceNumber
        else: # unknown camera and data type
            if DEBUG:
                print("The camera and data type is unknown.")
            return None
        return originalFilenameWithoutExtension, cameraID
    else:
        if DEBUG:
            print("The filename is not in the format of FormattedV2.")
        return None, None

def getOriginalFilenameFromFormattedV3(filenameWithoutExtension):
    '''Get the original filename from the formatted name in the format of YYYYMMDD_HHMMSSTT_IIIII(_NN)?(OriginalFilenameWithoutExtension)'''
    # get the file information
    if checkFilenameType(filenameWithoutExtension) == FilenameType.FormattedV3:
        originalFilenameWithoutExtension = filenameWithoutExtension.split("(")[1]
        originalFilenameWithoutExtension = originalFilenameWithoutExtension.split(")")[0]
        cameraID = filenameWithoutExtension.split("_")[2]
        return originalFilenameWithoutExtension, cameraID
    else:
        if DEBUG:
            print("The filename is not in the format of FormattedV3.")
        return None, None

def getOriginalFilenameFromFormattedV3FromGoproMediaLib(filenameWithoutExtension):
    '''Get the original filename from the formatted name in the format of YYYYMMDD_HHMMSSTT_IIIII(_NN)?_OriginalFilenameWithoutExtension_'''
    # get the file information
    if checkFilenameType(filenameWithoutExtension) == FilenameType.V3FromGoproMediaLib:
        filenameElements = filenameWithoutExtension.split("_")
        cameraID = filenameElements[2]
        originalFilenameWithoutExtension = ""
        # remove the date, time, cameraID from the filenameElements.
        # r'^([0-9]{4})(0[1-9]|1[0-2])([0-2][0-9]|3[0-1])_([0-1][0-9]|2[0-3])([0-5][0-9])([0-5][0-9])([0-9]{2})_([a-zA-Z0-9]+)(_[0-9]{2})?-([^\)]*)$'
        filenameElements.pop(0)
        filenameElements.pop(0)
        filenameElements.pop(0)
        if re.match(r'([0-9]{2})$', filenameElements[0]) is not None:
            filenameElements.pop(0)
        if len(filenameElements) > 1:
            # assempble the original filename, with the "_" between the elements
            for element in filenameElements:
                originalFilenameWithoutExtension = originalFilenameWithoutExtension + element + "_"
            # remove the last "_", and the second last "_" introducted by the last ")".
            originalFilenameWithoutExtension = originalFilenameWithoutExtension[:-2]
        return originalFilenameWithoutExtension, cameraID
    else:
        if DEBUG:
            print("The filename is not in the format of V3FromGoproMediaLib.")
        return None, None

def getOriginalFilenameFromFormattedV4(filenameWithoutExtension):
    '''Get the original filename from the formatted name in the format of YYYYMMDD_HHMMSSTT_IIIII(_NN)?-OriginalFilenameWithoutExtension'''
    # get the file information
    if checkFilenameType(filenameWithoutExtension) == FilenameType.FormattedV4:
        cameraID = filenameWithoutExtension.split("_")[2]
        originalFilenameWithoutExtension = ""

        filenameRoughElements = filenameWithoutExtension.split("-")

        if len(filenameRoughElements) > 2:
            # in this case, the original filename is contains "-"
            for element in filenameRoughElements[2:]:
                originalFilenameWithoutExtension = originalFilenameWithoutExtension + element + "-"
            # remove the last "-"
            originalFilenameWithoutExtension = originalFilenameWithoutExtension[:-1]
        elif len(filenameRoughElements) == 2:
            # in this case, the original filename is not contains "-"
            originalFilenameWithoutExtension = filenameRoughElements[1]
        else: # len(filenameRoughElements) == 1 or 0
            # in this case, the filename does not contain "-", which means it is not formatted as formattedV4
            if DEBUG:
                print("The filename is not in the format of FormattedV4.")
            return None, None
        return originalFilenameWithoutExtension, cameraID
    else:
        if DEBUG:
            print("The filename is not in the format of FormattedV4.")
        return None, None

def renameFile(filePath, newFilename, destinationFolderPath = None):
    '''Rename the file to the new filename.'''
    destinationFolderPath = os.path.dirname(filePath) if destinationFolderPath is None else destinationFolderPath
    # check if the file exists
    if not os.path.isfile(filePath):
        if DEBUG:
            print("The file " + filePath + " does not exist.")
        return False
    # check if the new filename exists in the destination folder
    if os.path.isfile(os.path.join(destinationFolderPath, newFilename)):
        if DEBUG:
            print("The file " + newFilename + " already exists in the destination folder " + destinationFolderPath + ".")
        return False
    # rename the file
    try:
        os.rename(filePath, os.path.join(destinationFolderPath, newFilename))
        return True
    except Exception as e:
        if DEBUG:
            print("Error: " + e)
        return False

def renameMediaFilesInFolder(sourceFolder, destinationFolder = None, overrideCameraID = None, defaultCameraID = "Cid"):
    '''Process all the files in the folder'''
    destinationFolder = sourceFolder if destinationFolder is None else destinationFolder
    # get the file path list
    filePathList = getFilePathList(sourceFolder)
    # rename the files
    for filePath in filePathList:
        newFilename = None
        try:
            newFilename = getFormattedNameV4(filePath, destinationFolder, overrideCameraID, defaultCameraID)
        except Exception as e:
            if DEBUG:
                print("Error: " + e)
            continue
        if newFilename is not None:
            renameFile(filePath, newFilename, destinationFolder)
            
            if DEBUG:
                outputString = "The file " + filePath
                if newFilename != os.path.basename(filePath):
                    outputString += " is renamed to " + newFilename
                else:
                    outputString += " has the same formatted name"

                if destinationFolder == sourceFolder:
                    outputString += "."
                else:
                    outputString += ", and moved to " + destinationFolder + "."
                print(outputString)
        else:
            if DEBUG:
                print("The file " + filePath + " is not renamed or moved.")
            continue

def restoreOriginalFilenamesInFolder(sourceFolder, destinationFolder = None):
    '''Process all the files in the folder'''
    destinationFolder = sourceFolder if destinationFolder is None else destinationFolder
    # get the file path list
    filePathList = getFilePathList(sourceFolder)
    # rename the files
    for filePath in filePathList:
        filenameWithoutExtension, fileExtension = os.path.splitext(os.path.basename(filePath))
        filenameType = checkFilenameType(filenameWithoutExtension)

        if filenameType == FilenameType.FormattedV1:
            newFilename = getOriginalFilenameFromFormattedV1(filenameWithoutExtension)[0] + fileExtension
        elif filenameType == FilenameType.FormattedV2:
            newFilename = getOriginalFilenameFromFormattedV2(filenameWithoutExtension)[0] + fileExtension
        elif filenameType == FilenameType.FormattedV3:
            newFilename = getOriginalFilenameFromFormattedV3(filenameWithoutExtension)[0] + fileExtension
        elif filenameType == FilenameType.V3FromGoproMediaLib:
            newFilename = getOriginalFilenameFromFormattedV3FromGoproMediaLib(filenameWithoutExtension)[0] + fileExtension
        elif filenameType == FilenameType.FormattedV4:
            newFilename = getOriginalFilenameFromFormattedV4(filenameWithoutExtension)[0] + fileExtension

        elif filenameType == FilenameType.Unknown:
            print("The filename " + os.path.basename(filePath) + " is not recognized.")
            continue
        else: # the filename is not formatted
            print("The filename " + os.path.basename(filePath) + " is not formatted, \n but it is recognized as a " + str(filenameType) + " file.")
            continue
            
        if newFilename is not None:
            renameFile(filePath, newFilename, destinationFolder)
            if DEBUG:
                if destinationFolder == sourceFolder:
                    print("The file " + filePath + " is renamed to " + newFilename + ".")
                else:
                    print("The file " + filePath + " is renamed to " + newFilename + " and moved to " + destinationFolder + ".")
        else:
            if DEBUG:
                print("The file " + filePath + " is not renamed.")
            continue

def checkFilesInFolder(folderPath, printDetailedList = False):
    '''check the files in the folder, print the detailed list if printDetailedList is True'''
    fileTypeCountDict = {}
    for filenameType in FilenameType:
        fileTypeCountDict[filenameType] = 0

    for filenameWithExtension in os.listdir(folderPath):
        filenameWithoutExtension, fileExtension = os.path.splitext(filenameWithExtension)
        filenameType = checkFilenameType(filenameWithoutExtension)
        fileTypeCountDict[filenameType] = fileTypeCountDict[filenameType] + 1
        if printDetailedList and filenameType == FilenameType.Unknown:
            print(filenameWithExtension + " is not recognized.")
    print("The file type count in the folder is: ")
    for filenameType in FilenameType:
        print(str(filenameType) + ": " + str(fileTypeCountDict[filenameType]))


