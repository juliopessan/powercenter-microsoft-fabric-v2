# ⚡ Quick Start: Importar em 15 Minutos

**Tempo Total:** ~15 minutos  
**Pré-requisitos:** Workspace Fabric + Lakehouse padrão + XMLs uploadados  
**Resultado:** 2 notebooks + 2 pipelines prontos para executar

---

## 🚀 Início Rápido (Sem Configurações Complexas)

### ✅ Step 1: Upload dos XMLs (2 min)

```
Fabric Workspace
  └─ seu-workspace
      └─ Lakehouse (default)
          └─ Files/ 📁
              ├─ employees.xml ✓ (copie de aqui →)
              │   ../employees.xml
              └─ hr.xml ✓ (copie de aqui →)
                  ../hr.xml
```

**Via UI:**
1. Abra seu **Lakehouse padrão**
2. Clique em **Files**
3. Clique em **Upload**
4. Selecione `employees.xml` e `hr.xml`
5. **Aguarde completar** ✓

---

### ✅ Step 2: Criar Notebook EMP (3 min)

**Via UI - Super Simples:**

1. **Workspace → + New → Notebook**
2. Nome: `03_Map_EMP_Source_to_Target`
3. **Na primeira célula**, copie TODO este código:

```python
# ============================================================================
# FABRIC NOTEBOOK: EMP Map (wf_m_poc_xml_emp)
# ============================================================================

from pyspark.sql.functions import col, trim, upper, cast
from pyspark.sql.types import ByteType, ShortType, StringType

# 1. LER XML
print("📥 Reading employees.xml...")
df_source = spark.read.format("xml").option("rowTag", "employee") \
    .load("/lakehouse/default/Files/employees.xml")
print(f"✓ Loaded: {df_source.count()} records")

# 2. TRANSFORMAR
print("🔄 Transforming...")
df_transformed = df_source.select(
    cast(col("EMPLOYEE_ID"), ByteType()).alias("EMPLOYEE_ID"),
    trim(upper(col("FIRST_NAME"))).alias("FIRST_NAME"),
    trim(upper(col("LAST_NAME"))).alias("LAST_NAME"),
    cast(col("SALARY"), ShortType()).alias("SALARY"),
    cast(col("DEPARTMENT_ID"), ByteType()).alias("DEPARTMENT_ID")
)

# 3. VALIDAR
print("✅ Validating...")
nulls = df_transformed.filter(col("EMPLOYEE_ID").isNull()).count()
dups = df_transformed.count() - df_transformed.select("EMPLOYEE_ID").distinct().count()
print(f"  Nulls: {nulls} | Duplicates: {dups}")

# 4. SALVAR
print("📤 Writing to emp_poc_target...")
df_transformed.coalesce(1).write.format("csv").mode("overwrite") \
    .option("header", "true").save("/lakehouse/default/Files/emp_poc_target")

# 5. TABELA DELTA (opcional)
try:
    spark.sql("DROP TABLE IF EXISTS emp_poc")
    df_transformed.write.format("delta").mode("overwrite").saveAsTable("emp_poc")
    print("✓ Delta table created: emp_poc")
except:
    print("⚠️ Delta table skipped")

print("=" * 60)
print("✅ SUCCESS - EMP Map Completed")
print("=" * 60)
```

4. **Ctrl+S** para salvar
5. Clique em **Run all** para testar ✓

---

### ✅ Step 3: Criar Notebook HR (3 min)

**Via UI - Mesmo processo:**

1. **Workspace → + New → Notebook**
2. Nome: `05_Map_HR_Source_to_Target`
3. **Na primeira célula**, copie TODO este código:

