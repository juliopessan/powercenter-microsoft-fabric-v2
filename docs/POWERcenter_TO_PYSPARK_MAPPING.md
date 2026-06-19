# PowerCenter to PySpark/Fabric Translation Guide

## Overview

This document provides a comprehensive mapping of Informatica PowerCenter concepts to Microsoft Fabric PySpark implementations.

---

## 1. Core Component Mapping

### PowerCenter Workflow → Fabric Pipeline

| PowerCenter | Fabric Equivalent | Implementation |
|------------|------------------|-----------------|
| Workflow | Pipeline | Native Fabric pipeline with notebook activities |
| Session Task | Notebook Activity | Python/PySpark notebook execution |
| Shell Task | Script Activity | Bash/PowerShell script execution |
| Decision Task | Decision Activity | Conditional branching in pipeline |
| Start/End | Start/End Nodes | Native pipeline nodes |
| Link (Success) | Success Edge | Success connection between activities |
| Link (Failure) | Failure Edge | Failure connection between activities |

### Example Workflow Structure

**PowerCenter:**
```
START
  ↓
[Session: wf_m_poc_xml_emp]
  ├─ Success → [Session: Validation]
  └─ Failure → [Session: Error_Handler]
  ↓
END
```

**Fabric Pipeline:**
```
[Start]
  ↓
[Notebook Activity: Load_EMP_Data]
  ├─ Success → [Notebook Activity: Validate]
  └─ Failure → [Notebook Activity: Error_Handler]
  ↓
[End]
```

---

## 2. Source and Target Mapping

### SOURCE Transformations

#### PowerCenter SOURCE (XML Type)
```xml
<SOURCE NAME="EMP_SOURCE" TYPE="XML" OBJECTTYPE="FILE">
  <FIELD NAME="EMPLOYEE_ID"/>
  <FIELD NAME="FIRST_NAME"/>
  <FIELD NAME="LAST_NAME"/>
  <FIELD NAME="SALARY"/>
</SOURCE>
```

#### PySpark Equivalent
```python
df_source = spark.read \
    .format("xml") \
    .option("rowTag", "employee") \
    .option("inferSchema", "true") \
    .load("employees.xml")
```

### TARGET Transformations

#### PowerCenter TARGET (CSV Type)
```xml
<TARGET NAME="CSV_TARGET" TYPE="CSV" OBJECTTYPE="FILE">
  <PATH>/output/emp_poc.csv</PATH>
</TARGET>
```

#### PySpark Equivalent
```python
df.coalesce(1).write \
    .mode("overwrite") \
    .option("header", "true") \
    .csv("/lakehouse/default/Files/emp_poc")
```

---

## 3. Transformation Mapping

### EXPRESSION Transformation

**PowerCenter:**
```
TRANSFORMATION: EXPRESSION
  INPUT: SALARY (Integer)
  OUTPUT: CALCULATED_SALARY = SALARY * 1.1
```

**PySpark:**
```python
df = df.withColumn(
    "CALCULATED_SALARY",
    col("SALARY") * 1.1
)
```

### FILTER Transformation

**PowerCenter:**
```
TRANSFORMATION: FILTER
  CONDITION: SALARY > 80000
```

**PySpark:**
```python
df = df.filter(col("SALARY") > 80000)
```

### SEQUENCE Transformation

**PowerCenter:**
```
TRANSFORMATION: SEQUENCE
  NEXTVAL: XPK_EMPLOYEE
```

**PySpark:**
```python
from pyspark.sql.window import Window
window_spec = Window.orderBy(col("EMPLOYEE_ID"))
df = df.withColumn(
    "XPK_EMPLOYEE",
    row_number().over(window_spec)
)
```

### LOOKUP Transformation

**PowerCenter:**
```
TRANSFORMATION: LOOKUP
  LOOKUP_TABLE: DEPARTMENTS
  JOIN_KEY: DEPARTMENT_ID
```

**PySpark:**
```python
df = df.join(
    lookup_df,
    on="DEPARTMENT_ID",
    how="left"
)
```

