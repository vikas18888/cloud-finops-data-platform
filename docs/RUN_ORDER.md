# Run order (from the project root folder)

Week 1:  generate_data -> ingest_billing -> load_warehouse -> run_queries -> profile_costs -> benchmark_indexes -> validate_data -> reconcile
Week 2:  unit_economics -> audit_untagged -> export_flat -> anomaly_engine -> k8s_rightsizing -> build_rate_model -> audit_summary

Example: python src/unit_economics.py
Tests:   python -m unittest discover -s tests -p "test_*.py" -t .   (or: python -m unittest tests.test_etl tests.test_anomaly)

IMPORTANT: re-run generate_data.py first if you have an older copy (resource IDs were fixed so each service has unique IDs).

Week 3:  run_pipeline (Day 15) -> depreciation (16) -> build_storage_model (19) -> export_dashboard_pdf (18) -> draw_architecture (20) -> build_excel_log (21)
Optional: pip install streamlit ; streamlit run dashboard/app.py      |      docker compose -f docker-compose.airflow.yml up
