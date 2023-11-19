import os
import os.path
import argparse

from FileUtility import *

# create an ArgumentParser object
parser = argparse.ArgumentParser()
# add an argument for the camera ID (-i or --camera-id)

parser.add_argument('-oct','--override-camera-type', help='Set the camera type brutally, ignoring other information', default = None)
parser.add_argument('-oci','--override-camera-id', help='Set the camera ID brutally, ignoring other information', default = None)

parser.add_argument('-ii','--set-iPhone-id', help='Set iPhone camera ID.', default = "iPhone13")
parser.add_argument('-gi','--set-GoPro-id', help='Set GoPro camera ID.', default = "11Mini")

parser.add_argument('-s','--source-folder', help='Set the source folder. If not set, the default is current folder', default = None)
parser.add_argument('-d','--destination-folder', help='Set the destination folder. If not set, it will be the same with the source folder', default = None)

parser.add_argument('-r','-recover','--recover-original-filenames', action='store_true', help='Reset the file names to original', default=False)

parser.add_argument('-l','-list','--list-files', action='store_true', help='List the files in the folder', default=False)

parser.add_argument('-p', '--process', action='store_true', help='Process the files in the folder', default=False)

# parse the command-line arguments
args = parser.parse_args()
overrideCameraType = args.override_camera_type

overrideCameraID = args.override_camera_id
goproCameraID = args.set_GoPro_id
iphoneCameraID = args.set_iPhone_id

sourceFolder = None
destinationFolder = None

if args.source_folder is None:
    sourceFolder = os.getcwd()
else:
    sourceFolder = args.source_folder

if args.destination_folder is None:
    destinationFolder = sourceFolder
else:
    destinationFolder = args.destination_folder

print("Processing started...")
print("Source folder: " + sourceFolder)
print("Destination folder: " + destinationFolder)

if args.list_files:
    checkFilesInFolder(sourceFolder, printDetailedList=True)

if args.recover_original_filenames:
    # reset the file name to the original name in the folder
    print("Start recover the video filename to the original name from: /n"
          + sourceFolder + "/n to: /n" + destinationFolder)
    renameFilesInFolderToOriginalName(sourceFolder, destinationFolder)
elif args.process:
    deleteGoproTrashFiles(sourceFolder)
    # rename the video file name to the formatted name in the folder
    print("Start rename the video filename to the formatted name from: /n" 
          + sourceFolder + "/n to: /n" + destinationFolder)
    renameFilesInFolderToFormattedName(sourceFolder, destinationFolder, 
                                       overrideCameraType, overrideCameraID, 
                                       goproCameraID, iphoneCameraID)
    