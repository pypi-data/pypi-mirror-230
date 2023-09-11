from dotenv import load_dotenv
import os

load_dotenv('.env')

mssql_server = os.getenv('MSSQL_SERVER')
mssql_user = os.getenv('MSSQL_USER')
mssql_password = os.getenv('MSSQL_PASSWORD')
mssql_database = os.getenv('MSSQL_DATABASE')

oracle_user = os.getenv('ORACLE_USER')
oracle_password = os.getenv('ORACLE_PASSWORD')
oracle_dsn = os.getenv('ORACLE_DSN')

postgresql_url = os.getenv('POSTGRESQL_URL')

sqlite_path = os.getenv('SQLITE_PATH')

access_path = os.getenv('ACCESS_PATH')

skype_account = os.getenv('SKYPE_ACCOUNT')
skype_password = os.getenv('SKYPE_PASSWORD')
