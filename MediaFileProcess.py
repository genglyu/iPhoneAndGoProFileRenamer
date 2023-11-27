import os
import os.path
import argparse

from FileUtility import *

# create an ArgumentParser object
parser = argparse.ArgumentParser()
# add an argument for the camera ID (-i or --camera-id)
parser.add_argument('-oci','--override-camera-id', help='Set the camera ID brutally, ignoring other information. \n This is a dangerous action, be sure you know what you are doing.', default = None)

parser.add_argument('-s','--source-folder', help='Set the source folder. If not set, the default is current folder', default = None)
parser.add_argument('-d','--destination-folder', help='Set the destination folder. If not set, it will be the same with the source folder', default = None)

parser.add_argument('-r','-recover','--recover-original-filenames', action='store_true', help='Reset the file names to original', default=False)

parser.add_argument('-l','-list','--list-files', action='store_true', help='List the files in the folder', default=False)

parser.add_argument('-p', '--process', action='store_true', help='Process the files in the folder', default=False)

parser.add_argument('-m', '--merge-airdrop-sub-folders', action='store_true', help='Merge the sub-folders generated by Airdrop in the folder', default=False)
parser.add_argument("-mf", "--merge-sub-folders", action='store_true', help="Merge all the sub-folders in the folder", default=False)
# parse the command-line arguments
args = parser.parse_args()
overrideCameraID = args.override_camera_id

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

if args.merge_airdrop_sub_folders:
    if isThereAirdropSubFolder(sourceFolder):
        print("Start merging the Airdrop subfolders in the folder: " + sourceFolder)
        mergeAirdropSubFolders(sourceFolder, destinationFolder)
        sourceFolder = destinationFolder
if args.merge_sub_folders:
    if isThereSubFolder(sourceFolder):
        print("Start merging all the subfolders in the folder: " + sourceFolder)
        mergeSubFolders(sourceFolder, destinationFolder)
        sourceFolder = destinationFolder

if args.recover_original_filenames:
    # reset the file name to the original name in the folder
    print("Start recover the video filename to the original name from: \n"
          + sourceFolder + "\n to: \n" + destinationFolder)
    restoreOriginalFilenamesInFolder(sourceFolder, destinationFolder)
elif args.process:
    deleteGoproTrashFiles(sourceFolder)
    # rename the video file name to the formatted name in the folder
    print("Start rename the video filename to the formatted name from: \n" 
          + sourceFolder + "\n to: \n" + destinationFolder)
    renameMediaFilesInFolder(sourceFolder, 
                             destinationFolder, 
                             overrideCameraID, 
                             defaultCameraID="Cid")    