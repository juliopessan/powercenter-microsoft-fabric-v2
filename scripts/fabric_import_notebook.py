# Fabric Notebook: 03_Import_and_Create_Delta_Tables.ipynb
# Este notebook importa os CSVs gerados e cria tabelas Delta no Fabric

# ═════════════════════════════════════════════════════════════════════════
# CELL 1: SETUP E IMPORTS
# ═════════════════════════════════════════════════════════════════════════

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

spark = SparkSession.builder \
    .appName("FabricImportAndTransform") \
    .getOrCreate()

print("✓ Spark Session initialized")
print(f"Spark Version: {spark.version}")

# ═════════════════════════════════════════════════════════════════════════
# CELL 2: CONFIGURAÇÃO DE CAMINHOS
# ═════════════════════════════════════════════════════════════════════════

# Paths
LAKEHOUSE_PATH = "/lakehouse/default"
FILES_PATH = f"{LAKEHOUSE_PATH}/Files"
TABLES_PATH = f"{LAKEHOUSE_PATH}/Tables"

# CSV Files na pasta /Files/
CSV_EMP = f"{FILES_PATH}/emp_poc.csv"
CSV_HR = f"{FILES_PATH}/hr_poc.csv"

# Nomes das tabelas Delta
TABLE_EMP = "emp_poc"
TABLE_HR = "hr_poc"

print("═" * 60)
print("CONFIGURATION")
print("═" * 60)
print(f"Lakehouse Path: {LAKEHOUSE_PATH}")
print(f"Files Path: {FILES_PATH}")
print(f"Tables Path: {TABLES_PATH}")
print(f"CSV EMP Location: {CSV_EMP}")
print(f"CSV HR Location: {CSV_HR}")
print(f"Target Tables: {TABLE_EMP}, {TABLE_HR}")

# ═════════════════════════════════════════════════════════════════════════
# CELL 3: DEFINIR SCHEMAS
# ═════════════════════════════════════════════════════════════════════════

# Schema para emp_poc.csv
emp_schema = StructType([
    StructField("XPK_employee", IntegerType(), True),
    StructField("FK_employees", IntegerType(), True),
    StructField("EMPLOYEE_ID", IntegerType(), True),
    StructField("FIRST_NAME", StringType(), True),
    StructField("LAST_NAME", StringType(), True),
    StructField("SALARY", DoubleType(), True),
    StructField("DEPARTMENT_ID", IntegerType(), True)
])

# Schema para hr_poc.csv
hr_schema = StructType([
    StructField("XPK_Department", IntegerType(), True),
    StructField("DEPT_ID", IntegerType(), True),
    StructField("DEPT_NAME", StringType(), True),
    StructField("XPK_Employee", IntegerType(), True),
    StructField("FK_Department", IntegerType(), True),
    StructField("EMP_ID", IntegerType(), True),
    StructField("FIRST_NAME", StringType(), True),
    StructField("LAST_NAME", StringType(), True),
    StructField("SALARY", DoubleType(), True)
])

print("✓ Schemas defined")
print(f"EMP Schema: {len(emp_schema.fields)} fields")
print(f"HR Schema: {len(hr_schema.fields)} fields")

# ═════════════════════════════════════════════════════════════════════════
# CELL 4: CARREGAR CSVs
# ═════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("LOADING CSV FILES")
print("═" * 60)

try:
    # Carregar emp_poc.csv
    df_emp = spark.read \
        .schema(emp_schema) \
        .option("header", "true") \
        .option("inferSchema", "false") \
        .csv(CSV_EMP)
    
    print(f"\n✓ EMP_POC loaded successfully")
    print(f"  Rows: {df_emp.count()}")
    print(f"  Columns: {len(df_emp.columns)}")
    print(f"  Schema:\n{df_emp.schema}")
    
except Exception as e:
    print(f"\n✗ Error loading EMP_POC: {str(e)}")
    raise

try:
    # Carregar hr_poc.csv
    df_hr = spark.read \
        .schema(hr_schema) \
        .option("header", "true") \
        .option("inferSchema", "false") \
        .csv(CSV_HR)
    
    print(f"\n✓ HR_POC loaded successfully")
    print(f"  Rows: {df_hr.count()}")
    print(f"  Columns: {len(df_hr.columns)}")
    print(f"  Schema:\n{df_hr.schema}")
    
