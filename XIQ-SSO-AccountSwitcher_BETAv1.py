#!/usr/bin/env python3
import getpass  ## import getpass is required if prompting for XIQ crednetials
import json
import requests
from colored import fg
import os
import pandas as pd
from pprint import pprint as pp
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='openpyxl') # Suppress specific warnings
import inquirer


########################################################################################################################
## written by:       Mike Rieben
## e-mail:           mrieben@extremenetworks.com
## date:             December, 2024
## version:          BETA_v1
## tested versions:  Python 3.11.4, XIQ 24r6 (December 2024)
########################################################################################################################
## This script ...  See README.md file for full description 
########################################################################################################################
## ACTION ITEMS / PREREQUISITES
## Please read the README.md file in the package to ensure you've completed the required and optional settings below
## Also as a reminder, do not forget to install required modules:  pip install -r requirements.txt
########################################################################################################################
## - ## two pound chars represents a note about that code block or a title
## - # one pound char represents a note regarding the line and may provide info about what it is or used for
## - There are single # pound char so the VScode will allow for collapsing code blocks e.g. #region - note about begin or end code block
########################################################################################################################


#region - Begin user settings section
##User defined variables as outlined in README documentation
filename = 'XIQ-SSO-AccountSwitcher.xlsx' #<-- If you change it here, remember to also change the template file name.
#endregion ##end user settings section

#region #************************* No user edits below this line required ************************************************************************************
##Global Variables-------------------------------------------------------------------------------------------------------------------------------------
URL = "https://api.extremecloudiq.com"  ##XIQ's API portal
headers = {"Accept": "application/json", "Content-Type": "application/json"}
PATH = os.path.dirname(os.path.abspath(__file__))  #Stores the current Python script directory to write the file to
colorWhite = fg(255) ##DEFAULT Color: color pallete here: https://dslackw.gitlab.io/colored/tables/colors/
colorRed = fg(1) ##RED
colorGreen = fg(2) ##GREEN
colorPurple = fg(54) ##PURPLE
colorCyan = fg(6) ##CYAN
colorOrange = fg(94) ##ORANGE
colorGrey = fg(8)  ##GREY
##ANSI escape code for underlining text
underline_start = '\033[4m'
underline_end = '\033[0m'
counterIntro = 0
#endregion #end Global Variables---------------------------------------------------------------------------------------------------------------------------------

##Use provided credentials to acquire the access token if none was provided-------------------------
def GetaccessToken(XIQ_username, XIQ_password):
    url = f'{URL}/login'
    payload = json.dumps({"username": XIQ_username, "password": XIQ_password})
    response = requests.post(url, headers=headers, data=payload)
    if response is None:
        log_msg = "ERROR: Not able to login into ExtremeCloud IQ - no response!"
        raise TypeError(log_msg)
    if response.status_code != 200:
        log_msg = f"Error getting access token - HTTP Status Code: {str(response.status_code)}"
        try:
            data = response.json()
            if "error_message" in data:
                log_msg += f"\n\t{data['error_message']}"
        except:
            log_msg += ""
        raise TypeError(log_msg)
    data = response.json()
    if "access_token" in data:
        headers["Authorization"] = "Bearer " + data["access_token"]
        return 0
    else:
        log_msg = "Unknown Error: Unable to gain access token"
        raise TypeError(log_msg)
##end Use provided credentials....--------------------------------------------------------------

##Get the VIQ name after credential prompt so the user can confirm they're accessing the correct VIQ
def GetVIQNameRDCName():
    url = URL + "/account/home"
    try:
        rawList = requests.get(url, headers=headers, verify = True)
    except ValueError as e:
        print('script is exiting...')
        raise SystemExit
    except Exception as e:
        print('script is exiting...')
        raise SystemExit
    if rawList.status_code != 200:
        print('Error exiting script...')
        print(rawList.text)
        raise SystemExit
    jsonDump = rawList.json()
    viqName = jsonDump['name']
    rdcName = jsonDump['data_center']
    return viqName, rdcName

