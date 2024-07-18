import os
import re
import time
import logging
from pathlib import Path

import boto3
from botocore.exceptions import NoCredentialsError


ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
REGION_NAME = os.getenv('AWS_DEFAULT_REGION')
# S3 버킷명 + 중간경로 + 'dbt/' 가 붙은 형태
S3_BUCKET_BASE = os.getenv('S3_BUCKET_BASE')
S3_BUCKET, S3_BASE = re.search(r's3://([^/]+)/(.*)', S3_BUCKET_BASE).groups()
S3_OUTPUT_LOCATION = os.getenv('S3_OUTPUT_LOCATION')
USER_ID = os.getenv('USER_ID')

print("S3_BUCKET_BASE: ", S3_BUCKET_BASE)
print("S3_BUCKET: ", S3_BUCKET)
print("S3_BASE: ", S3_BASE)
print("S3_OUTPUT_LOCATION: ", S3_OUTPUT_LOCATION)
print("USER_ID: ", USER_ID)


logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

# 로컬 파일 경로, S3 버킷 이름, S3에 저장할 파일 이름을 지정합니다.
# uploaded = upload_to_aws('local_file.txt', 'your_bucket_name', 's3_file_name.txt')

# Athena 클라이언트를 초기화합니다.
athena_client = boto3.client('athena', 
                             aws_access_key_id=ACCESS_KEY, 
                             aws_secret_access_key=SECRET_KEY, 
                             region_name=REGION_NAME)


# Athena 쿼리를 실행하는 함수
def _run_athena_query(query, database, output_location):
    response = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': database
        },
        ResultConfiguration={
            'OutputLocation': output_location
        }
    )
    return response


# Athena 쿼리 실행 상태를 확인하는 함수입니다.
def check_query_status(query_execution_id):
    while True:
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        status = response['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            if status == 'FAILED':
                print(response['QueryExecution']['Status']['StateChangeReason'])
            return status
        time.sleep(5)


def run_athena_query(database, query, output_location):
    """Athena 쿼리 실행."""

    # 쿼리를 실행합니다.
    response = _run_athena_query(query, database, output_location)
    query_execution_id = response['QueryExecutionId']

    # 쿼리 실행 상태를 확인합니다.
    status = check_query_status(query_execution_id)
    if status != 'SUCCEEDED':
        print(f"Following query failed with status: {status}\n\n{query}")
        return False
    return True


if __name__ == "__main__":
    logger.info("Update data to S3...")

    #  Create file name to table name mapping
    files = {
        "jaffle_shop_customers.csv": "customers",
        "jaffle_shop_orders.csv": "orders",
        "stripe_payments.csv": "payments"
    }

    # 파일을 S3에 업로드 
    for file, file_dir in files.items():
        local_path = str(Path(__file__).resolve().parent.parent / "data/{}".format(file))
        s3_path = "{}/{}/raw/{}/{}".format(S3_BASE, USER_ID, file_dir, file)
        print(local_path, s3_path)
        upload_to_aws(local_path, S3_BUCKET, s3_path)

    # Athena 테이블 생성 쿼리 실행
    logger.info("Creating tables...")

    with open(Path(__file__).resolve().parent / "sql/create_tables.sql", "r") as f:
        query_text = f.read()

    query_text = query_text.format(user=USER_ID, bucket_base=S3_BUCKET_BASE)
    queries = query_text.split(";")
    for query in queries:
        if len(query) == 0:
            continue
        print(query)
        if not run_athena_query('default', query, S3_OUTPUT_LOCATION):
            break

    logger.info("Tables created")
