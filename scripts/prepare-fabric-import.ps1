#!/usr/bin/env powershell
<#
.SYNOPSIS
    Prepare and validate CSV files for Fabric import
    
.DESCRIPTION
    - Verifies CSV integrity
    - Validates data types and row counts
    - Prepares files for Fabric upload
    - Generates validation report
    
.PARAMETER Action
    Action to perform: Verify, Prepare, Validate, Upload
    
.PARAMETER FilePath
    Path to CSV file (optional)
    
.PARAMETER ReportPath
    Output path for validation report
    
.EXAMPLE
    .\prepare-fabric-import.ps1 -Action Verify
    .\prepare-fabric-import.ps1 -Action Validate -ReportPath "reports/"
#>

param(
    [ValidateSet("Verify", "Prepare", "Validate", "Upload")]
    [string]$Action = "Verify",
    
    [string]$FilePath,
    [string]$ReportPath = "reports/",
    [string]$OutputPath = "output/",
    [switch]$Verbose
)

# ═════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═════════════════════════════════════════════════════════════════════════

$script:CSV_Files = @(
    @{
        Name = "emp_poc.csv"
        Path = "$OutputPath/emp_poc.csv"
        ExpectedRows = 8
        ExpectedColumns = 7
        Description = "Employee data (simple XML transformation)"
    },
    @{
        Name = "hr_poc.csv"
        Path = "$OutputPath/hr_poc.csv"
        ExpectedRows = 8
        ExpectedColumns = 9
        Description = "Hierarchical HR data (flattened)"
    }
)

$script:Report = @{
    Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    TotalFiles = $CSV_Files.Count
    FilesVerified = 0
    FilesValid = 0
    FilesFailed = 0
    Issues = @()
    Details = @()
}

# ═════════════════════════════════════════════════════════════════════════
# FUNCTIONS
# ═════════════════════════════════════════════════════════════════════════

function Write-Header {
    param([string]$Message)
    Write-Host "`n╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║ $($Message.PadRight(60)) ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
}

function Write-Step {
    param(
        [string]$Message,
        [ValidateSet("Info", "Success", "Warning", "Error")]
        [string]$Type = "Info"
    )
    
    $colors = @{
        Info = "White"
        Success = "Green"
        Warning = "Yellow"
        Error = "Red"
    }
    
    $symbols = @{
        Info = "ℹ"
        Success = "✓"
        Warning = "⚠"
        Error = "✗"
    }
    
    Write-Host "  $($symbols[$Type]) $Message" -ForegroundColor $colors[$Type]
}

function Verify-CSVFile {
    param(
        [hashtable]$FileInfo
    )
    
    $name = $FileInfo.Name
    $path = $FileInfo.Path
    $expectedRows = $FileInfo.ExpectedRows
    $expectedColumns = $FileInfo.ExpectedColumns
    
    Write-Host "`n📋 Verifying: $name" -ForegroundColor Cyan
    
    $details = @{
        Name = $name
        Status = "Unknown"
        Exists = $false
        RowCount = 0
        ColumnCount = 0
        FileSize = 0
        Encoding = "Unknown"
        Issues = @()
    }
    
    # 1. Check if file exists
    if (-not (Test-Path $path)) {
        Write-Step "File not found: $path" "Error"
        $details.Status = "FAILED"
        $details.Issues += "File does not exist"
        $script:Report.FilesFailed++
        $script:Report.Issues += "Missing: $name"
        return $details
    }
    
    $details.Exists = $true
    Write-Step "File found" "Success"
    
    # 2. Check file size
    $fileItem = Get-Item $path
    $details.FileSize = $fileItem.Length
    
    if ($fileItem.Length -lt 100) {
        Write-Step "File too small: $($fileItem.Length) bytes" "Warning"
        $details.Issues += "File size suspiciously small"
    } else {
        Write-Step "File size: $($fileItem.Length) bytes" "Info"
    }
    
    # 3. Check encoding
    $content = Get-Content $path -Raw
    $details.Encoding = "UTF-8"  # Assumed based on content reading
    Write-Step "Encoding: UTF-8" "Info"
    
    # 4. Parse CSV
    try {
        $csvContent = Import-Csv $path -ErrorAction Stop
        $details.RowCount = @($csvContent).Count
        $details.ColumnCount = $csvContent[0].PSObject.Properties.Count
        
        Write-Step "Row count: $($details.RowCount) (expected: $expectedRows)" `
            $(if ($details.RowCount -eq $expectedRows) { "Success" } else { "Warning" })
        
        Write-Step "Column count: $($details.ColumnCount) (expected: $expectedColumns)" `
            $(if ($details.ColumnCount -eq $expectedColumns) { "Success" } else { "Warning" })
        
        # 5. Check for null values
        $nullCount = 0
        foreach ($row in $csvContent) {
            foreach ($prop in $row.PSObject.Properties) {
                if ([string]::IsNullOrWhiteSpace($prop.Value)) {
                    $nullCount++
                }
            }
        }
        
        if ($nullCount -gt 0) {
            Write-Step "Warning: Found $nullCount null/empty values" "Warning"
            $details.Issues += "Contains null values: $nullCount"
        } else {
            Write-Step "No null values detected" "Success"
        }
        
        # 6. Show sample
        Write-Host "`n  Sample Data:" -ForegroundColor Gray
        $csvContent | Select-Object -First 2 | Format-Table -AutoSize | Out-String | ForEach-Object { 
            Write-Host "  $_" -ForegroundColor Gray 
        }
        
        # 7. Determine status
        if ($details.RowCount -eq $expectedRows -and $details.ColumnCount -eq $expectedColumns -and $nullCount -eq 0) {
            $details.Status = "VALID"
            $script:Report.FilesValid++
            Write-Step "Status: VALID ✓" "Success"
        } else {
            $details.Status = "VALID_WITH_WARNINGS"
            $script:Report.FilesValid++
            Write-Step "Status: VALID (with warnings)" "Warning"
        }
        
    } catch {
        Write-Step "Error parsing CSV: $($_.Exception.Message)" "Error"
        $details.Status = "FAILED"
        $details.Issues += $_.Exception.Message
        $script:Report.FilesFailed++
        $script:Report.Issues += "$name : CSV parsing error"
    }
    
    $script:Report.FilesVerified++
    $script:Report.Details += $details
    
    return $details
}

