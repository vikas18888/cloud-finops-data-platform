"""Run the full FinOps pipeline locally, in the same task order as the Airflow DAG (dags/finops_pipeline_dag.py).
Stops at the first failing task, like an orchestrator would."""
import subprocess, sys, time

TASKS = [  # (task_id, command)
    ("ingest_billing", "src/ingest_billing.py"),
    ("validate_data_quality", "src/validate_data.py"),
    ("load_warehouse", "src/load_warehouse.py"),
    ("reconcile", "src/reconcile.py"),
    ("transform_unit_economics", "src/unit_economics.py"),
    ("detect_anomalies", "src/anomaly_engine.py"),
]

def main():
    results = []
    for task_id, script in TASKS:
        start = time.time()
        p = subprocess.run([sys.executable, script], capture_output=True, text=True)
        ok = p.returncode == 0
        results.append((task_id, ok, time.time() - start))
        print(f"[{'OK' if ok else 'FAILED'}] {task_id} ({results[-1][2]:.1f}s)")
        if not ok:
            print(p.stdout[-800:], p.stderr[-800:]); sys.exit(1)
    print(f"Pipeline finished: {len(results)} tasks succeeded")

if __name__ == "__main__":
    main()
