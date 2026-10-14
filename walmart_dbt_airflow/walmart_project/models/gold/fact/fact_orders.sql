SELECT 
order_id,
customer_id,
product_id,
store_id,
employee_id,
order_item_id,
quantity,
unit_price,
line_amount,
total_amount
FROM {{ ref('obt_b') }}

