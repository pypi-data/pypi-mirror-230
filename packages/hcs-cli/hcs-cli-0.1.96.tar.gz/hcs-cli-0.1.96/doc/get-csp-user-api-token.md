
# Get CSP User API Token

## Purpose
To work with HCS, we need to specify credentials in hcs-cli profile. Either of the following two credentials are needed
* CSP user token --- As a login human user, 
* CSP OAuth client id & secret --- Used for service identity.

## Get CSP User API Token
1. Goto CSP console
   1. Production: https://console.cloud.vmware.com/ 
   2. Staging: https://console-stg.cloud.vmware.com/
2. Click right top user name to bring the dropdown menu.
3. If needed, change organization to the desired one.
4. Click the right top user name to bring the dropdown menu, click "My Account"
5. Click "API Tokens" tab
6. Click "Generate a New API Token"
7. Provide proper input in the form, generate the token, and copy the token after generated.