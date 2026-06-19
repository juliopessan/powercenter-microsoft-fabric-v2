param()

$SchemasDir = 'c:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\pipelines\schemas'
$FabricReadyDir = 'c:\Users\julio.cesar.d.pessan\powercenter-microsoft-fabric\pipelines\deliverables\fabric-ready'
$publishTime = Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ"

function Read-ArmActivities {
    param([string]$Path)
    # Neutralize $schema key so PowerShell ConvertFrom-Json can parse it
    $raw = (Get-Content $Path -Raw) -replace '"[$]schema"', '"xschema"'
    $obj = $raw | ConvertFrom-Json
    return $obj.resources[0].properties.activities
}

# ── EMP ──────────────────────────────────────────────────────────────────────
$empActivities = Read-ArmActivities (Join-Path $SchemasDir 'pipeline_wf_m_poc_xml_emp_CORRECT.json')

$empFabric = [ordered]@{
    name       = 'pl_m_poc_xml_emp'
    objectId   = [System.Guid]::NewGuid().ToString()
    properties = [ordered]@{
        activities             = $empActivities
        lastModifiedByObjectId = '00000000-0000-0000-0000-000000000000'
        lastPublishTime        = $publishTime
    }
}
$empJson = $empFabric | ConvertTo-Json -Depth 50
$empJson | Out-File -FilePath (Join-Path $SchemasDir 'pl_m_poc_xml_emp_FABRIC.json') -Encoding UTF8 -Force
Write-Host "[OK] EMP: pl_m_poc_xml_emp_FABRIC.json created ($($empActivities.Count) activities)" -ForegroundColor Green

# ── HR ───────────────────────────────────────────────────────────────────────
$hrActivities = Read-ArmActivities (Join-Path $SchemasDir 'pipeline_wf_m_poc_xml_hr_CORRECT.json')

$hrFabric = [ordered]@{
    name       = 'pl_m_poc_xml_hr'
    objectId   = [System.Guid]::NewGuid().ToString()
    properties = [ordered]@{
        activities             = $hrActivities
        lastModifiedByObjectId = '00000000-0000-0000-0000-000000000000'
        lastPublishTime        = $publishTime
    }
}
$hrJson = $hrFabric | ConvertTo-Json -Depth 50
$hrJson | Out-File -FilePath (Join-Path $SchemasDir 'pl_m_poc_xml_hr_FABRIC.json') -Encoding UTF8 -Force
Write-Host "[OK] HR:  pl_m_poc_xml_hr_FABRIC.json created ($($hrActivities.Count) activities)" -ForegroundColor Green

# ── Rebuild ZIPs ─────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "Rebuilding ZIPs..." -ForegroundColor Cyan

[Reflection.Assembly]::LoadWithPartialName("System.IO.Compression.FileSystem") | Out-Null

function New-FabricZip {
    param([string]$Name, [string]$ManifestPath, [string]$PipelineJsonPath, [string]$OutputZip)

    if (Test-Path $OutputZip) { Remove-Item $OutputZip -Force }

    $tempDir = Join-Path $env:TEMP ("fabric-" + [System.Guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

    Copy-Item $ManifestPath  (Join-Path $tempDir "manifest.json") -Force
    Copy-Item $PipelineJsonPath (Join-Path $tempDir "$Name.json") -Force

    $zip = [System.IO.Compression.ZipFile]::Open($OutputZip, "Create")
    Get-ChildItem $tempDir -File | ForEach-Object {
        [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $_.FullName, $_.Name) | Out-Null
    }
    $zip.Dispose()
    Remove-Item $tempDir -Recurse -Force

    $kb = [math]::Round((Get-Item $OutputZip).Length / 1KB, 2)
    Write-Host "[OK] $OutputZip ($kb KB)" -ForegroundColor Green
}

New-FabricZip -Name "pl_m_poc_xml_emp" `
    -ManifestPath (Join-Path $SchemasDir "manifest_emp.json") `
    -PipelineJsonPath (Join-Path $SchemasDir "pl_m_poc_xml_emp_FABRIC.json") `
    -OutputZip (Join-Path $FabricReadyDir "pl_m_poc_xml_emp_FABRIC.zip")

New-FabricZip -Name "pl_m_poc_xml_hr" `
    -ManifestPath (Join-Path $SchemasDir "manifest_hr.json") `
    -PipelineJsonPath (Join-Path $SchemasDir "pl_m_poc_xml_hr_FABRIC.json") `
    -OutputZip (Join-Path $FabricReadyDir "pl_m_poc_xml_hr_FABRIC.zip")

# ── Verify ───────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "ZIP contents:" -ForegroundColor Cyan
foreach ($zip in @("pl_m_poc_xml_emp_FABRIC.zip", "pl_m_poc_xml_hr_FABRIC.zip")) {
    Write-Host "  $zip" -ForegroundColor Yellow
    tar -tzf (Join-Path $FabricReadyDir $zip) | ForEach-Object { Write-Host "    - $_" }
}

# ── Validate JSON structure ───────────────────────────────────────────────────
Write-Host ""
Write-Host "Validating Fabric JSON structure..." -ForegroundColor Cyan
foreach ($file in @("pl_m_poc_xml_emp_FABRIC.json", "pl_m_poc_xml_hr_FABRIC.json")) {
    $obj = Get-Content (Join-Path $SchemasDir $file) -Raw | ConvertFrom-Json
    $hasName       = $null -ne $obj.name
    $hasObjectId   = $null -ne $obj.objectId
    $hasActivities = $null -ne $obj.properties.activities
    $actCount      = $obj.properties.activities.Count
    Write-Host "  $file" -ForegroundColor Yellow
    Write-Host "    name       : $($obj.name)  $(if($hasName){'[OK]'}else{'[MISSING]'})"
    Write-Host "    objectId   : $($obj.objectId)  $(if($hasObjectId){'[OK]'}else{'[MISSING]'})"
    Write-Host "    activities : $actCount activities  $(if($hasActivities -and $actCount -gt 0){'[OK]'}else{'[MISSING]'})"
}
