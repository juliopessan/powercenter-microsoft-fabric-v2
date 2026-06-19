#!/usr/bin/env powershell
<#
.SYNOPSIS
    Fabric Core MCP Server Integration - Automated Workspace & Lakehouse Setup
    
.DESCRIPTION
    Automates Fabric workspace and lakehouse creation and CSV upload via MCP API
    
.PARAMETER TenantId
    Azure AD Tenant ID
    
.PARAMETER ClientId
    App Registration Client ID
    
.PARAMETER ClientSecret
    App Registration Client Secret
    
.PARAMETER Action
    Action: Create, Upload, Verify
    
.EXAMPLE
    .\fabric-mcp-automation.ps1 -TenantId "xxx" -ClientId "yyy" -ClientSecret "zzz" -Action Create
#>

param(
    [string]$TenantId = $env:AZURE_TENANT_ID,
    [string]$ClientId = $env:AZURE_CLIENT_ID,
    [string]$ClientSecret = $env:AZURE_CLIENT_SECRET,
    [ValidateSet("Create", "Upload", "Verify", "Full")]
    [string]$Action = "Full",
    [string]$CapacityId,
    [string]$WorkspaceName = "informatica-poc-workspace",
    [string]$LakehouseName = "informatica_poc_data"
)

# ═════════════════════════════════════════════════════════════════════════
# CONSTANTS
# ═════════════════════════════════════════════════════════════════════════

$MCP_BASE_URI = "https://api.fabric.microsoft.com/v1/mcp/core"
$TOKEN_URI = "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token"
$SCOPE = "https://fabric.microsoft.com/.default"

$CSV_FILES = @(
    @{ Name = "emp_poc.csv"; Path = "output/emp_poc.csv" },
    @{ Name = "hr_poc.csv"; Path = "output/hr_poc.csv" }
)

$COLORS = @{
    Success = "Green"
    Error = "Red"
    Warning = "Yellow"
    Info = "Cyan"
    Step = "Blue"
}

# ═════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════

function Write-Header {
    param([string]$Message)
    Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor $COLORS.Step
    Write-Host "║ $($Message.PadRight(60)) ║" -ForegroundColor $COLORS.Step
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor $COLORS.Step
}

function Write-Status {
    param(
        [string]$Message,
        [ValidateSet("Success", "Error", "Warning", "Info")]
        [string]$Type = "Info"
    )
    
    $symbols = @{
        Success = "✓"
        Error = "✗"
        Warning = "⚠"
        Info = "ℹ"
    }
    
    Write-Host "  $($symbols[$Type]) $Message" -ForegroundColor $COLORS[$Type]
}

