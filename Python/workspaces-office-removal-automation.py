# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## Upgrade Boto3, v.1.28 required for WorkSpaces application management API, adds ~5 seconds to execution time
## AWS Lambda with Python 3.11 defaults to Boto3 v1.27
## Remove once AWS Lambda defaults to > v1.28 
import sys
from pip._internal import main
main(['install', '-I', '-q', 'boto3', '--target', '/tmp/', '--no-cache-dir', '--disable-pip-version-check'])
sys.path.insert(0,'/tmp/')


## Begin main Lambda function
import json
import boto3
import logging
import os



def lambda_handler(event, context):
    
    LOGGER = logging.getLogger()
    LOGGER.setLevel(logging.INFO)


    # Retrieve starting parameters from event data or environment variable
    # If parameter not found, inject default values defined in Lambda function
    if 'WorkspacesDirectory' in event :
        WorkspacesDirectory = event['WorkspacesDirectory']
    elif "WorkspacesDirectory" in os.environ :
        WorkspacesDirectory = os.environ['WorkspacesDirectory']
    else :
        WorkspacesDirectory = "UPDATE_DIRECTORYID"
    
    ## Microsoft Office Professional Plus 2016 - ApplicationId: wsa-khw7gclz4
    ## Microsoft Office Professional Plus 2019 - ApplicationId: wsa-hvh179sq6
    if 'OfficeAppId' in event :
        OfficeAppId = event['OfficeAppId']
    elif "OfficeAppId" in os.environ :
        OfficeAppId = os.environ['OfficeAppId']
    else :
        OfficeAppId = "UPDATE_APPID"

    
    workspaces_client = boto3.client("workspaces")
    
    ## Generate the list of application packages to get their Ids
    ## Uncomment below to view the current list of Ids
    #response = workspaces_client.describe_applications(
    #    Owner = 'AMAZON'
    #)
    #for app in response['Applications']:
    #    print("Application: " +  app['Name'] + "    ApplicationId: " + app['ApplicationId'])

    print(f"Searching directory {WorkspacesDirectory} for WorkSpaces with app id {OfficeAppId} installed.")

    ## Generate list of WorkSpaces in directory, 25 at a time
    paginator = workspaces_client.get_paginator("describe_workspaces")
    operation_parameters = {'DirectoryId': WorkspacesDirectory}
    try:
        ListResponse = {}
        for page in paginator.paginate(**operation_parameters, PaginationConfig={"PageSize": 25}):
            if ListResponse:
                ListResponse["Workspaces"] = (
                    ListResponse["Workspaces"] + page["Workspaces"]
                )
            else:
                ListResponse = {**ListResponse, **page}
        LOGGER.info("Found %s workspaces in directory %s", len(ListResponse["Workspaces"]), WorkspacesDirectory)

    except EndpointConnectionError as e:
        LOGGER.warning("Could not connect to WorkSpaces API endpoint.")
    except Exception as e:
        LOGGER.error("Failed to get WorkSpaces list for directory "+WorkspacesDirectory+" - "+str(e))

    if len(ListResponse['Workspaces']) == 0:
        LOGGER.info("No WorkSpaces instances found in directory "+WorkspacesDirectory)
        return {
            'statusCode': 200,
            'body': json.dumps('No WorkSpaces found in directory!')
        }

    action_count = 0
    ## Loop through all WorkSpaces in the directory        
    for workspace in ListResponse['Workspaces']:

        ## Get application associations for WorkSpace
        response = workspaces_client.describe_workspace_associations(
            WorkspaceId = workspace['WorkspaceId'],
            AssociatedResourceTypes=[
                'APPLICATION',
            ]
        )
        
        ## Only check WorkSpaces with associations
        if response['Associations']:
            ## Check each association looking for Office Application Id
            for association in response['Associations']:
                if association['AssociatedResourceId'] == OfficeAppId:
                    action_count = action_count + 1
                    
                    try :
                        LOGGER.info("Found matching Office association for" +  workspace['WorkspaceId'])
                        print("Found matching Office association for " +workspace['WorkspaceId'])
                        
                        print("Removing application association")
                        response = workspaces_client.disassociate_workspace_application(
                            WorkspaceId=workspace['WorkspaceId'],
                            ApplicationId=OfficeAppId
                        )
                        
                        print("Initiating application uninstallation")
                        response = workspaces_client.deploy_workspace_applications(
                            WorkspaceId=workspace['WorkspaceId'],
                            Force=True
                        )
                    except Exception as e:
                        LOGGER.error("Failed to get remove application from "+workspace['WorkspaceId']+" - "+str(e))
                    
    print(f"Initiated Office uninstall on {action_count} WorkSpaces.")

    return {
        'statusCode': 200,
        'body': json.dumps('Completed WorkSpaces Application Modifications!')
    }
