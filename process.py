import os
import os.path
import GoProVideoFileNameModifier
import argparse

# create an ArgumentParser object
parser = argparse.ArgumentParser()
# add an argument for the camera ID (-i or --camera-id)
parser.add_argument('-i', '--camera-id', help='Set camera ID in file name, default is Gopro', default='Gopro')
parser.add_argument('-rc', '--replace-camera-id', nargs=2, help='Replace cameraID in file name. Format: -rc oldCameraID newCameraID')
parser.add_argument('-reset', '--reset-gopro', action='store_true', help='Reset the file names to Gopro file style')

# parse the command-line arguments
args = parser.parse_args()
# get the camera ID as a string
cameraID = args.camera_id

if args.reset_gopro:
    # reset the video file name to the original name in the folder
    print("Start resetting the video file name to the original name in the folder.")
    folderPath = os.getcwd()
    GoProVideoFileNameModifier.resetVideoFileNameToOriginalNameInFolder(folderPath)
elif args.replace_camera_id:
    # replace the old camera ID in all file names in the current folder with the new camera ID
    print("Start replacing the old camera ID in all file names in the current folder with the new camera ID.")
    oldCameraID = args.replace_camera_id[0]
    newCameraID = args.replace_camera_id[1]
    GoProVideoFileNameModifier.replaceAllCameraIDInFileNameInCurrentFolder(oldCameraID, newCameraID)
else:
    # Rename MP4 files in the current folder
    folderPath = os.getcwd()
    fileExtension = ".MP4"
    GoProVideoFileNameModifier.renameAllFilesInFolderFromGoProFormatToCustom(folderPath, fileExtension, cameraID)
    # Remove all .THM and .LRV files in the current folder
    GoProVideoFileNameModifier.deleteTrashFiles(folderPath)
    
