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


# Region where the WorkSpaces reside
$region="us-west-2"

# Set to the location of the CSV file created in Step 1
$CSV_Input = "c:\temp\wsApps.csv"

# Import the CSV file
$wsData = Import-Csv $CSV_Input

# Loop through the WorkSpaces and publish the application removal
foreach ($workSpace in $wsData){
    if ($workSpace.ApplicationId -ne ""){
        Write-Host "Starting Publish for: " $workSpace.WorkSpaceId
        try{
            $callBlock = "Publish-WKSWorkspaceApplication -WorkspaceId $workSpace.WorkSpaceId -Region $region"
            $scriptblock = [Scriptblock]::Create($callBlock)
            $appDetails = Invoke-Command -scriptblock $scriptblock
        }Catch{
            write-host $_
        }
    }
} 
