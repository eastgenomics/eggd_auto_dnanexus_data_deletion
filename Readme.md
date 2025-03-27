<!-- dx-header -->
# eggd_auto_dnanexus_data_deletion (DNAnexus Platform App)

A tool for identifying data that is older than a given time.

## What does this app do?
Takes a config file specifying the project, regex patterns(used to identify matching file names) and a time in months. The tool then scans through the given project and extracts the details of files where the names match the given patterns and are older than the given time in months.

## What are the typical use cases for this app?
To monitor storage use and to identify files for deletion.

## What are the inputs?
### Required
- `-iconfig_file` (`file`) a JSON configuration file.
        see repo for an example: https://github.com/eastgenomics/eggd_auto_dnanexus_data_deletion/blob/v0.1-initial_build/resources/home/dnanexus/eggd_automatic_deletion/configs/StagingArea_config.json

### Optional
- `-iproject` (`DNA nexus project id`) ID for the DNAnexus project ID (e.g. `project-xxxx`) which you want to scan for files.

## What are the outputs?
- `outputFromConfig.txt` - a CSV file where each column is a field returned by dxpy's describe function, filtered to the subset specified in the input config.

Column | Description |
--- | --- |
file ID | DNAnexus file ID |
file name | file name on DNAnexus |
project ID | ID of project containing file on DNAnexus |
file size | size of file in bytes |


see dxpy documentation for more information:

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