# Walmart_DBT_AIRFLOW_PROJECT

## Local setup

1. Copy `walmart_dbt_airflow/.env.example` to `walmart_dbt_airflow/.env`.
2. Set `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, and `FERNET_KEY` in `.env`.
   Generate a Fernet key with:

   ```powershell
   docker run --rm apache/airflow:3.3.2 airflow config get-value core fernet_key
   ```

3. Set the Databricks SQL warehouse HTTP path in
   `walmart_dbt_airflow/profiles.yml`.
4. From the `walmart_dbt_airflow` directory, start the services:

   ```powershell
   docker compose up --build
   ```

The profile reads the Databricks host and token from environment variables.
Keep `.env` private; it is excluded from Git.