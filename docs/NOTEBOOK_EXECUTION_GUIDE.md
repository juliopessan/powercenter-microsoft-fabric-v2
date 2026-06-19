# PySpark Large-Scale Data Generation Notebook
## Execution Guide & Reference

**File:** `notebooks/04_PySpark_Large_Scale_Data_Generation.ipynb`

---

## 🚀 Quick Start

### Environment Setup

**Azure Fabric (Recommended):**
```
1. Open Fabric workspace
2. Create new Notebook
3. Import this notebook file
4. Attach to Spark cluster (default)
5. Run all cells (Ctrl+Alt+Enter)
```

**Databricks:**
```
1. Upload .ipynb to workspace
2. Attach to cluster (7.3 LTS or higher)
3. Run cells sequentially
```

**Local Spark (Testing):**
```bash
jupyter notebook
# Navigate to notebook file
# Requires: pyspark, jupyter installed
```

---

## 📊 Notebook Sections

| Cell | Section | Runtime | Output |
|------|---------|---------|--------|
| 1 | Import Libraries | <1s | Spark ready |
| 2 | Create Departments | <1s | 3 departments |
| 3 | Generate Employees | 5-30s | 10K synthetic records |
| 4 | Add Hierarchy | 2-5s | Manager relationships |
| 5 | Join Data | 3-10s | Complete HR dataset |
| 6 | Write to Storage | 5-15s | CSV files saved |
| 7 | Documentation | - | Guide & reference |
| 8 | Quick Commands | <1s | Performance metrics |

**Total Runtime:** ~20-60 seconds (for 10K records)

---

## ⚙️ Configuration Options

### Scale Dataset
Edit Cell 3:
```python
num_records = 10000  # Change this value
```

| Value | Time | Size | Use Case |
|-------|------|------|----------|
| 1,000 | 1s | 100KB | Testing |
| 10,000 | 5s | 1MB | Development |
| 100,000 | 30s | 15MB | QA |
| 1,000,000 | 3min | 150MB | Production |

### Change Output Location
Edit Cell 6:
```python
# Azure Fabric Lakehouse (default)
output_path = "/lakehouse/default/Files/hr_poc_large"

# ADLS (Data Lake Storage)
output_path = "abfss://container@storage.dfs.core.windows.net/path"

# Local DBFS (Databricks)
output_path = "/dbfs/mnt/data/hr_poc_large"

# Workspace storage
output_path = "/Workspace/Users/username/data/hr_poc_large"
```

### Output Format
Replace Cell 6 write operation:
```python
# CSV (current)
df_joined.write.mode("overwrite").csv(output_path, header=True)

# Parquet (faster, compressed)
df_joined.write.mode("overwrite").parquet(output_path)

# Delta (ACID, time travel)
df_joined.write.format("delta").mode("overwrite").save(output_path)

# SQL Table
df_joined.write.saveAsTable("hr_poc_large", mode="overwrite")
```

---

## ✅ Data Quality Validation

Add this cell after Cell 6 to validate output:

```python
# Data Quality Checks
print("\n🔍 DATA QUALITY VALIDATION")

# Check for nulls
null_counts = df_joined.select([F.count(F.when(F.col(c).isNull(), c)) for c in df_joined.columns])
print(f"Null values: {null_counts.collect()[0]}")

# Check hierarchy
valid_hierarchy = df_joined.filter((col("EMP_ID") > 10) & col("MANAGER_ID").isNull()).count()
print(f"Invalid hierarchy: {valid_hierarchy} records")

# Check salary range
salary_stats = df_joined.agg({"SALARY": ["min", "max", "avg", "stddev"]})
print(f"Salary statistics:")
salary_stats.show()

# Check department distribution
print(f"\nDepartment distribution:")
df_joined.groupBy("DEPT_NAME").count().show()
```

---

## 🐛 Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| **Cell execution hangs** | Cluster too small | Increase executor memory in cluster settings |
| **Out of Memory (OOM)** | `num_records` too large | Reduce to 100K or enable spillover |
| **Path not found error** | Invalid output path | Verify `/lakehouse/default/` exists |
| **Permission denied** | Insufficient write access | Check role assignments on lakehouse |
| **Slow execution** | Single partition bottleneck | Add `.repartition(4)` before write |
| **CSV files are empty** | Header option issue | Ensure `header=True` in write operation |
| **Column naming conflict** | Duplicate column names | Check join operation in Cell 5 |

---

## 📈 Performance Optimization

### For Large Datasets (1M+ records):

```python
# Enable adaptive query execution
spark.conf.set("spark.sql.adaptive.enabled", "true")

# Increase parallelism
df_emps = spark.range(1, num_records + 1, numPartitions=16)

# Enable caching
df_emps.cache()
df_depts.cache()

# Use Parquet instead of CSV
df_joined.write.parquet(output_path)
```

### Monitor Performance:

```python
# Check execution time
import time
start = time.time()
df_joined.write.mode("overwrite").csv(output_path, header=True)
elapsed = time.time() - start
print(f"Write time: {elapsed:.2f} seconds")
```

---

## 🔗 Integration Points

### Use with Informatica POC:
1. **Export** to your POC output folder
2. **Map** `hr_poc_large` CSV to Informatica workflows
3. **Process** through existing transformations
4. **Load** into target systems

### Use with Power BI:
1. **Publish** CSV to shared storage
2. **Create** semantic model in Power BI Service
3. **Build** dashboards on synthetic data

### Use with Azure Data Pipelines:
1. **Schedule** notebook to run daily
2. **Monitor** via Fabric Monitoring
3. **Alert** on failures or data quality issues

---

## 📝 Example Workflows

### Scenario 1: Daily Data Refresh
```python
# Add timestamp column
from datetime import datetime
df_joined = df_joined.withColumn("LOAD_DATE", lit(datetime.now().strftime("%Y-%m-%d")))

# Append to historical table
df_joined.write.mode("append").csv(output_path)
```

### Scenario 2: Multi-Department Simulation
```python
# Extend departments
num_depts = 10
depts = [(i*10, f"Dept_{i}", f"Location_{i}") for i in range(1, num_depts+1)]
df_depts = spark.createDataFrame(depts, ["DEPT_ID", "DEPT_NAME", "LOCATION"])
```

### Scenario 3: Realistic Salary Distribution
```python
# Use normal distribution instead of uniform
from pyspark.sql.functions import randn

df_emps = df_emps.withColumn(
    "SALARY", 
    (randn() * 2000 + 50000).cast("int")  # Mean: 50K, StdDev: 2K
)
```

---

## 📚 Additional Resources

- [PySpark SQL Docs](https://spark.apache.org/docs/latest/sql-programming-guide.html)
- [Azure Fabric Notebooks](https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-code-cells)
- [Delta Lake Documentation](https://docs.delta.io/)

---

## ✨ Next Steps

After running this notebook:

1. ✅ **Validate** output CSV files
2. ✅ **Test** integration with Informatica
3. ✅ **Schedule** for automated runs
4. ✅ **Build** reports on generated data
5. ✅ **Scale** to production volume

---

**Last Updated:** 2026-06-17  
**Status:** Production Ready ✓