except Exception as e:
    print(f"\n✗ Error loading HR_POC: {str(e)}")
    raise

# ═════════════════════════════════════════════════════════════════════════
# CELL 5: VISUALIZAR DADOS
# ═════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("DATA PREVIEW")
print("═" * 60)

print("\nEMP_POC (primeiro 3 registros):")
df_emp.show(3, truncate=False)

print("\nHR_POC (primeiro 3 registros):")
df_hr.show(3, truncate=False)

# ═════════════════════════════════════════════════════════════════════════
# CELL 6: VALIDAR DADOS
# ═════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("DATA VALIDATION")
print("═" * 60)

def validate_dataframe(df, name, expected_rows, expected_cols):
    """Valida integridade do DataFrame"""
    
    print(f"\n🔍 Validating {name}:")
    
    issues = []
    
    # Verificar row count
    actual_rows = df.count()
    if actual_rows != expected_rows:
        issues.append(f"Row count mismatch: {actual_rows} vs {expected_rows} expected")
    else:
        print(f"  ✓ Row count: {actual_rows} (expected: {expected_rows})")
    
    # Verificar column count
    actual_cols = len(df.columns)
    if actual_cols != expected_cols:
        issues.append(f"Column count mismatch: {actual_cols} vs {expected_cols} expected")
    else:
        print(f"  ✓ Column count: {actual_cols} (expected: {expected_cols})")
    
    # Verificar nulls
    null_counts = df.select([count(when(col(c).isNull(), c)).alias(c) for c in df.columns]).collect()[0]
    total_nulls = sum(null_counts.asDict().values())
    
    if total_nulls > 0:
        issues.append(f"Found {total_nulls} null values")
        print(f"  ⚠ Null values: {total_nulls}")
    else:
        print(f"  ✓ No null values")
    
    # Verificar duplicatas (chave primária)
    if name == "EMP_POC":
        dup_count = df.groupBy("XPK_employee").count().filter(col("count") > 1).count()
        if dup_count > 0:
            issues.append(f"Found {dup_count} duplicate XPK_employee values")
        else:
            print(f"  ✓ No duplicates on XPK_employee")
    
    if name == "HR_POC":
        dup_count = df.groupBy("XPK_Employee").count().filter(col("count") > 1).count()
        if dup_count > 0:
            issues.append(f"Found {dup_count} duplicate XPK_Employee values")
        else:
            print(f"  ✓ No duplicates on XPK_Employee")
    
    # Status geral
    if len(issues) == 0:
        print(f"  ✅ {name} VALID")
        return True
    else:
        print(f"  ❌ {name} INVALID - Issues found:")
        for issue in issues:
            print(f"     - {issue}")
        return False

# Executar validações
emp_valid = validate_dataframe(df_emp, "EMP_POC", expected_rows=8, expected_cols=7)
hr_valid = validate_dataframe(df_hr, "HR_POC", expected_rows=8, expected_cols=9)

# ═════════════════════════════════════════════════════════════════════════
# CELL 7: CRIAR TABELAS DELTA
# ═════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("CREATING DELTA TABLES")
print("═" * 60)

try:
    # Criar tabela emp_poc
    print(f"\n📝 Creating Delta table: {TABLE_EMP}")
    
    df_emp.write \
        .format("delta") \
        .mode("overwrite") \
        .option("path", f"{TABLES_PATH}/{TABLE_EMP}") \
        .saveAsTable(TABLE_EMP)
    
    print(f"✓ Table {TABLE_EMP} created successfully")
    
except Exception as e:
    print(f"✗ Error creating {TABLE_EMP}: {str(e)}")
    raise

try:
    # Criar tabela hr_poc
    print(f"\n📝 Creating Delta table: {TABLE_HR}")
    
    df_hr.write \
        .format("delta") \
        .mode("overwrite") \
        .option("path", f"{TABLES_PATH}/{TABLE_HR}") \
        .saveAsTable(TABLE_HR)
    
    print(f"✓ Table {TABLE_HR} created successfully")
    
