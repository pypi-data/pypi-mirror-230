SELECT
  t0.store_id,
  t0.store_name,
  t0.country
FROM {{ ref('stg_stores') }} AS t0
WHERE
  t0.country = 'USA'