#imports
import dxpy as dx
import logging
import os
import sys

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

##output tar file details

##delete tar files

##check date

##get date for deletion(6 months ago)


#inputs
## argumets or read from config?

#get/check credetials
def main ():
    print(sys.argv[1])
    auth_token = get_credentials(sys.argv[1])

    dx_login(auth_token)



    

#get old tar files

#record files for deletion

if __name__=='__main__':
    main()