```python
# ============================================================================
# FABRIC NOTEBOOK: HR Map (wf_m_poc_xml_hr) - Hierarchical
# ============================================================================

from pyspark.sql.functions import col, trim, upper, cast, explode, count, avg, round, max, min
from pyspark.sql.types import ByteType, ShortType, StringType

# 1. LER XML HIERÁRQUICO
print("📥 Reading hr.xml (hierarchical)...")
df_source = spark.read.format("xml").option("rowTag", "Department") \
    .load("/lakehouse/default/Files/hr.xml")
print(f"✓ Loaded: {df_source.count()} departments")

# 2. FLATTEN (explode)
print("🔄 Flattening hierarchical data...")
df_flattened = df_source.select(
    col("DEPT_ID"),
    col("DEPT_NAME"),
    explode(col("Employees.Employee")).alias("employee")
).select(
    col("DEPT_ID"),
    col("DEPT_NAME"),
    col("employee.EMP_ID"),
    col("employee.FIRST_NAME"),
    col("employee.LAST_NAME"),
    col("employee.SALARY")
)
print(f"✓ Flattened: {df_flattened.count()} employees")

# 3. TRANSFORMAR
print("🔄 Transforming types...")
df_transformed = df_flattened.select(
    cast(col("DEPT_ID"), ByteType()).alias("DEPT_ID"),
    trim(upper(col("DEPT_NAME"))).alias("DEPT_NAME"),
    cast(col("EMP_ID"), ByteType()).alias("EMP_ID"),
    trim(upper(col("FIRST_NAME"))).alias("FIRST_NAME"),
    trim(upper(col("LAST_NAME"))).alias("LAST_NAME"),
    cast(col("SALARY"), ShortType()).alias("SALARY")
)

# 4. VALIDAR HIERARQUIA
print("✅ Validating hierarchical relationships...")
dept_summary = df_transformed.groupBy("DEPT_ID", "DEPT_NAME").agg(
    count("EMP_ID").alias("emp_count"),
    round(avg("SALARY"), 2).alias("avg_sal")
).orderBy("DEPT_ID")
dept_summary.show()

# 5. SALVAR
print("📤 Writing to hr_poc_target...")
df_transformed.coalesce(1).write.format("csv").mode("overwrite") \
    .option("header", "true").save("/lakehouse/default/Files/hr_poc_target")

# 6. TABELAS DELTA (opcional)
try:
    spark.sql("DROP TABLE IF EXISTS hr_departments")
    spark.sql("DROP TABLE IF EXISTS hr_employees")
    df_transformed.select("DEPT_ID", "DEPT_NAME").distinct() \
        .write.format("delta").mode("overwrite").saveAsTable("hr_departments")
    df_transformed.write.format("delta").mode("overwrite").saveAsTable("hr_employees")
    print("✓ Delta tables created: hr_departments, hr_employees")
except:
    print("⚠️ Delta tables skipped")

print("=" * 60)
print("✅ SUCCESS - HR Map Completed (Flattened)")
print("=" * 60)
```

4. **Ctrl+S** para salvar
5. Clique em **Run all** para testar ✓

---

### ✅ Step 4: Criar Pipeline EMP (3 min)

**Via UI - Simples:**

1. **Workspace → + New → Data Pipeline**
2. Nome: `wf_m_poc_xml_emp`
3. **Clique em "Edit"** (ou já está em modo edit)
4. Na esquerda, clique em **Canvas** (se não estiver)
5. Arraste componentes do lado esquerdo:
   - **Start** (1× encontre e arraste)
   - **Notebook Activity** (1× para a execução)
   - **Notebook Activity** (1× para validação)
   - **Notebook Activity** (1× para erro)
   - **End Success** (1×)
   - **End Failed** (1×)

6. **Configure cada atividade:**

#### Activity 1: Execute_EMP_Map
```
- Clique na atividade
- Nome: Execute_EMP_Map
- Notebook: 03_Map_EMP_Source_to_Target
- Timeout: 30 minutos
- Conexão de sucesso → Activity 2 (Validate)
- Conexão de falha → Activity 3 (Error)
```

#### Activity 2: Validate_EMP_Data
```
- Nome: Validate_EMP_Data
- Notebook: 02_Workflow_Execution_EMP_and_HR (use existente)
- Timeout: 15 minutos
- Conexão de sucesso → End Success
- Conexão de falha → Activity 3 (Error)
```

#### Activity 3: Handle_Error
```
- Nome: Handle_Error
- Notebook: 02_Workflow_Execution_EMP_and_HR
- Timeout: 10 minutos
- Conexão de sucesso → End Failed
```

7. **Ctrl+S** para salvar ✓

---

### ✅ Step 5: Criar Pipeline HR (3 min)

**Mesmo processo que o passo 4:**

1. **Workspace → + New → Data Pipeline**
2. Nome: `wf_m_poc_xml_hr`
3. **Edit Mode**
4. Arraste componentes:
   - Start
   - Notebook Activity (Execute_HR_Map)
   - Notebook Activity (Validate_HR_Data)
   - Notebook Activity (Optional_Scale_10K)
   - Notebook Activity (Handle_Error)
   - End Success / End Failed

5. **Configure cada atividade:**

#### Activity 1: Execute_HR_Map
```
- Notebook: 05_Map_HR_Source_to_Target
- Timeout: 30 min
- Sucesso → Activity 2
- Falha → Activity 4 (Error)
```

#### Activity 2: Validate_HR_Data
```
- Notebook: 02_Workflow_Execution_EMP_and_HR
- Timeout: 15 min
- Sucesso → Activity 3 (Scale)
- Falha → Activity 4 (Error)
```

#### Activity 3: Optional_Scale_10K
```
- Notebook: 04_PySpark_Large_Scale_Data_Generation
- Timeout: 20 min
- Sucesso → End Success
- Falha → End Success (não bloqueia)
```

