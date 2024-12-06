# XIQ SSO Account Switcher

Video Guide Coming Soon...

## Purpose
ExtremeCloud IQ (XIQ) supports local and external account access to access multiple VIQs.  This script applies if you're an organization that uses multiple VIQs and wish to use the new Self Service SSO feature in XIQ so all users can access them.  You will configure Self Service SSO feature in your first VIQ#1 by linking your IDP.  Today, do not configure the same IDP in multiple VIQs.  Each user that will be using SSO to access XIQ will have to login so their local account is created and will be identified by an SSO icon in the UI.

The primary purpose is to gather SSO account info since the username is auto generated via the ID Provider connection.  This script will export all local accounts to an XLSX template from your VIQ#1.  This allows you to push those SSO users to your other External Admin accounts.

### Workflow
1. Configure Self Service SSO in VIQ#1 using a local administrator account
  - Guide:  https://supportdocs.extremenetworks.com/support/documentation/extremecloud-iq/
  - File:  ExtremeCloud IQ v24.6.0 SSO Integration Guide - Configuring Self-Service SAML SSO with Microsoft Entra ID and Okta
  - By the time this feature goes GA, there may be a newer guide available.
  - ALL USERS must login using their new SSO access.  The system will create their local accounts marked SSO.
2. Download all files from GitHub
3. Store all files in the same folder
4. Prepare your Python environment and run the script
5. Run script, Option 1 for VIQ # 1, then review output by opening `XIQ-AccountExport.xlsx`
  - Run script and choose Option 1 to export all accounts from VIQ#1 where SSO is configured
  - You will be prompted for credentials (must be a local administrator account)
  - Verify the contents of the export in `XIQ-AccountExport.xlsx` found in the current directory which will also be printed to the screen
5. When ready, run script again to import accounts into VIQ#2+ using Option 2
  - You will be prompted for credentials (must be a local administrator account)
6. Repeat Option 2 for all additional VIQs the user needs access to
7. Test by having an SSO user login and verify the Switch ExtremeCloud IQ works as expected

## Actions & Requirements
Install the required modules.  No need to generate an API token since this will prompt you to input XIQ credentials.  If you need assistance setting up your computing environment, see this guide: https://github.com/ExtremeNetworksSA/API_Getting_Started

### Copy Required Files
You must copy from Github and place these files into the same folder:  `XIQ-ExportAccountsToXLSX_v#.py` & `requirements.txt` & `XIQ-AccountExport.xlsx`

### Install Modules
There are additional modules that need to be installed in order for this script to function.  They're listed in the *requirements.txt* file and can be installed with the command `pip install -r requirements.txt` if using `PIP`.  Store the *requirements.txt* file in the same directory as the Python script file.

## User Settings
Review the user controllable variables within `XIQ-ExportAccountsToXLSX_v#.py` which are outlined below.
Locate in the script "Begin user settings section" (around line 35)
  - `filename = "XIQ-SSO-AccountSwitcher.xlsx"` < if you change this variable, remember to also change the file name to match.

## Example XLSX Template:

| Home VIQ ID | LOGIN NAME | FIRST NAME | LAST NAME | DISPLAY NAME | USER ROLE | VHM ID | OWNER ID | VIQ NAME |
| --: | --:| --:| --:| --:| --:| --:| --:| --:|

- These are the columns that are provided as default in the template along row 1
