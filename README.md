# Walmart DBT, Airflow & Databricks Analytics Pipeline

A portfolio data engineering project that demonstrates how change data capture (CDC), cloud data processing, analytics engineering, and workflow orchestration can work together in a modern data stack.

The pipeline ingests changes from a source Agentic database into a Databricks catalog, transforms and tests the data with dbt, and schedules the end-to-end workflow with Apache Airflow.


<img width="1183" height="544" alt="Walmaet_arch" src="https://github.com/user-attachments/assets/234724bb-99e3-495f-bab0-041b26a54fd7" />


> The diagram shows the logical data flow. Airflow triggers the Databricks ingestion job and coordinates the dbt steps; Databricks is the storage and processing platform.

## Pipeline

The `orchestrate` Airflow DAG runs daily at **09:00 UTC** (`0 9 * * *`) with catchup disabled. Its tasks run in sequence:

1. **Ingest** — trigger the Databricks job that loads CDC changes from the source database into the `walmart.bronze` catalog schema, then wait for the run to finish.
2. **Check source freshness** — invoke `dbt source freshness`.
3. **Build and test Silver Technical** — create dbt models for source entities and run data quality tests.
4. **Build and test Silver Business** — create the business-level One Big Table (OBT) and run its tests.
5. **Prepare Gold models** — build ephemeral models used by the Gold layer.
6. **Capture dimension history** — run dbt snapshots for customers, employees, orders, products, and stores.
7. **Build the fact model** — materialize `fact_orders` from the business-level model.

## Data layers

| Layer | Purpose | Implementation |
| --- | --- | --- |
| **Bronze** | Land source changes with minimal transformation. | Databricks CDC ingestion job writes to `walmart.bronze`. |
| **Silver Technical** | Create typed, cleaned entity models from Bronze source tables. | dbt models for customers, employees, order items, orders, products, and stores. |
| **Silver Business** | Combine technical models into a business-facing One Big Table. | dbt `obt_b` model. |
| **Gold** | Provide analytics-ready historical dimensions and a fact model. | Timestamp-based dbt snapshots, ephemeral models, and `fact_orders`. |

The `fact_orders` model exposes order, customer, product, store, employee, and order-item identifiers alongside quantity, unit price, line amount, and total amount. Dimension snapshots retain historical versions using each entity's update timestamp and unique key.

## Data quality

The project uses dbt tests to check `not_null` and `unique` constraints on entity identifiers in the Silver Technical models. The products model also applies a conditional uniqueness test to products with a positive price. Airflow runs the Silver Technical and Silver Business test steps as part of the daily workflow.

## Technology

- **Databricks** — CDC ingestion, data catalog, and cloud data platform
- **dbt Core** — SQL transformations, tests, snapshots, and model organization
- **dbt-databricks** — dbt adapter for Databricks
- **Apache Airflow** — scheduled orchestration and task monitoring
- **Docker Compose** — local Airflow services
- **Python** — Databricks Jobs SDK utility used by the ingestion task

The project is intended as a practical, low-cost learning and portfolio example. Availability, limits, and pricing depend on the selected Databricks and hosting plans; verify current provider terms before deployment.

## Repository layout

```text
.
├── README.md
├── walmart_dbt_airflow/
│   ├── dags/
│   │   ├── databricks_job_utils.py
│   │   └── orchestrate.py
│   ├── docker-compose.yaml
│   ├── Dockerfile
│   └── walmart_project/
│       ├── dbt_project.yml
│       ├── models/
│       │   ├── source/
│       │   ├── silver_t/
│       │   ├── silver_b/
│       │   └── gold/
│       ├── snapshots/
│       ├── macros/
│       └── tests/
└── walmart_project/  # dbt project files also present at repository root
```

## Configuration and security

Before running the pipeline, configure:

- A Databricks workspace, a CDC ingestion job, and permissions for the identity used by Airflow.
- `DATABRICKS_HOST` and `DATABRICKS_TOKEN` for the Databricks SDK utility.
- A dbt profile for the `walmart_project` profile, with credentials supplied through environment variables or a secrets manager.
- Airflow's required configuration and secrets for the chosen deployment.

Do not commit access tokens, passwords, Fernet keys, or other credentials. Use a local ignored `.env` file for development or a secrets backend for shared and production environments. Rotate any credential that has been exposed.

## Notes

- The scheduled time is **09:00 UTC**; change the DAG cron expression and timezone configuration together if a different schedule is required.
- The Airflow DAG and dbt project are under `walmart_dbt_airflow/`. A dbt project directory also exists at the repository root; use the project copy configured by the Compose volumes when running the containerized workflow.
- This is a learning and demonstration project, not a production-ready reference architecture. Production use should include environment-specific deployment configuration, stronger secret management, alerting, retries, and operational monitoring.
