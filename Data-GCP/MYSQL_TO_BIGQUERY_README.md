# MySQL to BigQuery Data Pipeline

## Overview
This Python script provides a robust pipeline to extract data from MySQL and load it into Google BigQuery.

## Features
✓ Read data from MySQL tables  
✓ Automatic data validation  
✓ Error handling and logging  
✓ Configurable write modes (TRUNCATE/APPEND)  
✓ Auto-schema detection  
✓ Type conversion  

## Prerequisites

### 1. Install Dependencies
```bash
pip install mysql-connector-python google-cloud-bigquery pandas
```

### 2. Google Cloud Setup
```bash
# Create service account in GCP Console
# Download JSON key file
# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service_account_key.json"
```

### 3. MySQL Access
- MySQL database with product table
- Valid username and password
- Network access (if remote)

## Usage

### Basic Example
```python
from mysql_to_bigquery import MySQLToBigQueryLoader

# Configure connections
mysql_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'database': 'my_database'
}

# Create loader
loader = MySQLToBigQueryLoader(
    mysql_config=mysql_config,
    gcp_project_id='my-gcp-project',
    gcp_credentials_path='service_account_key.json',
    dataset_id='data_warehouse',
    table_id='products'
)

# Run pipeline
loader.run_pipeline()
```

### Custom SQL Query
```python
custom_query = """
    SELECT product_id, product_name, price
    FROM products
    WHERE price > 100
    ORDER BY created_at DESC
"""

loader.run_pipeline(custom_query)
```

### Different Write Modes
```python
# Overwrite entire table
loader.load_to_bigquery(df, write_disposition="WRITE_TRUNCATE")

# Append to existing table
loader.load_to_bigquery(df, write_disposition="WRITE_APPEND")

# Only load if table is empty
loader.load_to_bigquery(df, write_disposition="WRITE_EMPTY")
```

## Configuration Reference

### MySQL Config Dictionary
```python
mysql_config = {
    'host': 'localhost',           # MySQL hostname
    'user': 'root',               # MySQL username
    'password': 'password',        # MySQL password
    'database': 'my_database',     # Database name
    'port': 3306,                 # MySQL port (optional)
    'charset': 'utf8mb4'          # Character set (optional)
}
```

### BigQuery Configuration
```python
loader = MySQLToBigQueryLoader(
    mysql_config=mysql_config,
    gcp_project_id='my-project',           # GCP Project ID
    gcp_credentials_path='key.json',       # Service account key path
    dataset_id='data_warehouse',           # BigQuery dataset
    table_id='products'                    # BigQuery table
)
```

## Methods

### `read_from_mysql(query)`
Read data from MySQL into a Pandas DataFrame
```python
df = loader.read_from_mysql()
# or with custom query
df = loader.read_from_mysql("SELECT * FROM products WHERE price > 50")
```

### `validate_data(df)`
Validate DataFrame before loading
```python
is_valid = loader.validate_data(df)
```

### `load_to_bigquery(df, write_disposition, autodetect_schema)`
Load DataFrame to BigQuery
```python
loader.load_to_bigquery(
    df, 
    write_disposition="WRITE_TRUNCATE",
    autodetect_schema=True
)
```

### `run_pipeline(mysql_query)`
Execute complete pipeline (Read → Validate → Load)
```python
loader.run_pipeline()
```

## Output & Logging
The script provides detailed logs:
```
2024-06-27 10:30:15 - INFO - Initialized loader for data_warehouse.products
2024-06-27 10:30:16 - INFO - Connected to MySQL database
2024-06-27 10:30:17 - INFO - Successfully read 1500 rows from MySQL
2024-06-27 10:30:18 - INFO - Validating data...
2024-06-27 10:30:19 - INFO - Loading 1500 rows to my-project.data_warehouse.products
2024-06-27 10:30:25 - INFO - Successfully loaded data to my-project.data_warehouse.products
```

## Error Handling
The script handles common errors:
- MySQL connection failures
- Invalid data types
- Null values in critical columns
- BigQuery API errors
- Network timeouts

All errors are logged with detailed messages.

## Example: Running as Scheduled Task

### Airflow DAG
```python
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

def load_mysql_to_bq():
    loader = MySQLToBigQueryLoader(...)
    loader.run_pipeline()

dag = DAG('mysql_to_bq', start_date=datetime(2024, 1, 1))
task = PythonOperator(
    task_id='load',
    python_callable=load_mysql_to_bq,
    dag=dag
)
```

### Cron Job
```bash
0 2 * * * cd /path/to/project && python mysql_to_bigquery.py
```

## Troubleshooting

### "MySQL Error: Access denied"
- Check username and password
- Verify database exists
- Check MySQL user privileges

### "Google authentication failed"
- Verify service account key path
- Check GOOGLE_APPLICATION_CREDENTIALS environment variable
- Ensure service account has BigQuery permissions

### "Table not found in BigQuery"
- Create dataset first: `bq mk data_warehouse`
- Or use `autodetect=True` to create table automatically

### "Data type mismatch"
- Review BigQuery schema
- Check MySQL column types
- Use custom query to cast data if needed

## Performance Tips

1. **Batch Loading**: For large tables, consider incremental loading
2. **Index**: Ensure MySQL table has proper indexes
3. **Network**: Run from same region as GCP resources
4. **Schema**: Define explicit schema for better performance

## License
This script is provided as-is for data engineering use.
