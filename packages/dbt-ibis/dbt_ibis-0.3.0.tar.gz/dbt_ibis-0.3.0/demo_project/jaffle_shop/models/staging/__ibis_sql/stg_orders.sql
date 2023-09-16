SELECT
  t0.order_id,
  t0.customer_id,
  t0.order_date,
  t0.status
FROM (
  SELECT
    t1.id AS order_id,
    t1.user_id AS customer_id,
    t1.order_date AS order_date,
    t1.status AS status,
    t1.dbt_scd_id AS dbt_scd_id,
    t1.dbt_updated_at AS dbt_updated_at,
    t1.dbt_valid_from AS dbt_valid_from,
    t1.dbt_valid_to AS dbt_valid_to
  FROM {{ ref('orders_snapshot') }} AS t1
) AS t0