except Exception as e:
    print(f"✗ Error creating {TABLE_HR}: {str(e)}")
    raise

# ═════════════════════════════════════════════════════════════════════════
# CELL 8: VERIFICAR TABELAS DELTA
# ═════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("VERIFYING DELTA TABLES")
print("═" * 60)

# Consultar tabelas via SQL
emp_count = spark.sql(f"SELECT COUNT(*) as count FROM {TABLE_EMP}").collect()[0][0]
hr_count = spark.sql(f"SELECT COUNT(*) as count FROM {TABLE_HR}").collect()[0][0]

print(f"\n✓ {TABLE_EMP}: {emp_count} rows")
print(f"✓ {TABLE_HR}: {hr_count} rows")

# Mostrar metadados das tabelas
try:
    emp_desc = spark.sql(f"DESCRIBE TABLE {TABLE_EMP}").collect()
    hr_desc = spark.sql(f"DESCRIBE TABLE {TABLE_HR}").collect()
    
    print(f"\n📋 {TABLE_EMP} Schema:")
    print("  " + "\n  ".join([f"{row[0]}: {row[1]}" for row in emp_desc]))
    
    print(f"\n📋 {TABLE_HR} Schema:")
    print("  " + "\n  ".join([f"{row[0]}: {row[1]}" for row in hr_desc]))
    
except Exception as e:
    print(f"Note: Could not retrieve schema details: {str(e)}")

# ═════════════════════════════════════════════════════════════════════════
# CELL 9: EXEMPLOS DE QUERIES
# ═════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("SAMPLE QUERIES")
print("═" * 60)

# Query 1: Total salary por department
print("\n1️⃣  Total salary per department (emp_poc):")
spark.sql(f"""
    SELECT 
        DEPARTMENT_ID,
        COUNT(*) as employee_count,
        SUM(SALARY) as total_salary,
        AVG(SALARY) as avg_salary
    FROM {TABLE_EMP}
    GROUP BY DEPARTMENT_ID
    ORDER BY DEPARTMENT_ID
""").show()

# Query 2: Employees por department (hr_poc)
print("\n2️⃣  Employees per department (hr_poc):")
spark.sql(f"""
    SELECT 
        DEPT_NAME,
        COUNT(*) as employee_count,
        SUM(SALARY) as total_salary
    FROM {TABLE_HR}
    GROUP BY DEPT_NAME
    ORDER BY DEPT_NAME
""").show()

# Query 3: Join entre tabelas
print("\n3️⃣  Salary distribution:")
spark.sql(f"""
    SELECT 
        SALARY,
        COUNT(*) as count
    FROM {TABLE_EMP}
    GROUP BY SALARY
    ORDER BY SALARY DESC
""").show()

# ═════════════════════════════════════════════════════════════════════════
# CELL 10: RELATÓRIO FINAL
# ═════════════════════════════════════════════════════════════════════════

print("\n" + "═" * 60)
print("IMPORT & TRANSFORMATION COMPLETE")
print("═" * 60)

summary = {
    "Timestamp": datetime.now().isoformat(),
    "Files Imported": 2,
    "Tables Created": 2,
    f"{TABLE_EMP} Rows": emp_count,
    f"{TABLE_HR} Rows": hr_count,
    "Validation Status": "✓ PASSED" if (emp_valid and hr_valid) else "⚠ WITH WARNINGS"
}

print("\n📊 SUMMARY:")
for key, value in summary.items():
    print(f"  {key}: {value}")

print("\n✅ NEXT STEPS:")
print("   1. Open your Lakehouse in Fabric")
print("   2. Navigate to Tables section")
print(f"   3. You'll see two new tables: {TABLE_EMP} and {TABLE_HR}")
print("   4. Click on each table to preview data")
print("   5. Use these tables in Power BI for analysis")
print(f"   6. Create relationships between {TABLE_EMP} and {TABLE_HR} if needed")

print("\n" + "═" * 60)
print("✨ FABRIC IMPORT SUCCESSFUL ✨")
print("═" * 60 + "\n")
