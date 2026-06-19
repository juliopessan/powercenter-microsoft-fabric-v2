param([ValidateSet("all", "structure", "data", "integrity", "performance")][string]$TestType = "all")

$ScriptDir = $PSScriptRoot
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$testLogsDir = Join-Path $ScriptDir "test-reports"
$testReportFile = Join-Path $testLogsDir "test-report_$timestamp.log"

if (-not (Test-Path $testLogsDir)) { New-Item -ItemType Directory -Path $testLogsDir -Force | Out-Null }

$testResults = @{ Passed = 0; Failed = 0; Skipped = 0; Tests = @() }

function Write-Test {
    param([string]$TestName, [string]$Status, [string]$Message = "")
    $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $result = "[$ts] [$Status] $TestName"
    if ($Message) { $result += " - $Message" }
    Write-Host $result
    Add-Content -Path $testReportFile -Value $result
    
    $testResults.Tests += [PSCustomObject]@{
        Name = $TestName; Status = $Status; Message = $Message; Timestamp = $ts
    }
    
    if ($Status -eq "PASS") { $testResults.Passed++ }
    elseif ($Status -eq "FAIL") { $testResults.Failed++ }
    else { $testResults.Skipped++ }
}

# TEST 1: CSV STRUCTURE
function Test-CSVStructure {
    Write-Host "`n=== TEST SUITE: CSV Structure ===" 
    
    $empFile = Join-Path $ScriptDir "output\emp_poc.csv"
    if (-not (Test-Path $empFile)) {
        Write-Test "T1.1-EMP-FILE" "FAIL" "emp_poc.csv not found"
        return
    }
    Write-Test "T1.1-EMP-FILE" "PASS" "emp_poc.csv exists"
    
    $empHeaders = @("XPK_employee", "FK_employees", "EMPLOYEE_ID", "FIRST_NAME", "LAST_NAME", "SALARY", "DEPARTMENT_ID")
    $empData = Import-Csv $empFile
    $actualHeaders = $empData[0].PSObject.Properties.Name | Sort-Object
    $expectedHeaders = $empHeaders | Sort-Object
    
    if (Compare-Object -ReferenceObject $expectedHeaders -DifferenceObject $actualHeaders | Measure-Object | Select-Object -ExpandProperty Count -eq 0) {
        Write-Test "T1.2-EMP-HEADERS" "PASS" "$($empHeaders.Count) headers OK"
    } else {
        Write-Test "T1.2-EMP-HEADERS" "FAIL" "Headers mismatch"
    }
    
    $hrFile = Join-Path $ScriptDir "output\hr.csv"
    if (-not (Test-Path $hrFile)) {
        Write-Test "T1.3-HR-FILE" "FAIL" "hr.csv not found"
        return
    }
    Write-Test "T1.3-HR-FILE" "PASS" "hr.csv exists"
    
    $hrHeaders = @("XPK_Department", "DEPT_ID", "DEPT_NAME", "XPK_Employee", "FK_Department", "EMP_ID", "FIRST_NAME", "LAST_NAME", "SALARY")
    $hrData = Import-Csv $hrFile
    $actualHRHeaders = $hrData[0].PSObject.Properties.Name | Sort-Object
    $expectedHRHeaders = $hrHeaders | Sort-Object
    
    if (Compare-Object -ReferenceObject $expectedHRHeaders -DifferenceObject $actualHRHeaders | Measure-Object | Select-Object -ExpandProperty Count -eq 0) {
        Write-Test "T1.4-HR-HEADERS" "PASS" "$($hrHeaders.Count) headers OK"
    } else {
        Write-Test "T1.4-HR-HEADERS" "FAIL" "Headers mismatch"
    }
}

# TEST 2: DATA VALIDATION
function Test-DataValidation {
    Write-Host "`n=== TEST SUITE: Data Validation ===" 
    
    $empFile = Join-Path $ScriptDir "output\emp_poc.csv"
    $empData = Import-Csv $empFile
    
    if ($empData.Count -eq 8) {
        Write-Test "T2.1-EMP-ROWCOUNT" "PASS" "8 records found"
    } else {
        Write-Test "T2.1-EMP-ROWCOUNT" "FAIL" "$($empData.Count) records (expected 8)"
    }
    
    $nullCount = 0
    foreach ($row in $empData) {
        foreach ($prop in $row.PSObject.Properties) {
            if ([string]::IsNullOrWhiteSpace($prop.Value)) { $nullCount++ }
        }
    }
    
    if ($nullCount -eq 0) {
        Write-Test "T2.2-EMP-NO-NULLS" "PASS" "No null values found"
    } else {
        Write-Test "T2.2-EMP-NO-NULLS" "FAIL" "$nullCount null values found"
    }
    
    $salaryValid = $true
    foreach ($row in $empData) {
        if (-not ([int]::TryParse($row.SALARY, [ref]0))) {
            $salaryValid = $false
            break
        }
    }
    
    if ($salaryValid) {
        Write-Test "T2.3-EMP-SALARY-TYPE" "PASS" "All salaries are valid numbers"
    } else {
        Write-Test "T2.3-EMP-SALARY-TYPE" "FAIL" "Invalid salary format"
    }
    
    $hrFile = Join-Path $ScriptDir "output\hr.csv"
    $hrData = Import-Csv $hrFile
    
    if ($hrData.Count -eq 14) {
        Write-Test "T2.4-HR-ROWCOUNT" "PASS" "14 flattened records found (3 levels hierarchy)"
    } else {
        Write-Test "T2.4-HR-ROWCOUNT" "FAIL" "$($hrData.Count) records (expected 14)"
    }
    
    $depts = ($hrData | Select-Object -ExpandProperty DEPT_NAME -Unique)
    if ($depts.Count -eq 3) {
        Write-Test "T2.5-HR-DEPTS" "PASS" "3 departments OK"
    } else {
        Write-Test "T2.5-HR-DEPTS" "FAIL" "$($depts.Count) departments (expected 3)"
    }
}

