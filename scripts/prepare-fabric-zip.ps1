#!/usr/bin/env powershell
<#
.SYNOPSIS
Prepares Fabric-ready ZIP files with manifest.json + pipeline JSON
.DESCRIPTION
Creates deployment-ready ZIPs for Microsoft Fabric import:
  - pl_m_poc_xml_emp_FABRIC.zip (manifest + EMP pipeline JSON)
  - pl_m_poc_xml_hr_FABRIC.zip (manifest + HR pipeline JSON)
#>

param(
    [ValidateSet("emp", "hr", "all")][string]$Pipeline = "all"
)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$SchemasDir = Join-Path $ProjectRoot "pipelines\schemas"
$DeliverablesDir = Join-Path $ProjectRoot "pipelines\deliverables"
$OutputDir = Join-Path $DeliverablesDir "fabric-ready"
$LogFile = Join-Path $ProjectRoot "logs\zip-prepare-$timestamp.log"

if (-not (Test-Path (Split-Path $LogFile))) {
    New-Item -ItemType Directory -Path (Split-Path $LogFile) -Force | Out-Null
}

function Log {
    param([string]$Msg, [string]$Level = "INFO")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMsg = "[$ts] [$Level] $Msg"
    Write-Host $logMsg
    Add-Content -Path $LogFile -Value $logMsg
}

function Create-FabricZip {
    param(
        [string]$PipelineName,
        [string]$ManifestPath,
        [string]$PipelineJsonPath,
        [string]$OutputPath
    )
    
    Log "Creating Fabric ZIP for: $PipelineName" "INFO"
    
    # Validate inputs
    if (-not (Test-Path $ManifestPath)) {
        Log "ERROR: Manifest not found: $ManifestPath" "ERROR"
        return $false
    }
    if (-not (Test-Path $PipelineJsonPath)) {
        Log "ERROR: Pipeline JSON not found: $PipelineJsonPath" "ERROR"
        return $false
    }
    
    # Create temp directory
    $tempDir = Join-Path $env:TEMP "fabric-zip-$([guid]::NewGuid())"
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    
    try {
        # Copy files to temp
        Copy-Item -Path $ManifestPath -Destination (Join-Path $tempDir "manifest.json") -Force
        Copy-Item -Path $PipelineJsonPath -Destination (Join-Path $tempDir "$PipelineName.json") -Force
        
        # Create ZIP using 7-zip or powershell compression
        if (Get-Command 7z -ErrorAction SilentlyContinue) {
            Log "Using 7-Zip to create archive" "INFO"
            & 7z a -tzip "$OutputPath" "$tempDir\*" -r | Out-Null
        } else {
            Log "Using PowerShell compression" "INFO"
            # Use Add-Type for compression
            [Reflection.Assembly]::LoadWithPartialName("System.IO.Compression.FileSystem") | Out-Null
            $zip = [System.IO.Compression.ZipFile]::Open($OutputPath, "Create")
            
            Get-ChildItem -Path $tempDir -File | ForEach-Object {
                $file = $_
                $entryPath = $file.Name
                [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $file.FullName, $entryPath) | Out-Null
            }
            $zip.Dispose()
        }
        
        if (Test-Path $OutputPath) {
            $size = (Get-Item $OutputPath).Length / 1KB
            Log "[OK] ZIP Created: $OutputPath ($([math]::Round($size, 2)) KB)" "SUCCESS"
            return $true
        } else {
            Log "ERROR: ZIP creation failed" "ERROR"
            return $false
        }
    }
    catch {
        Log "ERROR: $_" "ERROR"
        return $false
    }
    finally {
        if (Test-Path $tempDir) {
            Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

# Create output directory
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

Log "========================================" "INFO"
Log "FABRIC ZIP PREPARATION SCRIPT" "INFO"
Log "========================================" "INFO"
Log "Pipeline: $Pipeline" "INFO"
Log "Output Dir: $OutputDir" "INFO"

$successCount = 0
$failCount = 0

# EMP Pipeline
if ($Pipeline -in @("emp", "all")) {
    Log "" "INFO"
    Log "--- Processing EMP Pipeline ---" "INFO"
    $empZip = Join-Path $OutputDir "pl_m_poc_xml_emp_FABRIC.zip"
    $empManifest = Join-Path $SchemasDir "manifest_emp.json"
    $empJson = Join-Path $SchemasDir "pl_m_poc_xml_emp_FABRIC_DF.json"
    
    if (Create-FabricZip -PipelineName "pl_m_poc_xml_emp" `
                         -ManifestPath $empManifest `
                         -PipelineJsonPath $empJson `
                         -OutputPath $empZip) {
        $successCount++
    } else {
        $failCount++
    }
}

# HR Pipeline
if ($Pipeline -in @("hr", "all")) {
    Log "" "INFO"
    Log "--- Processing HR Pipeline ---" "INFO"
    $hrZip = Join-Path $OutputDir "pl_m_poc_xml_hr_FABRIC.zip"
    $hrManifest = Join-Path $SchemasDir "manifest_hr.json"
    $hrJson = Join-Path $SchemasDir "pl_m_poc_xml_hr_FABRIC_DF.json"
    
    if (Create-FabricZip -PipelineName "pl_m_poc_xml_hr" `
                         -ManifestPath $hrManifest `
                         -PipelineJsonPath $hrJson `
                         -OutputPath $hrZip) {
        $successCount++
    } else {
        $failCount++
    }
}

# Summary
Log "" "INFO"
Log "========================================" "INFO"
Log "SUMMARY" "INFO"
Log "========================================" "INFO"
Log "Successes: $successCount" "INFO"
Log "Failures: $failCount" "INFO"
Log "Output Location: $OutputDir" "INFO"
Log "" "INFO"
Log "[OK] Ready for Fabric Import:" "INFO"
Get-ChildItem -Path $OutputDir -Filter "*.zip" | ForEach-Object {
    $size = $_.Length / 1KB
    Log "  [OK] $($_.Name) ($([math]::Round($size, 2)) KB)" "INFO"
}

Log "" "INFO"
Log "Log file: $LogFile" "INFO"