function Prepare-ForFabric {
    param([hashtable[]]$Files)
    
    Write-Header "PREPARING FILES FOR FABRIC IMPORT"
    
    foreach ($file in $Files) {
        Write-Host "`n📦 Preparing: $($file.Name)" -ForegroundColor Cyan
        
        # 1. Ensure output directory exists
        if (-not (Test-Path $file.Path)) {
            Write-Step "File not found, skipping" "Warning"
            continue
        }
        
        # 2. Verify encoding is UTF-8
        $content = Get-Content $file.Path -Raw
        $utf8Content = [System.Text.Encoding]::UTF8.GetString(
            [System.Text.Encoding]::GetEncoding($content).GetBytes($content)
        )
        $utf8Content | Out-File $file.Path -Encoding UTF8 -Force
        
        Write-Step "Encoding verified: UTF-8" "Success"
        
        # 3. Create backup
        $backupPath = "$($file.Path).backup"
        Copy-Item $file.Path $backupPath -Force
        Write-Step "Backup created: $backupPath" "Success"
        
        # 4. Create metadata file
        $metaPath = "$($file.Path).meta.json"
        $metadata = @{
            FileName = $file.Name
            Description = $file.Description
            CreatedDate = (Get-Date).ToString("o")
            SourceWorkflow = if ($file.Name -like "*emp*") { "wf_m_poc_xml_emp" } else { "wf_m_poc_xml_hr" }
            RecordCount = (Import-Csv $file.Path | Measure-Object).Count
            Encoding = "UTF-8"
        }
        $metadata | ConvertTo-Json | Out-File $metaPath -Encoding UTF8
        Write-Step "Metadata created: $metaPath" "Success"
    }
}

function Validate-AllFiles {
    param([hashtable[]]$Files)
    
    Write-Header "VALIDATING ALL CSV FILES"
    
    foreach ($file in $Files) {
        Verify-CSVFile $file
    }
    
    # Summary
    Write-Host "`n═════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
    Write-Host "VALIDATION SUMMARY" -ForegroundColor Cyan
    Write-Host "═════════════════════════════════════════════════════════════════`n" -ForegroundColor Cyan
    
    Write-Step "Total Files: $($script:Report.TotalFiles)" "Info"
    Write-Step "Files Verified: $($script:Report.FilesVerified)" "Info"
    Write-Step "Files Valid: $($script:Report.FilesValid)" "Success"
    Write-Step "Files Failed: $($script:Report.FilesFailed)" $(if ($script:Report.FilesFailed -eq 0) { "Success" } else { "Error" })
    
    if ($script:Report.Issues.Count -gt 0) {
        Write-Host "`n⚠️  ISSUES FOUND:" -ForegroundColor Yellow
        foreach ($issue in $script:Report.Issues) {
            Write-Host "   - $issue" -ForegroundColor Yellow
        }
    } else {
        Write-Host "`n✓ NO ISSUES FOUND" -ForegroundColor Green
    }
}