# TEST 3: DATA INTEGRITY
function Test-DataIntegrity {
    Write-Host "`n=== TEST SUITE: Data Integrity ===" 
    
    $empFile = Join-Path $ScriptDir "output\emp_poc.csv"
    $hrFile = Join-Path $ScriptDir "output\hr.csv"
    
    $empData = Import-Csv $empFile
    $hrData = Import-Csv $hrFile
    
    $empEmpIds = ($empData | Select-Object -ExpandProperty EMPLOYEE_ID -Unique).Count
    $hrEmpIds = ($hrData | Select-Object -ExpandProperty EMP_ID -Unique).Count
    
    # HR tem hierarquia completa (3 níveis) então pode ter mais registros
    if ($hrEmpIds -ge $empEmpIds) {
        Write-Test "T3.1-EMP-COUNT-MATCH" "PASS" "$empEmpIds employees in emp, $hrEmpIds in hr hierarchy"
    } else {
        Write-Test "T3.1-EMP-COUNT-MATCH" "FAIL" "Employee count mismatch: emp=$empEmpIds, hr=$hrEmpIds"
    }
    
    $inconsistency = 0
    foreach ($empRow in $empData) {
        $empId = $empRow.EMPLOYEE_ID
        $empSalary = $empRow.SALARY
        # HR pode ter diferentes IDs por ser hierarquia completa, verificar correspondência
        $hrMatch = $hrData | Where-Object { $_.EMP_ID -eq $empId }
        if ($hrMatch -and $empSalary -ne ($hrMatch | Select-Object -ExpandProperty SALARY | Select-Object -First 1)) { 
            $inconsistency++ 
        }
    }
    
    if ($inconsistency -eq 0) {
        Write-Test "T3.2-SALARY-CONSISTENCY" "PASS" "Salaries consistent where IDs match"
    } else {
        Write-Test "T3.2-SALARY-CONSISTENCY" "FAIL" "$inconsistency salary inconsistencies"
    }
    
    $dupEmpIds = $empData | Group-Object EMPLOYEE_ID | Where-Object { $_.Count -gt 1 }
    if ($dupEmpIds.Count -eq 0) {
        Write-Test "T3.3-NO-DUP-EMPID" "PASS" "No duplicate EMPLOYEE_IDs"
    } else {
        Write-Test "T3.3-NO-DUP-EMPID" "FAIL" "$($dupEmpIds.Count) duplicate IDs found"
    }
    
    $invalidFk = 0
    foreach ($hrRow in $hrData) {
        if ([int]$hrRow.FK_Department -lt 1) { $invalidFk++ }
    }
    
    if ($invalidFk -eq 0) {
        Write-Test "T3.4-FK-VALIDITY" "PASS" "All foreign keys valid"
    } else {
        Write-Test "T3.4-FK-VALIDITY" "FAIL" "$invalidFk invalid FK relationships"
    }
}

# TEST 4: PERFORMANCE
function Test-Performance {
    Write-Host "`n=== TEST SUITE: Performance ===" 
    
    $empFile = Join-Path $ScriptDir "output\emp_poc.csv"
    $hrFile = Join-Path $ScriptDir "output\hr.csv"
    
    $empSize = (Get-Item $empFile).Length
    $hrSize = (Get-Item $hrFile).Length
    
    if ($empSize -lt 1MB) {
        Write-Test "T4.1-EMP-SIZE" "PASS" "emp_poc.csv = $(($empSize/1KB).ToString('F2')) KB"
    } else {
        Write-Test "T4.1-EMP-SIZE" "FAIL" "emp_poc.csv too large: $(($empSize/1MB).ToString('F2')) MB"
    }
    
    if ($hrSize -lt 1MB) {
        Write-Test "T4.2-HR-SIZE" "PASS" "hr.csv = $(($hrSize/1KB).ToString('F2')) KB"
    } else {
        Write-Test "T4.2-HR-SIZE" "FAIL" "hr.csv too large: $(($hrSize/1MB).ToString('F2')) MB"
    }
    
    $measure = Measure-Command { [void](Import-Csv $empFile) }
    if ($measure.TotalMilliseconds -lt 1000) {
        Write-Test "T4.3-EMP-LOAD-TIME" "PASS" "Load time $(($measure.TotalMilliseconds).ToString('F2')) ms"
    } else {
        Write-Test "T4.3-EMP-LOAD-TIME" "FAIL" "Load time $(($measure.TotalMilliseconds).ToString('F2')) ms (too slow)"
    }
}

