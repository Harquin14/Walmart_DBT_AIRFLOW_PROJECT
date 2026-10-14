{{ config(
    materialized='incremental',
    unique_key='customer_id'
) }}

SELECT *, current_timestamp() AS updated_at FROM {{ source('walmart_databricks', 'customers') }}



{% if is_incremental() %}
  WHERE updated_timestamp > COALESCE((SELECT MAX(updated_timestamp) FROM {{ this }}), '1900-01-01')
{% endif %}
