-- 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS dbt_{user}_jaffle_shop;
CREATE DATABASE IF NOT EXISTS dbt_{user}_stripe;

-- 테이블 생성
CREATE EXTERNAL TABLE IF NOT EXISTS dbt_{user}_jaffle_shop.customers (
    id int,
    first_name string,
    last_name string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    'separatorChar' = ',',
    'quoteChar' = '"',
    'skip.header.line.count' = '1'
) 
LOCATION '{bucket_base}/{user}/customers/'
TBLPROPERTIES ('has_encrypted_data'='false');

CREATE EXTERNAL TABLE IF NOT EXISTS dbt_{user}_jaffle_shop.orders (
    id int,
    user_id int,
    order_date string,
    status string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    'separatorChar' = ',',
    'quoteChar' = '"',
    'skip.header.line.count' = '1' 
) 
LOCATION '{bucket_base}/{user}/orders/'
TBLPROPERTIES ('has_encrypted_data'='false');

CREATE EXTERNAL TABLE IF NOT EXISTS dbt_{user}_stripe.payment (
    id int,
    orderid int,
    paymentmethod string,
    status string,
    amount int,
    created string
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES (
    'separatorChar' = ',',
    'quoteChar' = '"',
    'skip.header.line.count' = '1' 
) 
LOCATION '{bucket_base}/{user}/payments/'
TBLPROPERTIES ('has_encrypted_data'='false');