# dbt-tutorial

dbt 튜토리얼을 위한 코드 

로컬에서 PostgreSQL, 원격에서 AWS Athena 를 이용

> 아래 저장소의 오리지널 코드에 일부 수정 및 추가를 하였습니다. 
> https://github.com/luchonaveiro/dbt-postgres-tutorial


## DB 

### 로컬의 PostgreSQL 이용

튜토리얼 진행 전 다음과 같은 Docker Compose 명령으로 PostgreSQL DB 를 준비합니다.

```sh
docker-compose -f docker compose-postgresql.yaml up -d
```

### 원격의 AWS Athena 이용

Athena 를 위해서는 현재 쉘에 다음과 같은 환경 변수가 지정되어 있어야 합니다.

- `AWS_ACCESS_KEY_ID` - S3 및 Athena 에 대한 권한이 있는 IAM 유저 접근 키
- `AWS_SECRET_ACCESS_KEY` - S3 및 Athena 에 대한 권한이 있는 IAM 유저 비밀 키
- `AWS_DEFAULT_REGION` - 이용할 AWS 리전 (예: `ap-northeast-2`)
- `S3_BUCKET_BASE` - 샘플 데이터를 올릴 S3 버킷 기본 경로 (예: `s3://my-bucket/dbt-tutorial`)
- `S3_OUTPUT_LOCATION` - Athena 출력 결과가 저장될 S3 버킷 경로 (예: `s3://aws-athena-query-results-AWS_ACCOUNT_NO-ap-northeast-2`)
- `USER_ID` - 샘플 데이터 및 Athena DB 명 중복을 피하기 위한 유저 식별자 (예: `user123` )

샘플 데이터는 `s3://{S3_BUCKET_BASE}/{USER_ID}` 경로 아래에 올라가며, Athena DB 는 `dbt_{USER_ID}_jaffle_shop` 형식으로 만들어집니다.

튜토리얼 진행 전 다음과 같은 Docker Compose 명령으로 AThena DB 를 준비합니다.

```sh
docker-compose -f docker compose-athena.yaml up -d
```

docker-compose -f docker compose-athena.yaml up -d -e ACCESS_KEY=접근키 SECRET_KEY=비밀키 S3_BUCKET_BASE=S3버킷_기본경로 USER_ID=유저_식별자

## GitLab
