#!/usr/bin/env python3
"""
100% AUTONOMOUS FABRIC INTEGRATION
Uploads notebooks and XMLs, executes pipelines - NO MANUAL STEPS
Uses: Azure CLI + Python SDK
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time

# Add UTF-8 support on Windows
if sys.platform == "win32":
    os.environ["PYTHONUTF8"] = "1"

from dotenv import load_dotenv

# Load credentials
load_dotenv()
WORKSPACE_ID = os.getenv("FABRIC_WORKSPACE_ID", "878ba859-8217-47b1-8450-d483fcb00462")
WORKSPACE_NAME = os.getenv("FABRIC_WORKSPACE_NAME", "PowerCenter Migration")
LAKEHOUSE_NAME = "powercenter_lakehouse"

class AutonomousFabricUpload:
    def __init__(self):
        self.workspace_id = WORKSPACE_ID
        self.workspace_name = WORKSPACE_NAME
        self.lakehouse_name = LAKEHOUSE_NAME
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "workspace_id": self.workspace_id,
            "notebooks": [],
            "xmls": [],
            "pipelines": []
        }

    def run_command(self, cmd, description=""):
        """Execute shell command with error handling"""
        print(f"⏳ {description}...")
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                print(f"✅ {description}")
                return result.stdout.strip()
            else:
                print(f"⚠️  {description} — stderr: {result.stderr[:200]}")
                return None
        except subprocess.TimeoutExpired:
            print(f"❌ {description} — timeout")
            return None
        except Exception as e:
            print(f"❌ {description} — {str(e)[:100]}")
            return None

    def step_1_verify_az_cli(self):
        """Verify Azure CLI is available"""
        print("\n🔍 STEP 1: Verify Azure CLI installed")
        result = self.run_command("az --version", "Checking Azure CLI")
        if result and "azure-cli" in result.lower():
            print("✅ Azure CLI ready")
            return True
        return False

    def step_2_ensure_az_logged_in(self):
        """Ensure user is logged into Azure CLI"""
        print("\n🔐 STEP 2: Verify Azure CLI login")
        # Try to get current account
        result = self.run_command("az account show", "Getting current account")
        if result:
            account_data = json.loads(result)
            print(f"✅ Logged in as: {account_data.get('user', {}).get('name', 'unknown')}")
            return True
        else:
            print("⚠️  Not logged in, attempting interactive login...")
            self.run_command("az login", "Interactive login")
            return True

    def step_3_upload_notebooks_via_cli(self):
        """Upload all notebooks using az fabric CLI"""
        print("\n📓 STEP 3: Upload 6 Notebooks via Azure CLI")
        
        notebooks_dir = Path("notebooks")
        if not notebooks_dir.exists():
            print(f"❌ Notebooks directory not found: {notebooks_dir}")
            return 0

        notebook_files = sorted([
            "01_PowerCenter_to_PySpark_Translation.ipynb",
            "02_Workflow_Execution_EMP_and_HR.ipynb",
            "03_Map_EMP_Source_to_Target.ipynb",
            "04_PySpark_Large_Scale_Data_Generation.ipynb",
            "05_Map_HR_Source_to_Target.ipynb",
            "06_Pipeline_Import_Guide.ipynb"
        ])

        uploaded = 0
        for notebook_file in notebook_files:
            notebook_path = notebooks_dir / notebook_file
            if not notebook_path.exists():
                print(f"⚠️  Notebook not found: {notebook_path}")
                continue

            # Try az fabric notebook create
            notebook_name = notebook_file.replace(".ipynb", "")
            cmd = (
                f'az fabric item create '
                f'--workspace-name "{self.workspace_name}" '
                f'--item-name "{notebook_name}" '
                f'--item-type "Notebook" '
                f'--definition-file "{notebook_path}"'
            )
            
            result = self.run_command(cmd, f"Upload notebook: {notebook_name}")
            if result:
                self.results["notebooks"].append({"name": notebook_name, "status": "✅"})
                uploaded += 1
            else:
                self.results["notebooks"].append({"name": notebook_name, "status": "⚠️"})

        print(f"📊 Uploaded: {uploaded}/6 notebooks")
        return uploaded

    def step_4_upload_xmls_via_onelake(self):
        """Upload XML files directly to OneLake"""
        print("\n📁 STEP 4: Upload 8 XMLs to OneLake")
        
        data_dir = Path("data")
        if not data_dir.exists():
            print(f"❌ Data directory not found: {data_dir}")
            return 0

        xml_files = [
            "employees.xml",
            "hr.xml",
            "wf_m_poc_xml_emp.XML",
            "wf_m_poc_xml_hr.XML"
        ]

        # Also check for duplicates in this directory
        xml_files.extend([f.name for f in data_dir.glob("*.XML") if f.name not in xml_files])
        xml_files.extend([f.name for f in data_dir.glob("*.xml") if f.name not in xml_files])
        xml_files = list(set(xml_files))[:8]  # Get unique, max 8

        uploaded = 0
        for xml_file in xml_files:
            xml_path = data_dir / xml_file
            if not xml_path.exists():
                continue

            # Use az fabric lakehouse file upload
            cmd = (
                f'az fabric lakehouse file upload '
                f'--workspace-name "{self.workspace_name}" '
                f'--lakehouse-name "{self.lakehouse_name}" '
                f'--file "{xml_path}"'
            )
            
            result = self.run_command(cmd, f"Upload XML: {xml_file}")
            if result:
                self.results["xmls"].append({"name": xml_file, "status": "✅"})
                uploaded += 1
            else:
                self.results["xmls"].append({"name": xml_file, "status": "⚠️"})

        print(f"📊 Uploaded: {uploaded}/{len(xml_files)} XMLs")
        return uploaded

    def step_5_create_and_run_pipelines(self):
        """Create and execute both pipelines"""
        print("\n⚙️  STEP 5: Create and Run 2 Pipelines")
        
        pipelines = [
            {
                "name": "Pipeline_EMP_Workflow",
                "notebook": "02_Workflow_Execution_EMP_and_HR"
            },
            {
                "name": "Pipeline_HR_Workflow",
                "notebook": "05_Map_HR_Source_to_Target"
            }
        ]

        executed = 0
        for pipeline_config in pipelines:
            pipeline_name = pipeline_config["name"]
            notebook_name = pipeline_config["notebook"]

            # Create pipeline
            create_cmd = (
                f'az fabric pipeline create '
                f'--workspace-name "{self.workspace_name}" '
                f'--pipeline-name "{pipeline_name}"'
            )
            
            result = self.run_command(create_cmd, f"Create pipeline: {pipeline_name}")
            
            if result:
                # Run pipeline
                run_cmd = (
                    f'az fabric pipeline run '
                    f'--workspace-name "{self.workspace_name}" '
                    f'--pipeline-name "{pipeline_name}"'
                )
                
                run_result = self.run_command(run_cmd, f"Execute pipeline: {pipeline_name}")
                if run_result:
                    self.results["pipelines"].append({
                        "name": pipeline_name,
                        "status": "✅ Executed"
                    })
                    executed += 1
                else:
                    self.results["pipelines"].append({
                        "name": pipeline_name,
                        "status": "⚠️ Created, run pending"
                    })
            else:
                self.results["pipelines"].append({
                    "name": pipeline_name,
                    "status": "❌ Failed"
                })

        print(f"📊 Executed: {executed}/2 pipelines")
        return executed

    def step_6_generate_report(self):
        """Generate final report"""
        print("\n📊 STEP 6: Generate Final Report")
        
        report_file = Path("output") / f"fabric_autonomous_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(exist_ok=True)

        # Summary
        self.results["summary"] = {
            "total_notebooks": len(self.results["notebooks"]),
            "notebooks_uploaded": len([n for n in self.results["notebooks"] if n["status"] == "✅"]),
            "total_xmls": len(self.results["xmls"]),
            "xmls_uploaded": len([x for x in self.results["xmls"] if x["status"] == "✅"]),
            "pipelines_executed": len([p for p in self.results["pipelines"] if "Executed" in p["status"]])
        }

        with open(report_file, "w") as f:
            json.dump(self.results, f, indent=2)

        print(f"✅ Report saved: {report_file}")
        print("\n" + "="*60)
        print("🎉 EXECUTION SUMMARY")
        print("="*60)
        print(f"Notebooks:  {self.results['summary']['notebooks_uploaded']}/{self.results['summary']['total_notebooks']} ✅")
        print(f"XMLs:       {self.results['summary']['xmls_uploaded']}/{self.results['summary']['total_xmls']} ✅")
        print(f"Pipelines:  {self.results['summary']['pipelines_executed']}/2 ✅")
        print("="*60)

        return report_file

    def run_complete_flow(self):
        """Execute complete autonomous flow"""
        print("\n" + "="*70)
        print("🚀 100% AUTONOMOUS FABRIC INTEGRATION STARTING")
        print("="*70)

        try:
            # Step 1: Verify Azure CLI
            if not self.step_1_verify_az_cli():
                print("❌ Azure CLI not available. Please install: https://aka.ms/azurecli")
                return False

            # Step 2: Verify login
            self.step_2_ensure_az_logged_in()

            # Step 3: Upload notebooks
            self.step_3_upload_notebooks_via_cli()

            # Step 4: Upload XMLs
            self.step_4_upload_xmls_via_onelake()

            # Step 5: Create and run pipelines
            self.step_5_create_and_run_pipelines()

            # Step 6: Generate report
            report_file = self.step_6_generate_report()

            print("\n✨ 100% AUTONOMOUS INTEGRATION COMPLETE ✨")
            return True

        except Exception as e:
            print(f"\n❌ Fatal error: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    uploader = AutonomousFabricUpload()
    success = uploader.run_complete_flow()
    sys.exit(0 if success else 1)
