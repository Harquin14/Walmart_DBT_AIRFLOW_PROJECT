from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from databricks_job_utils import run_databricks_job
import pendulum

@dag(dag_id="orchestrate",
      schedule= "0 9 * * *",
      start_date= pendulum.datetime(year=2026, month=10, day=15, tz="UTC"),
      catchup=False)

def orchestrate():
    @task
    def ingest_cdc_data():
        run_id = run_databricks_job(job_id="929946241561054")
        return f"Databricks ingestion completed with run ID {run_id}"

    @task
    def clean_up():
        return "rm -rf /opt/airflow/walmart_project/target  && rm -rf /opt/airflow/walmart_project/logs"

    

    freshness_task = BashOperator(
        task_id="source_freshness",
        bash_command=(
            "cd /opt/airflow/walmart_project && "
            "dbt source freshness --profiles-dir /opt/airflow/walmart_project"
        ),
    )

    silver_technical_task = BashOperator(
        task_id="silver_technical",
        cwd = "/opt/airflow/walmart_project",
        bash_command=(
            "dbt run --select silver_t"
            
        ),
    )

    silver_technical_test_task = BashOperator(
        task_id="silver_technical_test",
        cwd = "/opt/airflow/walmart_project",
        bash_command=(
            "dbt test --select silver_t"
                
            ),
        )

    silver_business_task = BashOperator(
        task_id="silver_business",
        cwd = "/opt/airflow/walmart_project",
        bash_command=(
            "dbt run --select silver_b"
                
            ),
        )

    silver_business_test_task = BashOperator(
            task_id="silver_business_test",
            cwd = "/opt/airflow/walmart_project",
            bash_command=(
                "dbt test --select silver_b"
                    
                ),
            )
    gold_ephemeral_task = BashOperator(
        task_id="gold_ephemeral",
        cwd = "/opt/airflow/walmart_project",
        bash_command=(
            "dbt run --select gold/ephemeral"
                
            ),
        )
    gold_dimension_task = BashOperator(
        task_id="gold_dimension",
        cwd = "/opt/airflow/walmart_project",
        bash_command=(
            "dbt snapshot"
                
            ),
        )
    gold_fact_task = BashOperator(
        task_id="gold_fact",
        cwd = "/opt/airflow/walmart_project",
        bash_command=(
            "dbt run --select gold/fact"
                
            ),
        )


    ingest_task = ingest_cdc_data()
    clean_up_task = clean_up()

    ingest_task >> clean_up_task >> freshness_task >> silver_technical_task >> silver_technical_test_task >> silver_business_task >> silver_business_test_task >> gold_ephemeral_task >> gold_dimension_task >> gold_fact_task

orchestrate_dag = orchestrate()