function Get-FabricToken {
    Write-Header "AUTHENTICATING WITH AZURE AD"
    
    if (-not $TenantId -or -not $ClientId -or -not $ClientSecret) {
        Write-Status "Missing credentials (TenantId, ClientId, ClientSecret)" "Error"
        Write-Status "Set as parameters or environment variables:" "Info"
        Write-Host "  `$env:AZURE_TENANT_ID = 'your-tenant-id'" -ForegroundColor Yellow
        Write-Host "  `$env:AZURE_CLIENT_ID = 'your-client-id'" -ForegroundColor Yellow
        Write-Host "  `$env:AZURE_CLIENT_SECRET = 'your-secret'" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Status "Requesting token from: $TOKEN_URI" "Info"
    
    $body = @{
        grant_type    = "client_credentials"
        client_id     = $ClientId
        client_secret = $ClientSecret
        scope         = $SCOPE
    }
    
    try {
        $response = Invoke-RestMethod -Uri $TOKEN_URI -Method Post -Body $body
        $token = $response.access_token
        
        Write-Status "✓ Token obtained (expires in $($response.expires_in) seconds)" "Success"
        return $token
        
    } catch {
        Write-Status "Failed to get token: $($_.Exception.Message)" "Error"
        exit 1
    }
}

function Test-MCPConnection {
    param([string]$Token)
    
    Write-Header "TESTING MCP SERVER CONNECTION"
    
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Content-Type" = "application/json"
    }
    
    try {
        $response = Invoke-RestMethod `
            -Uri "$MCP_BASE_URI/workspaces" `
            -Headers $headers `
            -Method Get
        
        Write-Status "✓ MCP Connection successful" "Success"
        Write-Status "Endpoint: $MCP_BASE_URI" "Info"
        Write-Status "Response: Received $($response.Count) workspaces" "Info"
        
        return $true
        
    } catch {
        Write-Status "✗ MCP Connection failed" "Error"
        Write-Status $_.Exception.Message "Error"
        return $false
    }
}

function Create-FabricWorkspace {
    param(
        [string]$Token,
        [string]$WorkspaceName,
        [string]$CapacityId
    )
    
    Write-Header "CREATING FABRIC WORKSPACE"
    
    Write-Status "Workspace Name: $WorkspaceName" "Info"
    Write-Status "Capacity ID: $CapacityId" "Info"
    
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        displayName = $WorkspaceName
        description = "Informatica PowerCenter to Fabric Migration POC"
        capacityId = $CapacityId
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod `
            -Uri "$MCP_BASE_URI/workspaces" `
            -Headers $headers `
            -Method Post `
            -Body $body
        
        $workspaceId = $response.id
        Write-Status "✓ Workspace created successfully" "Success"
        Write-Status "Workspace ID: $workspaceId" "Info"
        
        return $workspaceId
        
    } catch {
        Write-Status "✗ Failed to create workspace: $($_.Exception.Message)" "Error"
        exit 1
    }
}

function Create-Lakehouse {
    param(
        [string]$Token,
        [string]$WorkspaceId,
        [string]$LakehouseName
    )
    
    Write-Header "CREATING LAKEHOUSE"
    
    Write-Status "Lakehouse Name: $LakehouseName" "Info"
    Write-Status "Parent Workspace: $WorkspaceId" "Info"
    
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Content-Type" = "application/json"
    }
    
    $body = @{
        displayName = $LakehouseName
        description = "Data lakehouse for Informatica POC"
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod `
            -Uri "$MCP_BASE_URI/workspaces/$WorkspaceId/lakehouses" `
            -Headers $headers `
            -Method Post `
            -Body $body
        
        $lakehouseId = $response.id
        Write-Status "✓ Lakehouse created successfully" "Success"
        Write-Status "Lakehouse ID: $lakehouseId" "Info"
        
        return $lakehouseId
        
    } catch {
        Write-Status "✗ Failed to create lakehouse: $($_.Exception.Message)" "Error"
        exit 1
    }
}

function Upload-CSVFile {
    param(
        [string]$Token,
        [string]$WorkspaceId,
        [string]$LakehouseId,
        [string]$FilePath
    )
    
    $fileName = Split-Path -Leaf $FilePath
    
    if (-not (Test-Path $FilePath)) {
        Write-Status "File not found: $FilePath" "Warning"
        return $false
    }
    
    Write-Status "Uploading: $fileName" "Info"
    
    $headers = @{
        "Authorization" = "Bearer $Token"
    }
    
    $fileContent = [System.IO.File]::ReadAllBytes($FilePath)
    $fileSize = $fileContent.Length
    
    $uri = "$MCP_BASE_URI/workspaces/$WorkspaceId/lakehouses/$LakehouseId/files/Files/$fileName"
    
    try {
        $response = Invoke-RestMethod `
            -Uri $uri `
            -Headers $headers `
            -Method Put `
            -Body $fileContent `
            -ContentType "application/octet-stream"
        
        Write-Status "✓ File uploaded: $fileName ($fileSize bytes)" "Success"
        return $true
        
    } catch {
        Write-Status "✗ Failed to upload $fileName : $($_.Exception.Message)" "Error"
        return $false
    }
}