### JOINER Transformation

**PowerCenter:**
```
TRANSFORMATION: JOINER
  MASTER: DEPARTMENTS
  DETAIL: EMPLOYEES
  JOIN_TYPE: LEFT_OUTER
  JOIN_CONDITION: DEPT_ID = DEPARTMENT_ID
```

**PySpark:**
```python
df_result = df_dept.join(
    df_emp,
    df_dept.DEPT_ID == df_emp.DEPARTMENT_ID,
    how="left"
)
```

### AGGREGATOR Transformation

**PowerCenter:**
```
TRANSFORMATION: AGGREGATOR
  GROUP_BY: DEPARTMENT_ID
  AGGREGATE: SUM(SALARY) as TOTAL_SALARY
```

**PySpark:**
```python
df_result = df.groupBy("DEPARTMENT_ID") \
    .agg(sum("SALARY").alias("TOTAL_SALARY"))
```

### FLATTENER Transformation

**PowerCenter:**
```
TRANSFORMATION: FLATTENER
  INPUT: Hierarchical XML
  OUTPUT: Flat table
```

**PySpark:**
```python
# For nested structures
df_flat = df.select(
    col("*"),
    explode(col("nested_array")).alias("flattened_item")
)
```

---

## 4. Data Type Mapping

| PowerCenter | SQL | PySpark |
|------------|-----|---------|
| string | VARCHAR(255) | StringType() / cast("string") |
| int | INTEGER | IntegerType() / cast("int") |
| numeric | DECIMAL(18,2) | DoubleType() / DecimalType() |
| date | DATE | DateType() / cast("date") |
| datetime | TIMESTAMP | TimestampType() / cast("timestamp") |
| boolean | BOOLEAN | BooleanType() / cast("boolean") |

---

## 5. Workflow Execution Pattern

### Simple Mapping Workflow (wf_m_poc_xml_emp)

**PowerCenter Structure:**
```
[START]
  ↓
[SOURCE: employees.xml] → [EXPRESSION: Transform] → [TARGET: emp_poc.csv]
  ↓
[END]
```

**Fabric Pipeline Implementation:**

1. **Load Notebook** activity executes translation notebook
2. **Notebook Steps:**
   - Read XML using Spark
   - Apply transformations
   - Write CSV output
   - Return execution status

**PySpark Code:**
```python
# Step 1: Read (SOURCE)
df = spark.read.format("xml").option("rowTag", "employee").load("employees.xml")

# Step 2: Transform (EXPRESSION + SEQUENCE)
df = df.select(col("EMPLOYEE_ID"), col("FIRST_NAME"), col("LAST_NAME"))
window = Window.orderBy("EMPLOYEE_ID")
df = df.withColumn("XPK_ID", row_number().over(window))

# Step 3: Write (TARGET)
df.write.mode("overwrite").csv("/lakehouse/default/Files/emp_poc")
```

---

## 6. Hierarchical Flattening Pattern (wf_m_poc_xml_hr)

### PowerCenter Approach

```
[SOURCE: hr.xml] 
  ├─ Extract DEPARTMENTS (top-level)
  ├─ Extract EMPLOYEES (nested)
  │
[FLATTENER: Flatten hierarchy]
  │
[JOINER: Department + Employee]
  │
[SEQUENCE: Add surrogate keys]
  │
[TARGET: hr.csv]
```

### PySpark Equivalent

```python
# Step 1: Read hierarchical XML
df_raw = spark.read.format("xml").option("rowTag", "Departments").load("hr.xml")

# Step 2: Extract departments
df_depts = [...departments data...]

# Step 3: Extract employees
df_emps = [...employees data...]

# Step 4: Add surrogate keys (SEQUENCE)
df_depts = df_depts.withColumn(
    "XPK_Department",
    row_number().over(Window.orderBy("DEPT_ID"))
)
df_emps = df_emps.withColumn(
    "XPK_Employee",
    row_number().over(Window.orderBy("EMP_ID"))
)

# Step 5: Join (JOINER)
df_joined = df_depts.join(df_emps, on="DEPT_ID", how="left")

# Step 6: Write
df_joined.write.mode("overwrite").csv("/lakehouse/default/Files/hr_poc")
```