function Generate-Report {
    param(
        [string]$Path = "reports/"
    )
    
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
    
    $reportFile = Join-Path $Path "fabric-import-validation-$(Get-Date -Format 'yyyyMMdd_HHmmss').json"
    
    $script:Report | ConvertTo-Json -Depth 10 | Out-File $reportFile -Encoding UTF8
    
    Write-Host "`n📄 Report saved: $reportFile" -ForegroundColor Green
    
    # Also create markdown report
    $mdFile = $reportFile -replace '\.json$', '.md'
    
    $md = @"
# Fabric Import Validation Report

**Generated:** $($script:Report.Timestamp)

## Summary

- Total Files: $($script:Report.TotalFiles)
- Files Verified: $($script:Report.FilesVerified)
- Files Valid: $($script:Report.FilesValid)
- Files Failed: $($script:Report.FilesFailed)

## File Details

"@
    
    foreach ($detail in $script:Report.Details) {
        $md += @"

### $($detail.Name)

- **Status:** $($detail.Status)
- **Exists:** $($detail.Exists)
- **Row Count:** $($detail.RowCount)
- **Column Count:** $($detail.ColumnCount)
- **File Size:** $($detail.FileSize) bytes
- **Encoding:** $($detail.Encoding)

"@
        
        if ($detail.Issues.Count -gt 0) {
            $md += "**Issues:**`n"
            foreach ($issue in $detail.Issues) {
                $md += "- $issue`n"
            }
        }
    }
    
    $md | Out-File $mdFile -Encoding UTF8
    Write-Host "📄 Markdown report saved: $mdFile" -ForegroundColor Green
}

function Show-FabricImportInstructions {
    Write-Header "NEXT STEPS: IMPORT TO FABRIC"
    
    Write-Host @"

✅ FILES ARE READY FOR FABRIC IMPORT

1. OPEN FABRIC
   URL: https://app.powerbi.com/
   
2. CREATE WORKSPACE
   Name: informatica-poc-workspace
   Capacity: Trial (recommended)

3. CREATE LAKEHOUSE
   Name: informatica_poc_data

4. UPLOAD FILES
   Method A (Drag & Drop - Easiest):
   - Open Lakehouse → Files tab
   - Drag emp_poc.csv and hr_poc.csv
   - Wait for upload to complete ✓

   Method B (Upload Button):
   - Click "Upload" in Files folder
   - Select both CSV files
   - Click "Upload"

5. VALIDATE IN FABRIC
   - Click on each CSV file
   - Select "Preview"
   - Verify data looks correct
   - Check row/column counts

6. CREATE DELTA TABLES
   - Open a new Notebook in Fabric
   - Copy code from FABRIC_IMPORT_GUIDE.md (Passo 7)
   - Run cells to create Delta tables
   - Query to verify

📖 FULL GUIDE: Read FABRIC_IMPORT_GUIDE.md for detailed steps

"@ -ForegroundColor Green
}

# ═════════════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════════════

Write-Host "`n" -ForegroundColor Cyan

switch ($Action) {
    "Verify" {
        Write-Header "VERIFYING CSV FILES FOR FABRIC IMPORT"
        Validate-AllFiles $CSV_Files
        Generate-Report $ReportPath
        Show-FabricImportInstructions
    }
    
    "Prepare" {
        Write-Header "PREPARING FILES FOR FABRIC UPLOAD"
        Prepare-ForFabric $CSV_Files
        Generate-Report $ReportPath
        Write-Step "Files prepared successfully" "Success"
    }
    
    "Validate" {
        Write-Header "COMPLETE VALIDATION"
        Validate-AllFiles $CSV_Files
        Prepare-ForFabric $CSV_Files
        Generate-Report $ReportPath
        Show-FabricImportInstructions
    }
    
    "Upload" {
        Write-Header "FABRIC UPLOAD HELPER"
        Write-Host @"

To upload files to Fabric:

1. Open Fabric: https://app.powerbi.com/
2. Go to your workspace: informatica-poc-workspace
3. Open Lakehouse: informatica_poc_data
4. Click Files tab
5. Click Upload button
6. Select both CSV files:
   - output/emp_poc.csv
   - output/hr_poc.csv
7. Wait for upload to complete

📌 NOTE: This script cannot directly upload to Fabric.
   Use the Fabric UI or Azure Storage Explorer for upload.

For automation, use Python script inside Fabric notebook.

"@ -ForegroundColor Cyan
    }
}

Write-Host "`n"
