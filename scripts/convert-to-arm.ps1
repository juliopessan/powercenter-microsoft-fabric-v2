#!/usr/bin/env powershell
<#
.SYNOPSIS
Convert Data Factory pipeline JSON to ARM Template format for Fabric import
.DESCRIPTION
Transforms direct Data Factory resource format to proper ARM Template structure
#>

param(
    [string]$SourceEmpJson = "c:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\pipelines\schemas\pl_m_poc_xml_emp_FABRIC_DF.json",
    [string]$SourceHrJson = "c:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\pipelines\schemas\pl_m_poc_xml_hr_FABRIC_DF.json"
)

function Convert-ToArmTemplate {
    param([string]$JsonPath, [string]$PipelineName)
    
    Write-Host "[INFO] Converting: $JsonPath" -ForegroundColor Cyan
    
    # Read existing JSON
    $json = Get-Content -Path $JsonPath -Raw | ConvertFrom-Json
    
    # Extract properties
    $name = $json.name
    $properties = $json.properties
    
    # Create ARM Template structure
    $armTemplate = @{
        "$schema" = "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#"
        "contentVersion" = "1.0.0.0"
        "parameters" = @{}
        "variables" = @{}
        "resources" = @(
            @{
                "name" = $name
                "type" = "pipelines"
                "apiVersion" = "2018-06-01"
                "properties" = $properties
                "dependsOn" = @()
            }
        )
    }
    
    # Convert to JSON with proper formatting
    $armJson = $armTemplate | ConvertTo-Json -Depth 50
    
    # Write to file
    $outputPath = $JsonPath -replace "\.json$", "_ARM.json"
    $armJson | Out-File -FilePath $outputPath -Encoding UTF8 -Force
    
    $size = (Get-Item $outputPath).Length / 1KB
    Write-Host "[SUCCESS] Converted: $outputPath ($([math]::Round($size, 2)) KB)" -ForegroundColor Green
    
    return $outputPath
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ARM TEMPLATE CONVERSION" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$empOutput = Convert-ToArmTemplate -JsonPath $SourceEmpJson -PipelineName "pl_m_poc_xml_emp"
Write-Host ""
$hrOutput = Convert-ToArmTemplate -JsonPath $SourceHrJson -PipelineName "pl_m_poc_xml_hr"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[OK] EMP: $empOutput" -ForegroundColor Green
Write-Host "[OK] HR:  $hrOutput" -ForegroundColor Green
Write-Host ""
Write-Host "Next: Update manifests to reference *_ARM.json files" -ForegroundColor Yellow