---

## 7. Error Handling & Logging

### PowerCenter Session Configuration

```xml
<SESSION NAME="EMP_Session">
  <ERROR_HANDLING>
    <ON_ERROR>STOP</ON_ERROR>
    <LOG_LEVEL>INFO</LOG_LEVEL>
  </ERROR_HANDLING>
</SESSION>
```

### PySpark Implementation

```python
import logging

logger = logging.getLogger(__name__)

try:
    # Workflow logic
    df = spark.read.format("xml").load("employees.xml")
    df.write.csv("output")
    logger.info("Workflow completed successfully")
    
except Exception as e:
    logger.error(f"Workflow failed: {str(e)}")
    raise
```

---

## 8. Performance Optimization

| PowerCenter | PySpark | Optimization |
|------------|---------|----------------|
| Partitioning | `repartition()` | Parallelize processing |
| Caching | `.cache()` | Reuse DataFrames |
| Session Config | `spark.conf.set()` | Tune parallelism |
| Sorting | `.orderBy()` | Sort before output |
| Row Filtering | `.filter()` | Reduce data early |

---

## 9. Deployment Checklist

- [ ] **Notebooks Created**: Both translation notebooks deployed
- [ ] **Testing**: Unit tests for each transformation
- [ ] **Data Validation**: Output matches PowerCenter baseline
- [ ] **Performance**: Processing time acceptable
- [ ] **Monitoring**: Logging and error handling configured
- [ ] **Documentation**: Transformation logic documented
- [ ] **Fabric Pipeline**: Created and scheduled
- [ ] **Access Control**: RBAC properly configured
- [ ] **Backup**: Original PowerCenter mapping archived

---

## 10. Reference Implementation

### File Structure
```
Informatica-Scenarios/
├── notebooks/
│   ├── 01_PowerCenter_to_PySpark_Translation.ipynb
│   └── 02_Workflow_Execution_EMP_and_HR.ipynb
├── wf_m_poc_xml_emp.XML
├── wf_m_poc_xml_hr.XML
├── employees.xml
├── hr.xml
└── POWERCENTER_TO_PYSPARK_MAPPING.md (this file)
```

### Execution Flow
```
1. Upload notebooks to Fabric workspace
2. Add data files to Lakehouse /Files/
3. Execute Notebook 1: Understand architecture
4. Execute Notebook 2: Run workflows
5. Validate outputs in Lakehouse
6. Create Fabric Pipeline for scheduling
7. Monitor and maintain in production
```

---

## 11. Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| XML parse error | Encoding mismatch | Use `inferSchema=true` option |
| Memory error | Large dataset | Use `coalesce()` before write |
| Null handling | Missing fields | Use `coalesce()` or `fillna()` |
| Key collision | Duplicate keys | Use Window partition for ordering |
| Performance | No partitioning | Use `repartition()` or `partitionBy()` |

---

## 12. Glossary

| Term | Definition |
|------|-----------|
| **Workflow** | Orchestration sequence of tasks |
| **Session** | Execution instance of a mapping |
| **Mapping** | Data transformation logic |
| **SOURCE** | Input data connector |
| **TARGET** | Output data connector |
| **TRANSFORMATION** | Computational step in mapping |
| **EXPRESSION** | Column-level calculation |
| **AGGREGATOR** | GROUP BY equivalent |
| **JOINER** | SQL JOIN equivalent |
| **FLATTENER** | Hierarchy to flat conversion |
| **SEQUENCE** | Auto-incrementing surrogate key |
| **Fabric Pipeline** | Native Fabric orchestration |
| **Notebook Activity** | Python/PySpark execution unit |
| **Lakehouse** | Unified data storage (delta lake) |

---

**Last Updated:** 2026-06-16  
**Status:** ✓ Production Ready  
**Version:** 1.0
