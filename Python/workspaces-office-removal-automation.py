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

import json
import boto3
import logging
import os
from botocore.config import Config


def lambda_handler(event, context):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Retrieve starting parameters from event data or environment variable
    # If parameter not found, inject default values defined in Lambda function
    if "WorkspacesDirectory" in event:
        workspaces_directory = event["WorkspacesDirectory"]
    elif "WorkspacesDirectory" in os.environ:
        workspaces_directory = os.environ["WorkspacesDirectory"]
    else:
        workspaces_directory = "UPDATE_DIRECTORYID"

    ## Microsoft Office Professional Plus 2016 - ApplicationId: wsa-khw7gclz4
    ## Microsoft Office Professional Plus 2019 - ApplicationId: wsa-hvh179sq6
    if "OfficeAppId" in event:
        office_app_id = event["OfficeAppId"]
    elif "OfficeAppId" in os.environ:
        office_app_id = os.environ["OfficeAppId"]
    else:
        office_app_id = "UPDATE_APPID"

    # Add exponential backoff and retries        
    config = Config(
       retries = {
          'max_attempts': 10,
          'mode': 'standard'
       }
    )        

    # Create boto3 WorkSpaces client using backoff config
    workspaces_client = boto3.client("workspaces", config=config)

    ## Generate the list of application packages to get their Ids
    ## Uncomment below to view the current list of Ids
    # response = workspaces_client.describe_applications(
    #    Owner = 'AMAZON'
    # )
    # for app in response['Applications']:
    #    print("Application: " +  app['Name'] + "    ApplicationId: " + app['ApplicationId'])

    print(
        f"Searching directory {workspaces_directory} for WorkSpaces with app id {office_app_id} installed."
    )

    ## Generate list of WorkSpaces in directory, 25 at a time
    paginator = workspaces_client.get_paginator("describe_workspaces")
    operation_parameters = {"DirectoryId": workspaces_directory}
    try:
        list_response = {}
        for page in paginator.paginate(
            **operation_parameters, PaginationConfig={"PageSize": 25}
        ):
            if list_response:
                list_response["Workspaces"] = (
                    list_response["Workspaces"] + page["Workspaces"]
                )
            else:
                list_response = {**list_response, **page}
        logger.info(
            "Found %s workspaces in directory %s",
            len(list_response["Workspaces"]),
            workspaces_directory,
        )

    except EndpointConnectionError as e:
        logger.warning("Could not connect to WorkSpaces API endpoint.")
    except Exception as e:
        logger.error(
            "Failed to get WorkSpaces list for directory "
            + workspaces_directory
            + " - "
            + str(e)
        )

    if len(list_response["Workspaces"]) == 0:
        logger.info("No WorkSpaces instances found in directory " + workspaces_directory)
        return {
            "statusCode": 200,
            "body": json.dumps("No WorkSpaces found in directory!"),
        }

    action_count = 0
    ## Loop through all WorkSpaces in the directory
    for workspace in list_response["Workspaces"]:
        ## Get application associations for WorkSpace
        response = workspaces_client.describe_workspace_associations(
            WorkspaceId=workspace["WorkspaceId"],
            AssociatedResourceTypes=[
                "APPLICATION",
            ],
        )

        ## Only check WorkSpaces with associations
        if response["Associations"]:
            ## Check each association looking for Office Application Id
            for association in response["Associations"]:
                if association["AssociatedResourceId"] == office_app_id:
                    action_count = action_count + 1

                    try:
                        logger.info(
                            "Found matching Office association for"
                            + workspace["WorkspaceId"]
                        )
                        print(
                            "Found matching Office association for "
                            + workspace["WorkspaceId"]
                        )

                        print("Removing application association")
                        response = workspaces_client.disassociate_workspace_application(
                            WorkspaceId=workspace["WorkspaceId"],
                            ApplicationId=office_app_id,
                        )

                        print("Initiating application uninstallation")
                        response = workspaces_client.deploy_workspace_applications(
                            WorkspaceId=workspace["WorkspaceId"], Force=True
                        )
                    except Exception as e:
                        logger.error(
                            "Failed to get remove application from "
                            + workspace["WorkspaceId"]
                            + " - "
                            + str(e)
                        )

    print(f"Initiated Office uninstall on {action_count} WorkSpaces.")

    return {
        "statusCode": 200,
        "body": json.dumps("Completed WorkSpaces Application Modifications!"),
    }
