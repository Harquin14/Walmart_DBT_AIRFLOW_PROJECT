SELECT
DISTINCT
employee_id,
employee_first_name,
employee_last_name,
employee_email,
job_title,
order_id,
salary,
employee_created_timestamp,
employee_updated_timestamp,
employee_is_active,
current_timestamp() AS employee_gold_processed_at
FROM {{ ref('obt_b') }}