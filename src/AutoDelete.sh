#!/bin/bash

set -exo pipefail

main() {

    export PATH=$PATH:/home/dnanexus/.local/bin  

    sudo -H python3 -m pip install --no-index --no-deps packages/*
    
    dx download "$config_file" -o config_file

    [ -n "$project" ] && project="--project ${project}" || unset project

    python3 /home/dnanexus/eggd_automatic_deletion/main.py --config config_file $project 

output=$(find . -maxdepth 1 -type f -name "*.csv")
if [[ -s "$output" ]]; then
    output_file=$(dx upload ${output} --brief)

    dx-jobutil-add-output output_file "$output_file" --class=file
fi
}
