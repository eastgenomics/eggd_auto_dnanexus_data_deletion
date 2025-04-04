#!/bin/bash

set -exo pipefail

main() {

    export PATH=$PATH:/home/dnanexus/.local/bin  

    sudo -H python3 -m pip install --no-index --no-deps packages/*
    
    dx download "$config_file" -o config_file

    [ -n "$project" ] && project="--project ${project}" || unset project

    python3 /home/dnanexus/eggd_automatic_deletion/main.py --config config_file $project 

files=(/home/dnanexus/*_files_to_delete_*.csv)
if [[ -s "${files[0]}" ]]; then
    output_file=$(dx upload /home/dnanexus/*_files_to_delete_*.csv --brief)

    dx-jobutil-add-output output_file "$output_file" --class=file
fi
}