#### Activity 4: Handle_Error
```
- Notebook: 02_Workflow_Execution_EMP_and_HR
- Timeout: 10 min
- Sucesso → End Failed
```

6. **Ctrl+S** para salvar ✓

---

## ✨ Validação Final (2 min)

### Test 1: Testar Notebook EMP isolado
```
1. Vá para: Notebooks → 03_Map_EMP_Source_to_Target
2. Clique "Run all"
3. Aguarde a output:
   ✓ Loaded: 8 records
   ✓ Validating...
   ✓ SUCCESS - EMP Map Completed
```

### Test 2: Testar Notebook HR isolado
```
1. Vá para: Notebooks → 05_Map_HR_Source_to_Target
2. Clique "Run all"
3. Aguarde a output:
   ✓ Loaded: 3 departments
   ✓ Flattened: 8 employees
   ✓ SUCCESS - HR Map Completed
```

### Test 3: Testar Pipeline EMP
```
1. Vá para: Pipelines → wf_m_poc_xml_emp
2. Clique "Run" (play button no topo)
3. Monitore:
   [Start] → [Execute_EMP_Map ✓] → [Validate ✓] → [Success ✓]
4. Tempo esperado: ~10-15 segundos
```

### Test 4: Testar Pipeline HR
```
1. Vá para: Pipelines → wf_m_poc_xml_hr
2. Clique "Run"
3. Monitore:
   [Start] → [Execute_HR_Map ✓] → [Validate ✓] → [Scale 10K] → [Success ✓]
4. Tempo esperado: ~25-35 segundos (com scale: ~45s)
```

---

## 📊 Verificar Outputs (2 min)

### Via SQL Editor no Fabric:

```sql
-- 1. Verificar CSVs gerados
SELECT * FROM emp_poc_target LIMIT 5;
SELECT * FROM hr_poc_target LIMIT 5;

-- 2. Contar registros
SELECT COUNT(*) FROM emp_poc_target;  -- Esperado: 8
SELECT COUNT(*) FROM hr_poc_target;   -- Esperado: 8

-- 3. Resumo por departamento (HR)
SELECT DEPT_ID, DEPT_NAME, COUNT(*) 
FROM hr_poc_target 
GROUP BY DEPT_ID, DEPT_NAME;
```

---

## ✅ Checklist Final

- ☐ XMLs uploadados em `/lakehouse/default/Files/`
- ☐ Notebook `03_Map_EMP_Source_to_Target` criado e testado
- ☐ Notebook `05_Map_HR_Source_to_Target` criado e testado
- ☐ Pipeline `wf_m_poc_xml_emp` criado com 3 atividades
- ☐ Pipeline `wf_m_poc_xml_hr` criado com 4 atividades
- ☐ Ambas pipelines executadas com sucesso
- ☐ Outputs validados: 8 registros cada

---

## 🎯 Resultado Final

```
Fabric Workspace
├── Notebooks/ 📓
│   ├── 02_Workflow_Execution_EMP_and_HR (existente)
│   ├── 03_Map_EMP_Source_to_Target ✅ NOVO
│   ├── 04_PySpark_Large_Scale_Data_Generation (existente)
│   └── 05_Map_HR_Source_to_Target ✅ NOVO
│
├── Pipelines/ 🔗
│   ├── wf_m_poc_xml_emp ✅ NOVO (3 atividades)
│   └── wf_m_poc_xml_hr ✅ NOVO (4 atividades)
│
└── Lakehouse/ 📁
    └── /Files
        ├── employees.xml
        ├── hr.xml
        ├── emp_poc_target/ ✅ (8 records)
        └── hr_poc_target/ ✅ (8 records flattened)
```

---

## 🚀 Próximos Passos Opcionais

1. **Agendar Pipelines** → Configure execução diária/horária
2. **Configurar Alertas** → Notifique em caso de falha
3. **Integrar Power BI** → Crie relatórios sobre os dados
4. **Escalar para 10K** → Execute `04_PySpark_Large_Scale` com scale factor
5. **Versionamento** → Use Git para rastrear mudanças

---

## 📞 Dúvidas Rápidas?

| Problema | Solução |
|----------|---------|
| Notebook não encontra XML | Verifique que XMLs estão em `/lakehouse/default/Files/` |
| Pipeline trava no notebook | Clique na atividade → Output para ver o erro |
| Dados não aparecem em `emp_poc_target` | Verifique Lakehouse → Files → procure por pasta `emp_poc_target` |
| Erro de tipo de dados | Confirme XMLs têm schema correto (EMPLOYEE_ID: byte, SALARY: short) |

---

✨ **Pronto!** Seus workflows PowerCenter estão agora rodando em Fabric.

