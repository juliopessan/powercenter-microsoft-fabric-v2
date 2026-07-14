# FABRIC MCP INTEGRATION — EXECUTION INSTRUCTIONS
# Workspace: PowerCenter Migration
# Workspace ID: 999fa43f-32d3-4a10-ad5d-b58a5962e43a
# Total Operations: 11

## EXECUTION STEPS:

### OPERATION 1 — Verificar workspace
Tool: mcp_fabricmcpserv_get_workspace
Sequence: 1/11

Parameters:
```json
{
  "WorkspaceId": "999fa43f-32d3-4a10-ad5d-b58a5962e43a"
}
```

### OPERATION 2 — Criar lakehouse powercenter_lakehouse
Tool: mcp_fabricmcpserv_create_item
Sequence: 2/11

Parameters:
```json
{
  "WorkspaceId": "999fa43f-32d3-4a10-ad5d-b58a5962e43a",
  "Details": {
    "displayName": "powercenter_lakehouse",
    "type": "Lakehouse",
    "description": "Lakehouse para migra\u00e7\u00e3o PowerCenter"
  }
}
```

### OPERATION 3 — Upload notebook: 01_PowerCenter_to_PySpark_Translation
Tool: mcp_fabricmcpserv_create_item
Sequence: 3/11

Parameters:
```json
{
  "WorkspaceId": "999fa43f-32d3-4a10-ad5d-b58a5962e43a",
  "Details": {
    "displayName": "01_PowerCenter_to_PySpark_Translation",
    "type": "Notebook",
    "filePath": "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\notebooks\\01_PowerCenter_to_PySpark_Translation.ipynb"
  }
}
```

### OPERATION 4 — Upload notebook: 02_Workflow_Execution_EMP_and_HR
Tool: mcp_fabricmcpserv_create_item
Sequence: 4/11

Parameters:
```json
{
  "WorkspaceId": "999fa43f-32d3-4a10-ad5d-b58a5962e43a",
  "Details": {
    "displayName": "02_Workflow_Execution_EMP_and_HR",
    "type": "Notebook",
    "filePath": "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\notebooks\\02_Workflow_Execution_EMP_and_HR.ipynb"
  }
}
```

### OPERATION 5 — Upload notebook: 03_Map_EMP_Source_to_Target
Tool: mcp_fabricmcpserv_create_item
Sequence: 5/11

Parameters:
```json
{
  "WorkspaceId": "999fa43f-32d3-4a10-ad5d-b58a5962e43a",
  "Details": {
    "displayName": "03_Map_EMP_Source_to_Target",
    "type": "Notebook",
    "filePath": "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\notebooks\\03_Map_EMP_Source_to_Target.ipynb"
  }
}
```

### OPERATION 6 — Upload notebook: 04_PySpark_Large_Scale_Data_Generation
Tool: mcp_fabricmcpserv_create_item
Sequence: 6/11

Parameters:
```json
{
  "WorkspaceId": "999fa43f-32d3-4a10-ad5d-b58a5962e43a",
  "Details": {
    "displayName": "04_PySpark_Large_Scale_Data_Generation",
    "type": "Notebook",
    "filePath": "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\notebooks\\04_PySpark_Large_Scale_Data_Generation.ipynb"
  }
}
```

### OPERATION 7 — Upload notebook: 05_Map_HR_Source_to_Target
Tool: mcp_fabricmcpserv_create_item
Sequence: 7/11

Parameters:
```json
{
  "WorkspaceId": "999fa43f-32d3-4a10-ad5d-b58a5962e43a",
  "Details": {
    "displayName": "05_Map_HR_Source_to_Target",
    "type": "Notebook",
    "filePath": "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\notebooks\\05_Map_HR_Source_to_Target.ipynb"
  }
}
```

### OPERATION 8 — Upload notebook: 06_Pipeline_Import_Guide
Tool: mcp_fabricmcpserv_create_item
Sequence: 8/11

Parameters:
```json
{
  "WorkspaceId": "999fa43f-32d3-4a10-ad5d-b58a5962e43a",
  "Details": {
    "displayName": "06_Pipeline_Import_Guide",
    "type": "Notebook",
    "filePath": "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\notebooks\\06_Pipeline_Import_Guide.ipynb"
  }
}
```

### OPERATION 9 — Upload 8 arquivos XML
Tool: mcp_fabricmcpserv_create_item
Sequence: 9/11

Parameters:
```json
{
  "WorkspaceId": "999fa43f-32d3-4a10-ad5d-b58a5962e43a",
  "Details": {
    "type": "File",
    "files": [
      "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\data\\employees.xml",
      "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\data\\employees.xml",
      "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\data\\hr.xml",
      "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\data\\hr.xml",
      "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\data\\wf_m_poc_xml_emp.XML",
      "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\data\\wf_m_poc_xml_emp.XML",
      "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\data\\wf_m_poc_xml_hr.XML",
      "C:\\Users\\julio.cesar.d.pessan\\powercenter-microsoft-fabric\\data\\wf_m_poc_xml_hr.XML"
    ],
    "destination": "lakehouse"
  }
}
```

### OPERATION 10 — Criar pipeline: Pipeline_EMP_Workflow
Tool: mcp_fabricmcpserv_create_item
Sequence: 10/11

Parameters:
```json
{
  "WorkspaceId": "999fa43f-32d3-4a10-ad5d-b58a5962e43a",
  "Details": {
    "displayName": "Pipeline_EMP_Workflow",
    "type": "Pipeline",
    "notebook": "03_Map_EMP_Source_to_Target",
    "description": "Pipeline para processamento de dados EMP"
  }
}
```

### OPERATION 11 — Criar pipeline: Pipeline_HR_Workflow
Tool: mcp_fabricmcpserv_create_item
Sequence: 11/11

Parameters:
```json
{
  "WorkspaceId": "999fa43f-32d3-4a10-ad5d-b58a5962e43a",
  "Details": {
    "displayName": "Pipeline_HR_Workflow",
    "type": "Pipeline",
    "notebook": "05_Map_HR_Source_to_Target",
    "description": "Pipeline para processamento de dados HR"
  }
}
```
