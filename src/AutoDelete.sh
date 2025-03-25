#!/bin/bash

set -exo pipefail

main() {

    export PATH=$PATH:/home/dnanexus/.local/bin  

    sudo -H python3 -m pip install --no-index --no-deps packages/*
    
    dx download "$config_file" -o config_file

    python3 /home/dnanexus/eggd_automatic_deletion/main.py -c config_file

    output_file=$(dx upload /home/dnanexus/outputFromConfig.txt --brief)

    
    dx-jobutil-add-output output_file "$output_file" --class=file
}
