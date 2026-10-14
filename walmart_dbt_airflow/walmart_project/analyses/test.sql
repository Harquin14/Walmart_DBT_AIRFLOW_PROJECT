SELECT * FROM  {{ ref('orders_t') }} 
WHERE is_active = 'N'