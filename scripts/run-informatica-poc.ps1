#!/usr/bin/env powershell
param([ValidateSet("emp", "hr", "all")][string]$WorkflowType = "all")

$ScriptDir = $PSScriptRoot
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logsDir = Join-Path $ScriptDir "logs"
$outputDir = Join-Path $ScriptDir "output"
$logFile = Join-Path $logsDir "wf_execution_$timestamp.log"

if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir -Force | Out-Null }
if (-not (Test-Path $outputDir)) { New-Item -ItemType Directory -Path $outputDir -Force | Out-Null }

function Log { 
    param([string]$Msg, [string]$Level = "INFO")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMsg = "[$ts] [$Level] $Msg"
    Write-Host $logMsg
    Add-Content -Path $logFile -Value $logMsg
}

function Invoke-WorkflowEmp {
    Log "=== INICIANDO WORKFLOW: wf_m_poc_xml_emp ===" "INFO"
    $sourceFile = Join-Path $ScriptDir "employees.xml"
    $outputFile = Join-Path $outputDir "emp_poc.csv"
    
    if (-not (Test-Path $sourceFile)) {
        Log "ERRO: $sourceFile nao encontrado" "ERROR"
        return $false
    }
    
    try {
        Log "Lendo XML de entrada..." "INFO"
        [xml]$data = Get-Content -Path $sourceFile -Encoding UTF8
        $records = @()
        $counter = 1
        
        foreach ($emp in $data.employees.employee) {
            $records += [PSCustomObject]@{
                "XPK_employee"   = $counter
                "FK_employees"   = 1
                "EMPLOYEE_ID"    = $emp.EMPLOYEE_ID
                "FIRST_NAME"     = $emp.FIRST_NAME
                "LAST_NAME"      = $emp.LAST_NAME
                "SALARY"         = $emp.SALARY
                "DEPARTMENT_ID"  = $emp.DEPARTMENT_ID
            }
            $counter++
        }
        
        Log "Processados $($records.Count) registros" "INFO"
        $records | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8 -Force
        Log "Arquivo salvo: $outputFile" "SUCCESS"
        return $true
    }
    catch {
        Log "ERRO: $_" "ERROR"
        return $false
    }
}

function Invoke-WorkflowHR {
    Log "=== INICIANDO WORKFLOW: wf_m_poc_xml_hr ===" "INFO"
    $sourceFile = Join-Path $ScriptDir "hr.xml"
    $outputFile = Join-Path $outputDir "hr.csv"
    
    if (-not (Test-Path $sourceFile)) {
        Log "ERRO: $sourceFile nao encontrado" "ERROR"
        return $false
    }
    
    try {
        Log "Lendo XML de entrada..." "INFO"
        [xml]$data = Get-Content -Path $sourceFile -Encoding UTF8
        $records = @()
        $deptCounter = 1
        $empCounter = 1
        
        # Criar mapa de departamentos
        $deptMap = @{}
        foreach ($dept in $data.hr.departments.department) {
            $deptMap[$dept.DEPT_ID] = @{
                XPK = $deptCounter
                ID = $dept.DEPT_ID
                NAME = $dept.DEPT_NAME
                LOCATION = $dept.LOCATION
            }
            $deptCounter++
        }
        
        # Processar employees
        foreach ($emp in $data.hr.employees.employee) {
            $deptId = $emp.DEPT_ID
            $deptInfo = $deptMap[$deptId]
            
            if ($deptInfo) {
                $records += [PSCustomObject]@{
                    "XPK_Department"  = $deptInfo.XPK
                    "DEPT_ID"         = $deptInfo.ID
                    "DEPT_NAME"       = $deptInfo.NAME
                    "XPK_Employee"    = $empCounter
                    "FK_Department"   = $deptInfo.XPK
                    "EMP_ID"          = $emp.EMP_ID
                    "FIRST_NAME"      = $emp.FIRST_NAME
                    "LAST_NAME"       = $emp.LAST_NAME
                    "SALARY"          = $emp.SALARY
                    "MANAGER_ID"      = $emp.MANAGER_ID
                }
                $empCounter++
            }
        }
        
        Log "Processados $($records.Count) registros" "INFO"
        $records | Export-Csv -Path $outputFile -NoTypeInformation -Encoding UTF8 -Force
        Log "Arquivo salvo: $outputFile" "SUCCESS"
        return $true
    }
    catch {
        Log "ERRO: $_" "ERROR"
        return $false
    }
}

# ===== MAIN =====
Log "========== INFORMATICA POWERCENTER - POC ==========" "INFO"
Log "WorkflowType: $WorkflowType" "INFO"
Log "" "INFO"

$success = 0
$failed = 0

switch ($WorkflowType) {
    "emp" {
        if (Invoke-WorkflowEmp) { $success++ } else { $failed++ }
    }
    "hr" {
        if (Invoke-WorkflowHR) { $success++ } else { $failed++ }
    }
    "all" {
        if (Invoke-WorkflowEmp) { $success++ } else { $failed++ }
        Log "" "INFO"
        if (Invoke-WorkflowHR) { $success++ } else { $failed++ }
    }
}

Log "" "INFO"
Log "========== RESUMO FINAL ==========" "INFO"
Log "Sucessos: $success" "SUCCESS"
Log "Falhas: $failed" $(if ($failed -gt 0) { "ERROR" } else { "INFO" })
Log "" "INFO"

if (Test-Path $outputDir) {
    Log "Arquivos gerados:" "INFO"
    Get-ChildItem -Path $outputDir -Filter "*.csv" | ForEach-Object {
        $size = [math]::Round($_.Length / 1KB, 2)
        Log "  - $($_.Name) ($size KB)" "INFO"
    }
}

Log "Log file: $logFile" "INFO"
exit $(if ($failed -eq 0) { 0 } else { 1 })
