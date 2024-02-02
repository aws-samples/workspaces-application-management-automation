<#
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

Permission is hereby granted, free of charge, to any person obtaining a copy of this
software and associated documentation files (the "Software"), to deal in the Software
without restriction, including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#>

function remove-WorkSpaceApplications(){
    <#
    .SYNOPSIS
        This cmdlet will remove the Office from the WorkSpaces provided in the CSV. Step 2, the Office dissociation, must be completed first.
    .DESCRIPTION
        This cmdlet will remove the Office from the WorkSpaces provided in the CSV. Step 2, the Office dissociation, must be completed first.
    .PARAMETER region
        This required parameter is a string value for the region you are building the WorkSpaces report for. For example, 'us-east-1'. 
    .PARAMETER CSV_Input
        This is  the CSV input generated from step 1 for the removal. 
    .EXAMPLE
        remove-WorkSpaceApplications -CSV_Input c:\temp\wsApps.csv -region us-east-1
    #>
    [CmdletBinding()]
        param (
            [Parameter(Mandatory=$true)]
            [string]$CSV_Input,
            [Parameter(Mandatory=$true)]
            [string]$region
    )
    # Import the CSV file
    try{
        $wsData = Import-Csv $CSV_Input
    }catch{
        write-host "Unable to import CSV at $CSV_Input"
        exit
    }

    # Loop through the WorkSpaces and publish the application removal
    foreach ($workSpace in $wsData){
        if ($workSpace.ApplicationId -ne ""){
            Write-Host "Starting Publish for: " $workSpace.WorkSpaceId
            $workSpaceId = $workSpace.WorkSpaceId
            try{
                Start-Sleep -Milliseconds 500
                $callBlock = "Publish-WKSWorkspaceApplication -WorkspaceId $workSpaceId -Region $region"
                $scriptblock = [Scriptblock]::Create($callBlock)
                $appDetails = Invoke-Command -scriptblock $scriptblock
            }Catch{
                write-host $_
                Write-Host "Retrying failed API call in two seconds.."
                try{
                    Start-Sleep -seconds 2
                    $appDetails = Invoke-Command -scriptblock $scriptblock
                }
                Catch{
                    write-host $_
                }
            }
        }
    } 
}
