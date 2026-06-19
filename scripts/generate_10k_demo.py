#!/usr/bin/env python3
"""
Demo Version: Generate 10,000 synthetic employee records (without Spark)
For TESTING ONLY. Use the Jupyter notebook in Azure Fabric for production.
"""

import csv
import os
import random
from datetime import datetime

print("\n" + "=" * 70)
print("DEMO: HR Data Generation (CSV - No Spark Required)")
print("=" * 70)

# ==============================================================================
# STEP 1: Create Department Data
# ==============================================================================
print("\n📊 Creating departments...")
departments = [
    {"DEPT_ID": 10, "DEPT_NAME": "Data & AI", "LOCATION": "Sao Paulo"},
    {"DEPT_ID": 20, "DEPT_NAME": "Engineering", "LOCATION": "Rio de Janeiro"},
    {"DEPT_ID": 30, "DEPT_NAME": "Operations", "LOCATION": "Belo Horizonte"}
]
print(f"✓ Created {len(departments)} departments")
for dept in departments:
    print(f"  - {dept['DEPT_NAME']} (ID: {dept['DEPT_ID']})")

# ==============================================================================
# STEP 2: Generate 10,000 Synthetic Employees
# ==============================================================================
print("\n👥 Generating 10,000 synthetic employee records...")
num_records = 10000
employees = []
dept_ids = [10, 20, 30]

for emp_id in range(1, num_records + 1):
    # Randomly assign to department
    dept_id = random.choice(dept_ids)
    
    # Assign manager (hierarchy)
    # First 10 employees per dept are directors (no manager)
    # Rest report to them
    if emp_id % 100 <= 10:
        manager_id = None  # Director level
    else:
        manager_id = (emp_id // 10)  # Report to someone
    
    # Random salary between 7000-12000
    salary = random.randint(7000, 12000)
    
    employees.append({
        "XPK_Employee": emp_id,
        "FK_Department": dept_id,
        "EMP_ID": emp_id,
        "FIRST_NAME": f"Emp_{emp_id}",
        "LAST_NAME": "Synthetic",
        "SALARY": salary,
        "MANAGER_ID": manager_id
    })
    
    # Progress indicator every 1000 records
    if emp_id % 1000 == 0:
        print(f"  ✓ Generated {emp_id:,} records...")

print(f"✓ Generated {len(employees):,} total employees")

# ==============================================================================
# STEP 3: Create Department-Employee Mapping
# ==============================================================================
print("\n🔀 Creating department-employee mapping...")
final_data = []

for dept in departments:
    dept_id = dept["DEPT_ID"]
    dept_employees = [e for e in employees if e["FK_Department"] == dept_id]
    
    for emp in dept_employees:
        final_data.append({
            "XPK_Department": dept_id,
            "DEPT_ID": dept_id,
            "DEPT_NAME": dept["DEPT_NAME"],
            "LOCATION": dept["LOCATION"],
            "XPK_Employee": emp["XPK_Employee"],
            "FK_Department": emp["FK_Department"],
            "EMP_ID": emp["EMP_ID"],
            "FIRST_NAME": emp["FIRST_NAME"],
            "LAST_NAME": emp["LAST_NAME"],
            "SALARY": emp["SALARY"],
            "MANAGER_ID": emp["MANAGER_ID"] if emp["MANAGER_ID"] else ""
        })

print(f"✓ Mapped {len(final_data):,} records")

# ==============================================================================
# STEP 4: Data Quality Validation
# ==============================================================================
print("\n✅ DATA QUALITY VALIDATION")

# Count nulls/blanks
null_emps = sum(1 for e in final_data if not e["EMP_ID"])
print(f"  Null EMP_IDs: {null_emps}")

# Count directors vs staff
directors = sum(1 for e in final_data if e["MANAGER_ID"] == "")
staff = sum(1 for e in final_data if e["MANAGER_ID"] != "")
print(f"  Total records: {len(final_data)}")
print(f"  Directors (no manager): {directors}")
print(f"  Staff (with manager): {staff}")

# Salary stats
salaries = [e["SALARY"] for e in final_data]
print(f"  Salary range: ${min(salaries):,} - ${max(salaries):,}")
print(f"  Salary average: ${sum(salaries) / len(salaries):,.0f}")

# Department distribution
dept_counts = {}
for e in final_data:
    dept = e["DEPT_NAME"]
    dept_counts[dept] = dept_counts.get(dept, 0) + 1

print("\n  Department distribution:")
for dept, count in sorted(dept_counts.items()):
    print(f"    - {dept}: {count:,} employees")

# ==============================================================================
# STEP 5: Write to CSV
# ==============================================================================
print("\n💾 Writing output to CSV...")
output_dir = "./output/hr_poc_10k"
os.makedirs(output_dir, exist_ok=True)

csv_path = os.path.join(output_dir, "hr_poc_10k_data.csv")

# Write CSV with headers
fieldnames = [
    "XPK_Department", "DEPT_ID", "DEPT_NAME", "LOCATION",
    "XPK_Employee", "FK_Department", "EMP_ID", "FIRST_NAME", "LAST_NAME", "SALARY", "MANAGER_ID"
]

with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(final_data)

file_size = os.path.getsize(csv_path) / (1024 * 1024)  # MB
print(f"✓ CSV written to: {csv_path}")
print(f"✓ File size: {file_size:.2f} MB")
print(f"✓ Records: {len(final_data):,}")

# ==============================================================================
# STEP 6: Create Sample Preview
# ==============================================================================
print("\n📋 SAMPLE PREVIEW (first 10 records):")
print("-" * 80)
for i, record in enumerate(final_data[:10], 1):
    print(f"{i}. {record['FIRST_NAME']:15} | Dept: {record['DEPT_NAME']:15} | Salary: ${record['SALARY']:>6} | Manager: {record['MANAGER_ID'] if record['MANAGER_ID'] else 'N/A'}")

# ==============================================================================
# STEP 7: Summary
# ==============================================================================
print("\n" + "=" * 70)
print("📈 EXECUTION SUMMARY")
print("=" * 70)
print(f"  ✓ Generated {len(final_data):,} employee records")
print(f"  ✓ {len(departments)} departments")
print(f"  ✓ Output format: CSV")
print(f"  ✓ Output location: {output_dir}")
print(f"  ✓ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

print("\n✨ Data generation complete!")
print("\n📌 IMPORTANT NOTES:")
print("  • This is a DEMO version without Spark")
print("  • For production: Use the Jupyter notebook in Azure Fabric")
print("  • CSV file is ready for testing and validation")
print("  • Next steps:")
print("    1. ✓ Validate CSV in ./output/hr_poc_10k")
print("    2. Import into Power BI for visualization")
print("    3. Use with Informatica POC workflows")
print("    4. Test with original data pipelines")

print("\n" + "=" * 70 + "\n")