##Get and Store All Account Users (Does not collect External Admins)
def GetAllAccountUsers():
    url = URL + "/account/viq"
    try:
        rawList = requests.get(url, headers=headers, verify = True)
    except ValueError as e:
        print('script is exiting...')
        raise SystemExit
    except Exception as e:
        print('script is exiting...')
        raise SystemExit
    if rawList.status_code != 200:
        print('Error exiting script...')
        print(rawList.text)
        raise SystemExit
    jsonDump = rawList.json()
    vhmId = jsonDump['vhm_id']
    ownerId = jsonDump['owner_id']
    #-------------------------------
    viqName, rdcName = GetVIQNameRDCName() #rdcName variable is ignored here since it's not used
    #-------------------------------
    page = 1
    pageCount = 1
    pageSize = 100
    foundUsers = []
    while page <= pageCount:
        url = URL + "/users?page=" + str(page) + "&limit=" + str(pageSize)
        try:
            rawList = requests.get(url, headers=headers, verify = True)
        except ValueError as e:
            print('script is exiting...')
            raise SystemExit
        except Exception as e:
            print('script is exiting...')
            raise SystemExit
        if rawList.status_code != 200:
            print('Error exiting script...')
            print(rawList.text)
            raise SystemExit
        jsonDump = rawList.json()
        for users in jsonDump['data']:
            newData = {}
            newData['Home VIQ ID'] = users['id']
            newData['LOGIN NAME'] = users['login_name']
            newData['FIRST NAME'] = users['first_name']
            newData['LAST NAME'] = users['last_name']
            newData['DISPLAY NAME'] = users['display_name']
            newData['USER ROLE'] = users['user_role']
            newData['VHM ID'] = vhmId
            newData['OWNER ID'] = ownerId
            newData['VIQ NAME'] = viqName
            foundUsers.append(newData)
        pageCount = jsonDump['total_pages']
        print(f"{colorPurple}\nCompleted page {page} of {jsonDump['total_pages']} collecting VIQ Local User Accounts")
        page = jsonDump['page'] + 1
    return foundUsers

def GetAllExternalAccountUsers():
    page = 1
    pageCount = 1
    pageSize = 100
    foundUsers = []
    while page <= pageCount:
        url = URL + "/users/external?page=" + str(page) + "&limit=" + str(pageSize)
        try:
            rawList = requests.get(url, headers=headers, verify = True)
        except ValueError as e:
            print('script is exiting...')
            raise SystemExit
        except Exception as e:
            print('script is exiting...')
            raise SystemExit
        if rawList.status_code != 200:
            print('Error exiting script...')
            print(rawList.text)
            raise SystemExit
        jsonDump = rawList.json()
        for users in jsonDump['data']:
            newData = {}
            newData['Home VIQ ID'] = users['grantee_id']
            newData['ID'] = users['id']
            newData['LOGIN NAME'] = users['login_name']
            newData['USER ROLE'] = users['user_role']
            foundUsers.append(newData)
        pageCount = jsonDump['total_pages']
        print(f"{colorPurple}\nCompleted page {page} of {jsonDump['total_pages']} collecting External VIQ User Accounts")
        page = jsonDump['page'] + 1
    return foundUsers

##Add SSO Users from SSO Configured VIQ to 2+ VIQs as External Users
def AddSSOExternalAccountUsers(uniqueUsersDfForNewExternalUsers_local):
    # print(uniqueUsersDfForNewExternalUsers_local)
    print(f'{colorPurple}\nAttempting to create External SSO Users...')
    for index, row in uniqueUsersDfForNewExternalUsers_local.iterrows(): #loop through each row and create the user
        # print(f'{colorRed}')
        # print(index)
        loginNameValue = {row['LOGIN NAME']}.pop()
        # print(loginNameValue)
        userRoleValue = {row['USER ROLE']}.pop()
        # print(userRoleValue)
        url = f"{URL}/users/external"
        payload = json.dumps(
            {
            "login_name": loginNameValue,
            "user_role": userRoleValue,
            "org_id": 0,
            "location_ids": []
            }
        )
        response = requests.request("POST", url, headers=headers, data=payload)
        if response is None:
            log_msg = "ERROR: POST call to create external user - no response!"
            print(f'{colorRed}{log_msg}')
        if response.status_code != 200:
            log_msg = f"Error - HTTP Status Code: {str(response.status_code)}"
            try:
                data = response.json()
                if "error_message" in data:
                    log_msg += f"\n\t{data['error_message']}"
            except:
                log_msg += ""
            print(f'{colorRed}{log_msg}')
        else:
            print(f'{colorGreen}External SSO user was created successfully: {loginNameValue}\n')
    return

##Prompt user for questsions
def PromptInitialQuestions():
    questions = [
        inquirer.List(
            "initialize",
            message="Use the arrow keys to make your selection, then press enter to continue:",
            choices=[
                "0 - Cancel and Quit",
                "1 - Enter credentials for VIQ # 1 to export user accounts to XLSX in the current directory",
                "2 - Enter credentials for VIQ # 2+ to import SSO user accounts for account switching",
            ]
        ),
    ]
    answers = inquirer.prompt(questions)
    # print(f'You selected: {answers["initialize"]}')
    selection = answers.get("initialize").split("-")[0]
    selection = int(selection)
    return(selection)

