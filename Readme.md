<!-- dx-header -->
# eggd_auto_dnanexus_data_deletion (DNAnexus Platform App)

A tool for identifying data that is older that a given time.

## What does this app do?
Takes a config file specifying the project, regex patterns(used to identify matching file names) and a time in months. The tool then scans through the given project and extracts the details of files where the names match the given patters and are older than the given time in months.

## What are the typical use cases for this app?
To monitor and storage use and to identify files for deletion.

## What are the inputs?
### Required
- `-iconfig_file` (`file`) a JSON configuration file

## What are the outputs?
- `outputFromConfig.txt` - a CSV file where each column is a feild returned by dxpy's describe function, filtered to the subset specified in the input config.

Column | Description |
--- | --- |
file ID | DNAnexus file ID |
file name | file name onf DNAnexus |
project ID | ID of project caonining file on DNAnexus |
file size | size of file in bytes |


see dxpy documentiaon for more information:

## How to run this app from command line?
```
dx run eggd_auto_dnanexus_data_deletion \
    -iconfig_file=file-xxx
```
Running locally:
```
python3 resources/home/dnanexus/eggd_automatic_deletion/main.py -c <config file>
```

### This app was made by EMEE GLH