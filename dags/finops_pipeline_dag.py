"""Day 15: Airflow DAG for the daily FinOps pipeline.
ingest -> data quality gate -> warehouse load -> reconciliation -> (unit economics || anomaly detection) -> alert summary.
Runs the project's scripts with BashOperator. Project is mounted at /opt/airflow/project (see docker-compose.airflow.yml)."""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

PROJECT = "/opt/airflow/project"
default_args = {"owner": "finops", "retries": 2, "retry_delay": timedelta(minutes=5), "email_on_failure": False}

def run(script):
    return f"cd {PROJECT} && python {script}"

with DAG(
    dag_id="finops_pipeline",
    description="Daily cloud billing ingestion, quality checks, warehouse load and anomaly alerting",
    default_args=default_args,
    start_date=datetime(2026, 11, 1),
    schedule="0 6 * * *",          # every day at 06:00
    catchup=False,
    max_active_runs=1,
    tags=["finops", "data-engineering"],
) as dag:
    start = EmptyOperator(task_id="start")
    ingest = BashOperator(task_id="ingest_billing", bash_command=run("src/ingest_billing.py"))
    # The validation script exits non-zero only on unexpected errors; failed DQ checks are quarantined, not fatal.
    validate = BashOperator(task_id="validate_data_quality", bash_command=run("src/validate_data.py"))
    load = BashOperator(task_id="load_warehouse", bash_command=run("src/load_warehouse.py"))
    reconcile = BashOperator(task_id="reconcile", bash_command=run("src/reconcile.py"))   # non-zero exit if row counts/checksums differ
    unit_econ = BashOperator(task_id="transform_unit_economics", bash_command=run("src/unit_economics.py"))
    anomalies = BashOperator(task_id="detect_anomalies", bash_command=run("src/anomaly_engine.py"),
                             env={"WEBHOOK_URL": "{{ var.value.get('finops_webhook_url', '') }}"}, append_env=True)
    end = EmptyOperator(task_id="end")

    start >> ingest >> validate >> load >> reconcile >> [unit_econ, anomalies] >> end