function Verify-LakehouseContent {
    param(
        [string]$Token,
        [string]$WorkspaceId,
        [string]$LakehouseId
    )
    
    Write-Header "VERIFYING LAKEHOUSE CONTENT"
    
    $headers = @{
        "Authorization" = "Bearer $Token"
        "Content-Type" = "application/json"
    }
    
    try {
        $uri = "$MCP_BASE_URI/workspaces/$WorkspaceId/lakehouses/$LakehouseId/files"
        $files = Invoke-RestMethod -Uri $uri -Headers $headers -Method Get
        
        Write-Status "✓ Files in Lakehouse:" "Success"
        foreach ($file in $files) {
            Write-Host "    - $($file.name) ($($file.size) bytes)" -ForegroundColor Green
        }
        
        return $true
        
    } catch {
        Write-Status "✗ Failed to verify content: $($_.Exception.Message)" "Error"
        return $false
    }
}

function Show-Summary {
    param(
        [string]$WorkspaceId,
        [string]$LakehouseId,
        [int]$FilesUploaded
    )
    
    Write-Header "EXECUTION SUMMARY"
    
    Write-Host @"

✅ FABRIC ENVIRONMENT SETUP COMPLETE

📊 Created Resources:
   • Workspace ID: $WorkspaceId
   • Lakehouse ID: $LakehouseId
   • Files Uploaded: $FilesUploaded

🔗 Fabric Console URLs:
   • Workspace: https://app.powerbi.com/groups/$WorkspaceId
   • Lakehouse: https://app.powerbi.com/groups/$WorkspaceId/lakehouse/$LakehouseId

📋 Next Steps:
   1. Open Fabric console at https://app.powerbi.com/
   2. Navigate to your workspace: informatica-poc-workspace
   3. Open the lakehouse: informatica_poc_data
   4. Click "Files" tab to see uploaded CSVs
   5. Create notebook to process data:
      - Use sample code from fabric_import_notebook.py
      - Run: Create_Delta_Tables cell
      - Query created tables

🚀 You're ready to query your data in Fabric!

"@
}

# ═════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════

Write-Host "`n"

# Get token
$token = Get-FabricToken

# Test connection
if (-not (Test-MCPConnection $token)) {
    exit 1
}

# Parse action
switch ($Action) {
    "Create" {
        Write-Status "Creating workspace and lakehouse only" "Info"
        $workspaceId = Create-FabricWorkspace $token $WorkspaceName $CapacityId
        $lakehouseId = Create-Lakehouse $token $workspaceId $LakehouseName
        Show-Summary $workspaceId $lakehouseId 0
    }
    
    "Upload" {
        Write-Status "Uploading files to existing lakehouse" "Warning"
        Write-Host "Enter Workspace ID: " -ForegroundColor Yellow -NoNewline
        $workspaceId = Read-Host
        Write-Host "Enter Lakehouse ID: " -ForegroundColor Yellow -NoNewline
        $lakehouseId = Read-Host
        
        $uploadedCount = 0
        foreach ($csv in $CSV_FILES) {
            if (Upload-CSVFile $token $workspaceId $lakehouseId $csv.Path) {
                $uploadedCount++
            }
        }
        
        Verify-LakehouseContent $token $workspaceId $lakehouseId
        Show-Summary $workspaceId $lakehouseId $uploadedCount
    }
    
    "Verify" {
        Write-Host "Enter Workspace ID: " -ForegroundColor Yellow -NoNewline
        $workspaceId = Read-Host
        Write-Host "Enter Lakehouse ID: " -ForegroundColor Yellow -NoNewline
        $lakehouseId = Read-Host
        
        Verify-LakehouseContent $token $workspaceId $lakehouseId
    }
    
    "Full" {
        Write-Status "Running FULL setup: Create workspace, lakehouse, and upload files" "Info"
        
        $workspaceId = Create-FabricWorkspace $token $WorkspaceName $CapacityId
        $lakehouseId = Create-Lakehouse $token $workspaceId $LakehouseName
        
        Write-Header "UPLOADING CSV FILES"
        
        $uploadedCount = 0
        foreach ($csv in $CSV_FILES) {
            if (Upload-CSVFile $token $workspaceId $lakehouseId $csv.Path) {
                $uploadedCount++
            }
        }
        
        Verify-LakehouseContent $token $workspaceId $lakehouseId
        Show-Summary $workspaceId $lakehouseId $uploadedCount
    }
}

Write-Host "`n"
