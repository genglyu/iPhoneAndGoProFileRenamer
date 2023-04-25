# GoProFileProcessingScript

Need to move the script to the same folder with the files to work.

Runing
```Bash
python generateTestingFiles.py
```
 would make 30 empty files with GoPro format file name.

Runing
```Bash
python cleaningTestingFiles.py
```
would delete all go pro files smaller than 10KB.

Runing 
```Bash
python process.py 
```
would convert the file names from AABBCCCC.MP4 to Date_CameraID_CCCC_BB_Time_AA.MP4 style.

This is the first time I try to use github copilot intensively. 
Got to say it is very helpful while making something you already know how to do.
You still need to check the code to make sure the logic is good.
A drawback is the solution provided by github copilot is usually not the most efficient.


Usage:

```Bash
python process.py -i CameraID
```

Convert Gopro Style file name to the new format, and delete the LRV/THM files.

```Bash
python process.py -rc oldCameraID newCameraID
```
Replace the cameraID for converted file names.


```Bash
python process.py -reset
```

go back to goPro style file names.
