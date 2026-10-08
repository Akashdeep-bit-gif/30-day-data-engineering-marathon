import sys
import os
import logging
import time
import subprocess

# Configure Master Pipeline Logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/pipeline_orchestrator.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def run_stage(stage_name, script_path):
    print(f"\n▶️ Running {stage_name} ({script_path})...")
    logging.info(f"Executing stage: {stage_name}")
    
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
        logging.info(f"Stage '{stage_name}' completed successfully.")
    else:
        print(result.stdout)
        print(result.stderr)
        logging.error(f"Stage '{stage_name}' failed with return code {result.returncode}.")
        raise Exception(f"Stage failed: {stage_name}\nError: {result.stderr}")

def run_full_pipeline():
    print("🚀 =====================================================")
    print("🚀 STARTING END-TO-END DATA ENGINEERING ETL PIPELINE")
    print("🚀 =====================================================")
    logging.info("Starting End-to-End Data Engineering Pipeline Execution.")

    start_time = time.time()

    try:
        # Phase 1: API Ingestion
        run_stage("Phase 1: API Ingestion", "code/day-01-api-ingest/extract.py")

        # Phase 2: Staging Database Load
        run_stage("Phase 2: Staging DB Load", "code/day-02-db-stage/load_staging.py")

        # Phase 3: Analytics Transformation
        run_stage("Phase 3: Analytics Transformation", "code/day-03-transform/transform_data.py")

        # Phase 4: Daily Summary Aggregation
        run_stage("Phase 4: Daily Aggregations", "code/day-04-aggregate/aggregate_daily.py")

        # Phase 5: Data Quality Validation
        run_stage("Phase 5: Quality Audit", "code/day-05-quality/validate_data.py")

        duration = round(time.time() - start_time, 2)
        print("=====================================================")
        print(f"🎉 PIPELINE EXECUTION SUCCESSFUL! Total Duration: {duration} seconds")
        print("=====================================================")
        logging.info(f"Pipeline finished successfully in {duration} seconds.")

    except Exception as e:
        err_msg = f"❌ PIPELINE FAILURE: Execution failed: {e}"
        print(err_msg)
        logging.error(err_msg)
        sys.exit(1)

if __name__ == "__main__":
    run_full_pipeline()