##Prompt user for questsions
def PromptExportOptions():
    questions = [
        inquirer.List(
            "initialize",
            message="Use the arrow keys to make your selection, then press enter to continue:",
            choices=[
                "0 - Cancel and Quit",
                "1 - Replace/Overwrite XLSX file contents",
                "2 - Append contents to existing XLSX file",
            ]
        ),
    ]
    answers = inquirer.prompt(questions)
    # print(f'You selected: {answers["initialize"]}')
    selection = answers.get("initialize").split("-")[0]
    selection = int(selection)
    return(selection)
    
##This is the start of the program
def main():
    global counterIntro
    ##Test if template file was found in the current directory which is required.
    if os.path.exists(filename):
        if counterIntro == 0: #Only displays once
            print(f'''{colorPurple}
                *****************************************************************************************
                This script will assist you in copying SSO accounts from a source VIQ#1 into other VIQs.
                This will enable your SSO users to use the Account Switcher to access all their VIQs.

                Workflow:
                - Configure Self Service SSO in VIQ#1 using a local administrator account
                    - Guide:  https://supportdocs.extremenetworks.com/support/documentation/extremecloud-iq/
                    - File:  ExtremeCloud IQ v24.6.0 SSO Integration Guide - Configuring Self-Service SAML SSO with Microsoft Entra ID and Okta
                    - By the time this feature goes GA, there may be a newer guide available.
                    - ALL USERS must login using their new SSO access.  The system will create their local accounts marked SSO.
                - Run script and choose Option 1 to export all accounts from VIQ#1 where SSO is configured
                  - You will be prompted for credentials
                - Verify the contents of the export in "{filename}" found in the current directory which will also be printed to the screen
                - When ready, run script again to import accounts into VIQ#2+ using Option 2
                  - You will be prompted for credentials
                - Repeat Option 2 for all additional VIQs the user needs access to
                - Test by having an SSO user login and verify the Switch ExtremeCloud IQ works as expected
                *****************************************************************************************
                ''')
            counterIntro += 1
        
        selectionInitial = PromptInitialQuestions()
        ##Initial Option 0 - Cancel
        if selectionInitial == 0:
            print(f'{colorRed}User cancelled the script, exiting...\n')
            raise SystemExit
        ##Initial Option 1
        elif selectionInitial == 1:
            print(f'{fg(6)}Enter your XIQ login credentials ')
            XIQ_username = input(f'{fg(6)}Email: ')
            XIQ_password = getpass.getpass(f'{fg(6)}Password: ')
            # XIQ_username = "xxxxx@gmail.com"
            # XIQ_password = "xxxxxxxxxxxxxx"
            if XIQ_username and XIQ_password:
                try:
                    GetaccessToken(XIQ_username, XIQ_password)
                    viqName, rdcName = GetVIQNameRDCName()
                    viqNameRdc = (f'VIQ Name: {viqName}, RDC Name: {rdcName}')
                    print(f'{colorGreen}\n{viqNameRdc}')
                    ##Go acquire every user in the VIQ
                    accountUsers = GetAllAccountUsers()
                    accountsDfToScreen = pd.DataFrame(accountUsers)
                    print(f'{colorGreen}\nExtracted VIQ User Accounts ready for export to XLSX:')
                    print(f'{colorGreen}' + accountsDfToScreen.to_string())
                except TypeError as e:
                    print(e)
                    raise SystemExit
                except:
                    log_msg = "Unknown Error: Failed to generate token"
                    print(log_msg)
                    raise SystemExit
            else:
                print(f'{colorRed}Must enter valid VIQ credentials, exiting...')
                return
            
            # print(f'{colorPurple}\nLocating the XLSX file in the current directory: {filename}')
            xls = pd.ExcelFile(filename)
            dfFromFile = pd.read_excel(xls, sheet_name='UserNames')
            print(f'{colorOrange}\n{filename} - File contents: ')
            pp(dfFromFile) # Print XLSX file contents
            print('\n')
            selectionExport = PromptExportOptions()
            ##Export Option 0 - Cancel
            if selectionExport == 0:
                print(f'{colorRed}\nCancelled... XLSX file was not altered: {filename}')
                dfFromFile = pd.read_excel(filename, sheet_name='UserNames')
                print(f'{colorOrange}\n{filename} - File contents: ')
                pp(dfFromFile) # Print XLSX file contents
                print('\n ')
                raise SystemExit
            ##Export Option 1 - Replace/Overwrite
            elif selectionExport == 1:
                accountUsers_df = pd.DataFrame(accountUsers)
                updated_df = accountUsers_df
                updated_df.to_excel(filename, sheet_name='UserNames', index=False)
                print(f'{colorGreen}XLSX file has been {underline_start}overwritten{underline_end}{colorGreen} with the VIQ\'s account users: {filename}')
                dfFromFile = pd.read_excel(filename, sheet_name='UserNames')
                print(f'{colorGreen}\n{filename} - File contents: ')
                pp(dfFromFile) # Print XLSX file contents
                print('\n ')
                return
            #Export Option 2 - Append
            elif selectionExport == 2:
                accountUsers_df = pd.DataFrame(accountUsers)
                updated_df = pd.concat([dfFromFile, accountUsers_df], ignore_index=True)
                updated_df.to_excel(filename, sheet_name='UserNames', index=False)
                print(f'{colorGreen}\nXLSX file has been {underline_start}appended{underline_end}{colorGreen} with the VIQ\'s account users, not overwritten: {filename}')
                dfFromFile = pd.read_excel(filename, sheet_name='UserNames')
                print(f'{colorGreen}\n{filename} - File contents: ')
                pp(dfFromFile) # Print XLSX file contents
                print('\n ')
                return
            
        ##Initial Option 2
        elif selectionInitial == 2:
            print(f'{fg(6)}Enter your XIQ login credentials ')
            XIQ_username = input(f'{fg(6)}Email: ')
            XIQ_password = getpass.getpass(f'{fg(6)}Password: ')
            # XIQ_username = "xxxxx@gmail.com"
            # XIQ_password = "xxxxxxxxxxxxxx"
            if XIQ_username and XIQ_password:
                try:
                    GetaccessToken(XIQ_username, XIQ_password)
                    dfFromFile = pd.read_excel(filename, sheet_name='UserNames')
                    print(f'{colorGreen}\nSSO source VIQ User Accounts from file')
                    pp(dfFromFile.sort_values(by='Home VIQ ID', ascending=False))
                    viqName, rdcName = GetVIQNameRDCName()
                    viqNameRdc = (f'{colorOrange}\nAccessing VIQ Name: {viqName}, RDC Name: {rdcName}')
                    print(f'{colorGreen}{viqNameRdc}')
                    ##Go acquire every user in the 2+ VIQ
                    accountExternalUsers = GetAllExternalAccountUsers()
                    accountsExternalDf = pd.DataFrame(accountExternalUsers)
                    print(f'{colorOrange}\nExisting VIQ Name: {viqName} - External User Accounts:')
                    printAccountsExternalDf = accountsExternalDf.sort_values(by='Home VIQ ID', ascending=False)
                    print(f'{colorOrange}' + printAccountsExternalDf.to_string())
                    # Merge DataFrames on "Home VIQ ID" to find matches
                    merged_df = pd.merge(dfFromFile, accountsExternalDf, on='Home VIQ ID')
                    # Filter out unique items from dfFromFile that are not in accountsExternalDf
                    filteredUniqueUsersDf = dfFromFile[~dfFromFile['Home VIQ ID'].isin(merged_df['Home VIQ ID'])]
                    # print(filteredUniqueUsersDf)
                    removeLocalUsersDf = filteredUniqueUsersDf[filteredUniqueUsersDf['LOGIN NAME'].str.endswith('@saml.login')]
                    # print(removeLocalUsersDf)
                    if removeLocalUsersDf.empty:
                        print(f'{colorGreen}\nAll users found in SSO source VIQ already exists in this VIQ\'s account list\nNo action required.\n')
                    else:
                        uniqueUsersDfForNewExternalUsers = removeLocalUsersDf[['LOGIN NAME', 'USER ROLE']]
                        # print(uniqueUsersDfForNewExternalUsers)
                        AddSSOExternalAccountUsers(uniqueUsersDfForNewExternalUsers)
                    return
                except TypeError as e:
                    print(e)
                    raise SystemExit
                except:
                    log_msg = "Unknown Error: Failed to generate token"
                    print(log_msg)
                    raise SystemExit
            else:
                print(f'{colorRed}Must enter valid VIQ credentials, exiting...')
                raise SystemExit
            
    else: #inform the user if the script can't find the XLSX file in the current directory
        print(f'{colorRed}\nABORT: File missing! You must copy the provided XSLX (from Github) into your current Python script directory!: {filename} \n')
        
##Python will see this and run whatever function is provided: xxxxxx(), should be the last items in this file
if __name__ == '__main__':
    while True:
        main() ##Go to main function

##***end script***
