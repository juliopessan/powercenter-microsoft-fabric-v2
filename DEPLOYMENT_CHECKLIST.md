# 📋 Pre-Deployment Checklist

**Use this checklist before each migration run**

---

## 🔵 Environment Setup

- [ ] Virtual environment activated: `.venv\Scripts\Activate.ps1`
- [ ] Python version verified: `python --version` (3.10+)
- [ ] UTF-8 encoding set: `$env:PYTHONUTF8=1`
- [ ] Azure CLI available: `az --version`
- [ ] Working directory correct: `cd powercenter-microsoft-fabric`

---

## 🔵 Configuration Files

- [ ] `.env` file exists
- [ ] `.env` permissions set: `chmod 600 .env` (Linux/Mac) or (hidden) (Windows)
- [ ] `.env` NOT committed to git
- [ ] `.env` added to `.gitignore`

**Required .env fields:**
- [ ] `FABRIC_USERNAME` filled
- [ ] `FABRIC_PASSWORD` filled
- [ ] `FABRIC_WORKSPACE_ID` filled
- [ ] `FABRIC_WORKSPACE_NAME` filled
- [ ] No trailing spaces in values

---

## 🔵 Source Files Verification

**Notebooks (6 required):**
- [ ] `01_PowerCenter_to_PySpark_Translation.ipynb` exists
- [ ] `02_Workflow_Execution_EMP_and_HR.ipynb` exists
- [ ] `03_Map_EMP_Source_to_Target.ipynb` exists
- [ ] `04_PySpark_Large_Scale_Data_Generation.ipynb` exists
- [ ] `05_Map_HR_Source_to_Target.ipynb` exists
- [ ] `06_Pipeline_Import_Guide.ipynb` exists

**XMLs (4 required):**
- [ ] `employees.xml` exists
- [ ] `hr.xml` exists
- [ ] `wf_m_poc_xml_emp.XML` exists
- [ ] `wf_m_poc_xml_hr.XML` exists

**File sizes reasonable:**
- [ ] Notebooks total < 200 KB
- [ ] XMLs total < 100 KB

---

## 🔵 Azure/Fabric Access

- [ ] Azure account logged in: `az account show`
- [ ] Workspace accessible: `python scripts/fabric_check_auth.py`
- [ ] Output shows "Pronto para migração" ✅

**Workspace Details:**
- [ ] Workspace ID verified
- [ ] Lakehouse ID verified
- [ ] Trial or Premium capacity assigned
- [ ] User has workspace admin role

---

## 🔵 Scripts Verification

- [ ] `scripts/fabric_auth_setup.py` exists (230 lines)
- [ ] `scripts/fabric_check_auth.py` exists (50 lines)
- [ ] `scripts/fabric_complete_upload_auto.py` exists (347 lines)
- [ ] `scripts/fabric_notebooks_onelake_upload.py` exists
- [ ] `scripts/fabric_execute_pipelines_final.py` exists

---

## 🔵 Network & Connectivity

- [ ] Internet connection active
- [ ] No proxy/firewall blocking:
  - [ ] `api.fabric.microsoft.com`
  - [ ] `onelake.blob.core.windows.net`
  - [ ] `login.microsoft.com`
- [ ] DNS resolution working: `nslookup api.fabric.microsoft.com`
- [ ] Ping test: `ping 8.8.8.8`

---

## 🔵 Output Directory

- [ ] `output/` directory exists
- [ ] Previous reports backed up (optional)
- [ ] Directory writable: Can create files here

---

## 🔵 Execution Readiness

**Before running scripts:**
- [ ] Close Fabric Portal browser (avoid conflict)
- [ ] Close other PowerShell windows (prevent env conflicts)
- [ ] Terminal has admin privileges
- [ ] No other Python processes running

---

## ✅ Pre-Execution Summary

| Item | Status | Notes |
|------|--------|-------|
| Python environment | ✅ | Activated |
| Configuration | ✅ | .env complete |
| Source files | ✅ | 6 notebooks + 4 XMLs |
| Azure access | ✅ | Verified connectivity |
| Scripts | ✅ | All present |
| Network | ✅ | Internet OK |
| Ready to execute? | ✅ | **YES** |

---

## 🚀 Execution Steps (Reference)

```powershell
# Step 1: Generate token (2-3 min)
python scripts/fabric_auth_setup.py

# Step 2: Upload notebooks & XMLs (1-2 min)
python scripts/fabric_complete_upload_auto.py

# Step 3: Execute pipelines & report (1-2 min)
python scripts/fabric_execute_pipelines_final.py

# Validation
cat output/fabric_final_report_*.json
```

---

## 📊 Expected Timing

| Step | Duration | Cumulative |
|------|----------|-----------|
| Auth setup | 2-3 min | 2-3 min |
| Upload | 1-2 min | 3-5 min |
| Execute | 1-2 min | 4-7 min |
| **TOTAL** | **~5 min** | **✅ COMPLETE** |

---

## ⚠️ Common Issues (Already Prevented)

| Issue | Prevention |
|-------|-----------|
| UTF-8 encoding errors | Set `$env:PYTHONUTF8=1` ✅ |
| Token expired | Regenerate every 1 hour ✅ |
| Workspace not found | Verify ID in .env ✅ |
| Upload HTTP 400 | Use OneLake endpoint (not REST) ✅ |
| Pipeline not found | Script queries workspace items ✅ |

---

## 🎯 Success Criteria

Migration is successful when:

```
✅ Status: COMPLETE
✅ Notebooks uploaded: 6/6
✅ XMLs uploaded: 4/4
✅ Pipelines executed: 2/2
✅ Report generated: output/fabric_final_report_*.json
✅ Execution time: < 10 minutes
```

---

## 📝 Notes for Next Migration

1. **Reuse:** Same 3 scripts work for any workspace
2. **Customize:** Update WORKSPACE_ID in .env
3. **Relocate:** Can copy entire repo to new directory
4. **Scale:** Can migrate multiple workspaces sequentially

---

**Status: Ready to execute** ✅

**Signed off on:** [DATE] by [USER]

---

*This checklist should be reviewed before every migration run.*
