"""
MySQL to BigQuery Data Pipeline

This script reads product data from MySQL and loads it into Google BigQuery.
It handles data transformation, validation, and error handling.

Prerequisites:
- pip install mysql-connector-python google-cloud-bigquery pandas
- MySQL database connection credentials
- GCP service account JSON key
"""

import mysql.connector
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
import logging
from typing import Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MySQLToBigQueryLoader:
    """
    A class to handle loading data from MySQL to Google BigQuery.
    """

    def __init__(
        self,
        mysql_config: dict,
        gcp_project_id: str,
        gcp_credentials_path: Optional[str] = None,
        dataset_id: str = "data_warehouse",
        table_id: str = "products"
    ):
        """
        Initialize the loader with MySQL and GCP configurations.

        Args:
            mysql_config: Dictionary with MySQL connection details
                {
                    'host': 'localhost',
                    'user': 'root',
                    'password': 'password',
                    'database': 'your_db'
                }
            gcp_project_id: GCP project ID
            gcp_credentials_path: Path to service account JSON key
            dataset_id: BigQuery dataset name
            table_id: BigQuery table name
        """
        self.mysql_config = mysql_config
        self.gcp_project_id = gcp_project_id
        self.dataset_id = dataset_id
        self.table_id = table_id

        # Initialize BigQuery client
        if gcp_credentials_path:
            credentials = service_account.Credentials.from_service_account_file(
                gcp_credentials_path
            )
            self.bq_client = bigquery.Client(
                project=gcp_project_id,
                credentials=credentials
            )
        else:
            self.bq_client = bigquery.Client(project=gcp_project_id)

        logger.info(f"Initialized loader for {dataset_id}.{table_id}")

    def read_from_mysql(self, query: str = None) -> pd.DataFrame:
        """
        Read data from MySQL table.

        Args:
            query: SQL query to execute. If None, reads entire products table.

        Returns:
            DataFrame containing the MySQL data
        """
        try:
            # Default query to read products table
            if query is None:
                query = """
                    SELECT 
                        product_id,
                        product_name,
                        category,
                        price,
                        stock_quantity,
                        created_at,
                        updated_at
                    FROM products
                """

            connection = mysql.connector.connect(**self.mysql_config)
            logger.info("Connected to MySQL database")

            # Read data into DataFrame
            df = pd.read_sql(query, connection)
            connection.close()

            logger.info(f"Successfully read {len(df)} rows from MySQL")
            return df

        except mysql.connector.Error as err:
            logger.error(f"MySQL Error: {err}")
            raise
        except Exception as err:
            logger.error(f"Error reading from MySQL: {err}")
            raise

    def validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate data before loading to BigQuery.

        Args:
            df: DataFrame to validate

        Returns:
            True if valid, False otherwise
        """
        logger.info("Validating data...")

        # Check for null values in critical columns
        critical_columns = ['product_id', 'product_name', 'price']
        for col in critical_columns:
            if col in df.columns and df[col].isnull().any():
                logger.warning(f"Found null values in {col}")

        # Check data types
        if 'price' in df.columns:
            try:
                df['price'] = pd.to_numeric(df['price'])
                logger.info("Price column validated as numeric")
            except ValueError:
                logger.error("Price column contains non-numeric values")
                return False

        # Check for duplicates
        if 'product_id' in df.columns:
            duplicates = df['product_id'].duplicated().sum()
            if duplicates > 0:
                logger.warning(f"Found {duplicates} duplicate product_ids")

        logger.info("Data validation complete")
        return True

    def load_to_bigquery(
        self,
        df: pd.DataFrame,
        write_disposition: str = "WRITE_TRUNCATE",
        autodetect_schema: bool = True
    ) -> bool:
        """
        Load DataFrame to BigQuery table.

        Args:
            df: DataFrame to load
            write_disposition: How to handle existing data
                - WRITE_TRUNCATE: Overwrite
                - WRITE_APPEND: Append
                - WRITE_EMPTY: Only if table empty
            autodetect_schema: Auto-detect schema from data

        Returns:
            True if successful, False otherwise
        """
        try:
            table_id_full = f"{self.gcp_project_id}.{self.dataset_id}.{self.table_id}"

            # Configure job
            job_config = bigquery.LoadJobConfig(
                write_disposition=write_disposition,
                autodetect=autodetect_schema,
                source_format=bigquery.SourceFormat.PARQUET,
            )

            logger.info(f"Loading {len(df)} rows to {table_id_full}")

            # Load data
            job = self.bq_client.load_table_from_dataframe(
                df,
                table_id_full,
                job_config=job_config
            )

            # Wait for job to complete
            job.result()
            logger.info(f"Successfully loaded data to {table_id_full}")

            # Get table info
            table = self.bq_client.get_table(table_id_full)
            logger.info(f"Table {table_id_full} now has {table.num_rows} rows")

            return True

        except Exception as err:
            logger.error(f"Error loading to BigQuery: {err}")
            raise

    def run_pipeline(self, mysql_query: str = None) -> bool:
        """
        Execute the complete pipeline: Read → Validate → Load.

        Args:
            mysql_query: Custom SQL query (optional)

        Returns:
            True if successful
        """
        try:
            logger.info("Starting MySQL to BigQuery pipeline...")

            # Step 1: Read from MySQL
            df = self.read_from_mysql(mysql_query)

            # Step 2: Validate data
            if not self.validate_data(df):
                logger.error("Data validation failed")
                return False

            # Step 3: Load to BigQuery
            if not self.load_to_bigquery(df):
                logger.error("Data loading failed")
                return False

            logger.info("Pipeline completed successfully!")
            return True

        except Exception as err:
            logger.error(f"Pipeline error: {err}")
            return False


def main():
    """
    Example usage of MySQLToBigQueryLoader.
    """

    # MySQL Configuration
    mysql_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'your_password',
        'database': 'your_database'
    }

    # GCP Configuration
    gcp_project_id = 'your-gcp-project-id'
    gcp_credentials_path = 'path/to/service_account_key.json'

    # Initialize loader
    loader = MySQLToBigQueryLoader(
        mysql_config=mysql_config,
        gcp_project_id=gcp_project_id,
        gcp_credentials_path=gcp_credentials_path,
        dataset_id='data_warehouse',
        table_id='products'
    )

    # Custom query (optional)
    custom_query = """
        SELECT 
            product_id,
            product_name,
            category,
            price,
            stock_quantity,
            created_at,
            updated_at
        FROM products
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    """

    # Run pipeline
    try:
        success = loader.run_pipeline(custom_query)
        if success:
            print("✓ Data successfully loaded to BigQuery")
        else:
            print("✗ Pipeline failed")
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    main()
