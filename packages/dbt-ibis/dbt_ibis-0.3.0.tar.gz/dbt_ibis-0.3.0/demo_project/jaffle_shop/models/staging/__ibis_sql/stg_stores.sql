SELECT
  CAST(t0.store_id AS BIGINT) AS store_id,
  t0.store_name,
  t0.country
FROM {{ source('sources_db', 'stores') }} AS t0