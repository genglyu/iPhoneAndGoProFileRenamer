# GoProFileProcessingScript

Need to move the script to the same folder with the files to work.

Runing generateTestingFiles.py would make 30 empty files with GoPro format file name.

Runing cleaningTestingFiles.py would delete all go pro files.

Runing process.py would convert the file names from AABBCCCC.MP4 to Date_CameraID_CCCC_BB_Time_AA.MP4 style.

Usage:

```Bash
python process.py -i CameraID
```

Convert Gopro Style file name to the new format, and delete the LRV/THM files.

```Bash
python process.py -rc oldCameraID newCameraID
```
Rep
lace the cameraID for converted file names.


```Bash
python process.py -reset
```

go back to goPro style file names.
