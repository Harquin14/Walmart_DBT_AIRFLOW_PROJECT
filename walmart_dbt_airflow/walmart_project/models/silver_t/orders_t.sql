
{{ config(
    materialized='incremental',
    unique_key='order_id'
) }}

SELECT *, current_timestamp() as updated_at FROM {{ source('walmart_databricks', 'orders') }}


{% if is_incremental() %}
  WHERE updated_timestamp > COALESCE((SELECT MAX(updated_timestamp) FROM {{ this }}), '1900-01-01')

{% endif %}