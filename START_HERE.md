# 🎯 START HERE — 5 Minute Migration

**Fastest path to migrate PowerCenter to Fabric**

---

## ⚡ The 3-Command Migration

### Command 1: Setup (2 minutes)

```powershell
$env:PYTHONUTF8=1
.venv\Scripts\python.exe scripts\fabric_auth_setup.py
```

✅ Creates `.env` with authentication token

---

### Command 2: Upload (1 minute)

```powershell
.venv\Scripts\python.exe scripts\fabric_complete_upload_auto.py
```

✅ Uploads 6 notebooks + 4 XMLs

---

### Command 3: Execute (1 minute)

```powershell
.venv\Scripts\python.exe scripts\fabric_execute_pipelines_final.py
```

✅ Runs pipelines + generates report

---

## 📋 Pre-Flight Checklist

Before running commands above:

- [ ] `.env` file exists
- [ ] WORKSPACE_ID filled in `.env`
- [ ] LAKEHOUSE_ID filled in `.env`
- [ ] `.venv` activated
- [ ] `notebooks/` has 6 `.ipynb` files
- [ ] `data/` has 4 `.xml` files

---

## 📂 Expected Files

```
notebooks/
├── 01_PowerCenter_to_PySpark_Translation.ipynb ✅
├── 02_Workflow_Execution_EMP_and_HR.ipynb ✅
├── 03_Map_EMP_Source_to_Target.ipynb ✅
├── 04_PySpark_Large_Scale_Data_Generation.ipynb ✅
├── 05_Map_HR_Source_to_Target.ipynb ✅
└── 06_Pipeline_Import_Guide.ipynb ✅

data/
├── employees.xml ✅
├── hr.xml ✅
├── wf_m_poc_xml_emp.XML ✅
└── wf_m_poc_xml_hr.XML ✅
```

---

## ✅ Success = This Report

After step 3, check:

```bash
cat output\fabric_final_report_*.json
```

Look for:
```json
{
  "status": "COMPLETE",
  "notebooks_uploaded": 6,
  "xml_files_uploaded": 4,
  "pipelines_executed": 2
}
```

---

## ❓ Something Wrong?

| Problem | Fix |
|---------|-----|
| Can't run python | Activate: `.venv\Scripts\Activate.ps1` |
| No .env file | Create: `cp .env.template .env` |
| Token error | Rerun: `fabric_auth_setup.py` |
| Upload fails | Check: `output/fabric_execution_final_*.json` |

---

## 📖 Need More Help?

- **Full Guide:** Open `README.md`
- **Quick Reference:** See `/memories/repo/fabric-migration-quick-reference.md`
- **Lessons Learned:** See `/memories/repo/fabric-migration-lessons-learned.md`
- **Roadmap:** See `TODO_LIST.md`

---

## 🎉 That's It!

**3 commands. 5 minutes. Done.**

Your PowerCenter workflows are now in Fabric! 🚀

---

**Need to do this again?** Same 3 commands, just update `.env` with new workspace IDs.
