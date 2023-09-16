WITH t0 AS (
  SELECT
    t2.id AS payment_id,
    t2.order_id AS order_id,
    t2.payment_method AS payment_method,
    t2.amount AS amount
  FROM {{ ref('raw_payments') }} AS t2
)
SELECT
  t1.payment_id,
  t1.order_id,
  t1.payment_method,
  t1.amount
FROM (
  SELECT
    t0.payment_id AS payment_id,
    t0.order_id AS order_id,
    t0.payment_method AS payment_method,
    t0.amount / CAST(CAST(100 AS TINYINT) AS DECIMAL(18, 3)) AS amount
  FROM t0
) AS t1