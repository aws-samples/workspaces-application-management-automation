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

function Get-WorkSpaceAssociations(){
    <#
    .SYNOPSIS
        This cmdlet will create an inventory for your Amazon WorkSpaces and the application associations that can be used in the following steps to remove Office.
    .DESCRIPTION
        This cmdlet will create an inventory for your Amazon WorkSpaces and the application associations that can be used in the following steps to remove Office.
    .PARAMETER region
        This required parameter is a string value for the region you are building the WorkSpaces report for. For example, 'us-east-1'. 
    .PARAMETER directoryId
        This is a required string parameter that, will only inventory the WorkSpaces in this provided directoryId. 
    .PARAMETER CSV_Output
        This is willbe the CSV output that will be used by steps 2 and 3 for the removal. 
    .EXAMPLE
        Get-WorkSpaceAssociations -CSV_Output c:\temp\wsApps.csv -region us-east-1 -directoryId "d-XXXXXXXXXX"
    #>
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [string]$CSV_Output,
        [Parameter(Mandatory=$true)]
        [string]$region,
        [Parameter(Mandatory=$true)]
        [string]$directoryId

    )  

    $WorkSpacesList = @()

    # Get all of the WorkSpaces in a directory and region
    $RegionalWks = Get-WKSWorkSpaces -Region $region -DirectoryId $directoryId

    # Loop through each WorkSpace to get the details and add place into an array that will be exported
    foreach ($Wks in $RegionalWks){
        $entry = New-Object -TypeName PSobject
        $entry | Add-Member -NotePropertyName "WorkSpaceId" -NotePropertyValue $Wks.WorkspaceId
        $entry | Add-Member -NotePropertyName "Region" -NotePropertyValue $region
        $entry | Add-Member -NotePropertyName "UserName" -NotePropertyValue $Wks.UserName 
        $entry | Add-Member -NotePropertyName "ComputerName" -NotePropertyValue $Wks.ComputerName
        $entry | Add-Member -NotePropertyName "Compute" -NotePropertyValue $Wks.WorkspaceProperties.ComputeTypeName | Out-String
        $entry | Add-Member -NotePropertyName "RootVolume" -NotePropertyValue $Wks.WorkspaceProperties.RootVolumeSizeGib 
        $entry | Add-Member -NotePropertyName "UserVolume" -NotePropertyValue $Wks.WorkspaceProperties.UserVolumeSizeGib
        $entry | Add-Member -NotePropertyName "RunningMode" -NotePropertyValue $Wks.WorkspaceProperties.RunningMode
        if($Wks.WorkspaceProperties.Protocols -like "WSP"){$wsProto = 'WSP'}else{$wsProto = 'PCoIP'}
        $entry | Add-Member -NotePropertyName "Protocol" -NotePropertyValue $wsProto
        $entry | Add-Member -NotePropertyName "IPAddress" -NotePropertyValue $Wks.IPAddress
        $entry | Add-Member -NotePropertyName "directoryId" -NotePropertyValue $Wks.directoryId
        $entry | Add-Member -NotePropertyName "State" -NotePropertyValue $Wks.State
        $entry | Add-Member -NotePropertyName "BundleId" -NotePropertyValue $Wks.BundleId

        # First the associations betweens applications and the specified WorkSpace.
        $wsID =$Wks.WorkspaceId
        $app=""
        try{
            # To get the associations Get-WKSWorkspaceAssociation will be called with the WorkSpaceId
            # https://docs.aws.amazon.com/powershell/latest/reference/items/Get-WKSWorkspaceAssociation.html
            Start-Sleep -Milliseconds 500
            $callBlock = "Get-WKSWorkspaceAssociation -WorkspaceId $wsID -AssociatedResourceType APPLICATION -Region $region"
            $scriptblock = [Scriptblock]::Create($callBlock)
            $app = Invoke-Command -scriptblock $scriptblock
        
        }Catch{
            write-host $_
            Write-Host "Retrying failed API call in two seconds.."
            try{
                Start-Sleep -seconds 2
                Invoke-Command -scriptblock $scriptblock
            }
            Catch{
                write-host $_
                continue
            }
        }
        $appResourceId=$app.AssociatedResourceId
        if ($appResourceId){
            try{
                $callBlock = "Get-WKSApplication -ApplicationId $appResourceId"
                $scriptblock = [Scriptblock]::Create($callBlock)
                $appDetails = Invoke-Command -scriptblock $scriptblock
                $entry | Add-Member -NotePropertyName "ApplicationId" -NotePropertyValue $app.AssociatedResourceId
                $entry | Add-Member -NotePropertyName "ApplicationsInstalled" -NotePropertyValue $appDetails.Description
                $WorkSpacesList  += $entry
            }Catch{
                write-host $_
            }
        }
    }

    # Output results to CSV file
    $WorkSpacesList  | Export-Csv -Path $CSV_Output -NoTypeInformation 
}
