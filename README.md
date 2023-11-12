# GoProFileProcessingScript

Need to move the script to the same folder with the files to work.
Or use -s and -d to set the source/destination folders.

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
python process.py -p
```
Easy convert.

Runing 
```Bash
python process.py -r
```
Easy restore.

Runing 
```Bash
python process.py -h
```
For help.
