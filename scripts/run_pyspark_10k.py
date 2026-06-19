#!/usr/bin/env python3
"""
PySpark Data Generation Script
Generates 10,000 synthetic employee records with departmental hierarchy
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, concat, floor, rand, when, min as spark_min, max as spark_max, avg as spark_avg
import os
from datetime import datetime

# Initialize Spark
spark = SparkSession.builder \
    .appName("HR_POC_DataGeneration") \
    .config("spark.driver.memory", "2g") \
    .config("spark.executor.memory", "2g") \
    .getOrCreate()

print("✅ Spark session initialized")
print(f"Spark version: {spark.version}")

# ==============================================================================
# STEP 1: Create Department DataFrame
# ==============================================================================
print("\n📊 Creating departments...")
departments = [
    (10, "Data & AI", "Sao Paulo"),
    (20, "Engineering", "Rio de Janeiro"),
    (30, "Operations", "Belo Horizonte")
]
df_depts = spark.createDataFrame(departments, ["DEPT_ID", "DEPT_NAME", "LOCATION"])
print(f"✓ Created {df_depts.count()} departments")
df_depts.show()

# ==============================================================================
# STEP 2: Generate Synthetic Employees (10,000 records)
# ==============================================================================
print("\n👥 Generating 10,000 synthetic employee records...")
num_records = 10000

df_emps = spark.range(1, num_records + 1) \
    .withColumnRenamed("id", "EMP_ID") \
    .withColumn("FIRST_NAME", concat(lit("Emp_"), col("EMP_ID"))) \
    .withColumn("LAST_NAME", lit("Synthetic")) \
    .withColumn("SALARY", (rand() * 5000 + 7000).cast("int")) \
    .withColumn("DEPT_ID", (floor(rand() * 3) * 10 + 10).cast("int"))

print(f"✓ Generated {df_emps.count()} employees")
df_emps.limit(5).show()

# ==============================================================================
# STEP 3: Add Hierarchical Relationships (Manager IDs)
# ==============================================================================
print("\n🔗 Adding manager hierarchies...")
df_emps = df_emps.withColumn(
    "MANAGER_ID",
    when(col("EMP_ID") <= 10, None).otherwise((col("EMP_ID") / 10).cast("int"))
)

print(f"✓ Hierarchy applied")
df_emps.filter(col("EMP_ID") <= 20).show()

# ==============================================================================
# STEP 4: Join Departments and Employees
# ==============================================================================
print("\n🔀 Joining departments and employees...")
df_joined = df_depts.join(df_emps, on="DEPT_ID", how="left")

print(f"✓ Final dataset: {df_joined.count()} rows")
print(f"✓ Columns: {len(df_joined.columns)}")
df_joined.limit(5).show()

# ==============================================================================
# STEP 5: Data Quality Validation
# ==============================================================================
print("\n✅ DATA QUALITY VALIDATION")

# Check for nulls in critical fields
null_emps = df_joined.filter(col("EMP_ID").isNull()).count()
print(f"  Null EMP_IDs: {null_emps}")

null_names = df_joined.filter(col("FIRST_NAME").isNull()).count()
print(f"  Null FIRST_NAMEs: {null_names}")

# Check hierarchy validity
total_records = df_joined.count()
directors = df_joined.filter(col("MANAGER_ID").isNull()).count()
staff = df_joined.filter(col("MANAGER_ID").isNotNull()).count()
print(f"  Total records: {total_records}")
print(f"  Directors (no manager): {directors}")
print(f"  Staff (with manager): {staff}")

# Check salary range
salary_agg = df_joined.agg(
    spark_min("SALARY").alias("min_salary"),
    spark_max("SALARY").alias("max_salary"),
    spark_avg("SALARY").alias("avg_salary")
).collect()[0]
print(f"  Salary range: ${salary_agg['min_salary']}-${salary_agg['max_salary']} (avg: ${salary_agg['avg_salary']:.0f})")

# Department distribution
print("\n  Department distribution:")
df_joined.groupBy("DEPT_NAME").agg(
    {"EMP_ID": "count"}
).withColumnRenamed("count(EMP_ID)", "COUNT").show()

# ==============================================================================
# STEP 6: Write to CSV (Local)
# ==============================================================================
print("\n💾 Writing output to CSV...")
output_dir = "./output/hr_poc_10k"

# Remove existing directory if it exists
import shutil
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)

# Write CSV
df_joined.coalesce(1).write.mode("overwrite").csv(output_dir, header=True)
print(f"✓ CSV written to: {output_dir}")

# Get the actual CSV filename
csv_files = [f for f in os.listdir(output_dir) if f.endswith('.csv')]
if csv_files:
    csv_file = csv_files[0]
    csv_path = os.path.join(output_dir, csv_file)
    file_size = os.path.getsize(csv_path) / (1024 * 1024)  # Convert to MB
    print(f"✓ File: {csv_file}")
    print(f"✓ Size: {file_size:.2f} MB")

# ==============================================================================
# STEP 7: Summary Statistics
# ==============================================================================
print("\n📈 EXECUTION SUMMARY")
print(f"  ✓ Generated {num_records:,} employee records")
print(f"  ✓ {df_depts.count()} departments")
print(f"  ✓ Output format: CSV")
print(f"  ✓ Output location: {output_dir}")
print(f"  ✓ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

print("\n✨ Data generation complete!")
print("   Next steps:")
print("   1. Validate CSV files in ./output/hr_poc_10k")
print("   2. Load into Power BI for visualization")
print("   3. Use with Informatica POC workflows")

# Close Spark session
spark.stop()
print("\n✓ Spark session closed")
