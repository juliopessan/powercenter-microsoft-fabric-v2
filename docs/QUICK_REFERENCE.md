# Quick Reference - Informatica POC Testing

## 🎯 Commands Summary

### Execute Workflows
```powershell
# Run both workflows
.\run-informatica-poc.ps1 -WorkflowType all

# Run only simple workflow
.\run-informatica-poc.ps1 -WorkflowType emp

# Run only hierarchical workflow
.\run-informatica-poc.ps1 -WorkflowType hr
```

### Run Tests
```powershell
# Run ALL tests (recommended)
.\test-informatica-poc.ps1 -TestType all

# Run specific test suite
.\test-informatica-poc.ps1 -TestType structure
.\test-informatica-poc.ps1 -TestType data
.\test-informatica-poc.ps1 -TestType integrity
.\test-informatica-poc.ps1 -TestType performance
```

### View Results
```powershell
# View latest test log
Get-Content .\test-reports\test-report_*.log -Tail 50

# View workflow logs
Get-Content .\logs\wf_execution_*.log -Tail 50

# List all output files
Get-ChildItem output\ -File
```

---

## 📊 Test Results - Latest Run

```
EXECUTION: 2026-06-16 16:01:50
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Tests Passed:  17 ✓
Tests Failed:   0
Tests Skipped:  0
Success Rate: 100%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 📁 Important Files

| File | Purpose | Type |
|------|---------|------|
| `run-informatica-poc.ps1` | Execute workflows | Script |
| `test-informatica-poc.ps1` | Run test suite | Script |
| `output/emp_poc.csv` | Generated output #1 | CSV |
| `output/hr.csv` | Generated output #2 | CSV |
| `test-reports/test-report.html` | Visual dashboard | HTML |
| `TEST_RESULTS.md` | Detailed results | Report |
| `INDEX.md` | Full documentation | Guide |

---

## ✅ Quality Metrics

```
Data Integrity:     ✓ 100% verified
Record Count:       ✓ 8/8 matching
Salary Consistency: ✓ 100% validated
No Duplicates:      ✓ Confirmed
FK Relationships:   ✓ All valid
Performance:        ✓ 42.86 ms
```

---

## 🔍 Verify Installation

```powershell
# Check all required files
Test-Path .\employees.xml
Test-Path .\hr.xml
Test-Path .\run-informatica-poc.ps1
Test-Path .\test-informatica-poc.ps1

# Check outputs exist
Test-Path .\output\emp_poc.csv
Test-Path .\output\hr.csv

# Check test reports
Test-Path .\test-reports\test-report.html
```

---

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| PowerShell execution disabled | `Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope CurrentUser` |
| File not found | Ensure you're in `Informatica-Scenarios` directory |
| CSV import fails | Run `.\run-informatica-poc.ps1 -WorkflowType all` first |
| Tests show 0 results | Check `test-reports/test-report_*.log` for errors |

---

## 📞 Workflow Overview

### Workflow 1: wf_m_poc_xml_emp
```
Input:  employees.xml (8 records)
   ↓
Process: XML Parse → Transform → CSV Write
   ↓
Output: emp_poc.csv (0.44 KB)
```

### Workflow 2: wf_m_poc_xml_hr
```
Input:  hr.xml (3 depts + 8 emps)
   ↓
Process: XML Parse → Flatten → Transform → CSV Write
   ↓
Output: hr.csv (0.57 KB)
```

---

## 📊 Test Coverage

```
✓ Structure Validation   (2 tests)
✓ Data Validation        (5 tests)
✓ Data Integrity         (4 tests)
✓ Performance            (3 tests)
✓ Input/Output Mapping   (3 tests)
━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TOTAL                  (17 tests)
```

---

## 🎯 One-Line Test (Quick Check)

```powershell
.\run-informatica-poc.ps1 -WorkflowType all; .\test-informatica-poc.ps1 -TestType all
```

---

## 📈 Next Steps

1. ✓ Workflows validated
2. ✓ Tests passed (17/17)
3. ✓ Data integrity confirmed
4. ✓ Performance acceptable
5. → Ready for production

---

## 🌐 Reports Location

- Visual Report: `test-reports/test-report.html`
- Text Report: `TEST_RESULTS.md`
- Log Files: `logs/` and `test-reports/`

**Open `test-reports/test-report.html` in browser for dashboard view**

---

**Last Updated:** 2026-06-16 16:01:51  
**Status:** All Tests Passing ✓