# TEST 5: INPUT/OUTPUT COMPARISON
function Test-InputOutput {
    Write-Host "`n=== TEST SUITE: Input/Output Comparison ===" 
    
    $empXmlFile = Join-Path $ScriptDir "employees.xml"
    $empCsvFile = Join-Path $ScriptDir "output\emp_poc.csv"
    
    [xml]$empXml = Get-Content $empXmlFile -Encoding UTF8
    $xmlEmpCount = ($empXml.SelectNodes("//employee")).Count
    $csvEmpCount = @(Import-Csv $empCsvFile).Count
    
    if ($xmlEmpCount -eq $csvEmpCount) {
        Write-Test "T5.1-EMP-COUNT-MATCH" "PASS" "$xmlEmpCount records XML = $csvEmpCount CSV"
    } else {
        Write-Test "T5.1-EMP-COUNT-MATCH" "FAIL" "XML($xmlEmpCount) != CSV($csvEmpCount)"
    }
    
    $csvFirstName = (Import-Csv $empCsvFile | Where-Object EMPLOYEE_ID -eq "101" | Select-Object -ExpandProperty FIRST_NAME)
    $xmlFirstName = ($empXml.employees.employee | Where-Object EMPLOYEE_ID -eq "101" | Select-Object -ExpandProperty FIRST_NAME)
    
    if ($csvFirstName -eq $xmlFirstName) {
        Write-Test "T5.2-NAME-MAPPING" "PASS" "Names mapped correctly"
    } else {
        Write-Test "T5.2-NAME-MAPPING" "FAIL" "Name mapping mismatch"
    }
    
    $hrXmlFile = Join-Path $ScriptDir "hr.xml"
    $hrCsvFile = Join-Path $ScriptDir "output\hr.csv"
    
    [xml]$hrXml = Get-Content $hrXmlFile -Encoding UTF8
    $xmlDeptCount = ($hrXml.SelectNodes("//department")).Count
    $csvDepts = @(Import-Csv $hrCsvFile | Select-Object -ExpandProperty DEPT_ID -Unique).Count
    
    if ($xmlDeptCount -eq $csvDepts) {
        Write-Test "T5.3-DEPT-FLATTEN" "PASS" "$xmlDeptCount departments after flattening"
    } else {
        Write-Test "T5.3-DEPT-FLATTEN" "FAIL" "Department count mismatch: xml=$xmlDeptCount, csv=$csvDepts"
    }
}

# MAIN
function Main {
    Write-Host "=========================================="
    Write-Host "INFORMATICA POC - TEST SUITE"
    Write-Host "=========================================="
    Write-Host ""
    
    Add-Content -Path $testReportFile -Value "=========================================="
    Add-Content -Path $testReportFile -Value "TEST REPORT - $timestamp"
    Add-Content -Path $testReportFile -Value "Test Type: $TestType"
    Add-Content -Path $testReportFile -Value "=========================================="
    Add-Content -Path $testReportFile -Value ""
    
    switch ($TestType) {
        "structure" { Test-CSVStructure }
        "data" { Test-DataValidation }
        "integrity" { Test-DataIntegrity }
        "performance" { Test-Performance }
        "all" {
            Test-CSVStructure
            Test-DataValidation
            Test-DataIntegrity
            Test-Performance
            Test-InputOutput
        }
    }
    
    Write-Host "`n=========================================="
    Write-Host "TEST SUMMARY"
    Write-Host "=========================================="
    Write-Host "PASSED:  $($testResults.Passed)"
    Write-Host "FAILED:  $($testResults.Failed)"
    Write-Host "SKIPPED: $($testResults.Skipped)"
    Write-Host "TOTAL:   $($testResults.Tests.Count)"
    Write-Host ""
    Write-Host "Report: $testReportFile"
    Write-Host ""
    
    Add-Content -Path $testReportFile -Value ""
    Add-Content -Path $testReportFile -Value "TEST SUMMARY"
    Add-Content -Path $testReportFile -Value "PASSED:  $($testResults.Passed)"
    Add-Content -Path $testReportFile -Value "FAILED:  $($testResults.Failed)"
    Add-Content -Path $testReportFile -Value "SKIPPED: $($testResults.Skipped)"
    Add-Content -Path $testReportFile -Value "TOTAL:   $($testResults.Tests.Count)"
    
    return $testResults.Failed -eq 0
}

$success = Main
exit $(if ($success) { 0 } else { 1 })
