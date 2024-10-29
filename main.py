#imports
import dxpy as dx
import logging
import os
import sys
import time

#functions

##dx login
def get_credentials(path):
    with open(f'{path}','r') as file:
        AUTH_TOKEN =file.read().rstrip()
    
    return AUTH_TOKEN

def dx_login(token):
    """
    Function to check authenticating to DNAneuxs

    Parameters
    ----------
    token : str
        DNAnexus authentication token
    """
    try:
        DX_SECURITY_CONTEXT = {
            "auth_token_type": "Bearer",
            "auth_token": str(token)
        }

        dx.set_security_context(DX_SECURITY_CONTEXT)
        print(dx.api.system_whoami())
    except dx.exceptions.InvalidAuthentication as err:
        print(err)        

##find tar files
def find_files(project, older_than):
    results = dx.api.system_find_data_objects(
        input_params={
            'name':{'regexp':'tar.gz$'},
            'scope':{'project':project},
            'folder':'/',
            'describe':True,
            'created':{'before':older_than}}
    )["results"]

    return(results)

##output tar file details
def tar_details(files):
    details = \
    [f"{x['describe']['name']},{x['id']},{x['project']}" for x in files]

    return details

##delete tar files

##check date

##get date for deletion(6 months ago)
### TODO: need a better way of adjusting this
def get_time_limit():
    #15778458 is 6 months in seconds, dx uses unix epoch 
    return time.time() - 15778458

#inputs
## argumets or read from config?

#get/check credetials
def main ():
    print(sys.argv[1])
    auth_token = get_credentials(sys.argv[1])
    output = sys.argv[2]

    dx_login(auth_token)

    #get old tar files
    timelimit = get_time_limit()
    tars = find_files('project-Gv6PK7Q4Zbz2x97XFz85xP0x', timelimit)

    details = tar_details(tars)

    #record files for deletion
    with open(f"{output}", 'w') as file:
        for i in details:
            file.write(f'{i}\n')

if __name__=='__main__':
    main()