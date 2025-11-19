import pandas as pd
import sqlite3
import streamlit as st
from config import CSV_ENCODINGS, SUPPORTED_SQL_DB_TYPES

class DataHandler:
    """Handles data loading from CSV files and database connections (SQL & NoSQL)"""
    
    @staticmethod
    def load_csv(uploaded_file):
        """Load CSV file with multiple fallback strategies"""
        df = None
        error_messages = []
        
        # Strategy 1: Standard read
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e1:
            error_messages.append(f"Standard: {str(e1)[:50]}")
            
            # Strategy 2: With error handling
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, on_bad_lines='skip', encoding='utf-8')
            except Exception as e2:
                error_messages.append(f"UTF-8: {str(e2)[:50]}")
                
                # Strategy 3: Different encoding
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, on_bad_lines='skip', encoding='latin-1')
                except Exception as e3:
                    error_messages.append(f"Latin-1: {str(e3)[:50]}")
                    
                    # Strategy 4: Python engine
                    try:
                        uploaded_file.seek(0)
                        df = pd.read_csv(uploaded_file, engine='python', on_bad_lines='skip', 
                                       encoding='utf-8', sep=None)
                    except Exception as e4:
                        error_messages.append(f"Python engine: {str(e4)[:50]}")
        
        return df, error_messages
    
    @staticmethod
    def load_from_database(db_type, connection_params):
        """Load data from database connection (SQL or NoSQL)"""
        try:
            # SQL Databases
            if db_type == "PostgreSQL":
                import psycopg2
                conn = psycopg2.connect(**connection_params)
            elif db_type == "MySQL":
                import mysql.connector
                conn = mysql.connector.connect(**connection_params)
            elif db_type == "SQLite":
                conn = sqlite3.connect(connection_params.get('database', ':memory:'))
            elif db_type == "SQL Server":
                import pyodbc
                conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={connection_params['host']};DATABASE={connection_params['database']};UID={connection_params['user']};PWD={connection_params['password']}"
                conn = pyodbc.connect(conn_str)
            
            # NoSQL Databases
            elif db_type == "MongoDB":
                from pymongo import MongoClient
                conn_str = f"mongodb://{connection_params.get('user', '')}:{connection_params.get('password', '')}@{connection_params['host']}:{connection_params.get('port', 27017)}"
                if not connection_params.get('user'):
                    conn_str = f"mongodb://{connection_params['host']}:{connection_params.get('port', 27017)}"
                client = MongoClient(conn_str)
                db = client[connection_params['database']]
                return {'client': client, 'db': db, 'type': 'mongodb'}, None, None
            
            elif db_type == "Redis":
                import redis
                conn = redis.Redis(
                    host=connection_params['host'],
                    port=connection_params.get('port', 6379),
                    password=connection_params.get('password', None),
                    db=connection_params.get('database', 0),
                    decode_responses=True
                )
                return {'client': conn, 'type': 'redis'}, None, None
            
            elif db_type == "Cassandra":
                from cassandra.cluster import Cluster
                from cassandra.auth import PlainTextAuthProvider
                
                if connection_params.get('user') and connection_params.get('password'):
                    auth_provider = PlainTextAuthProvider(
                        username=connection_params['user'],
                        password=connection_params['password']
                    )
                    cluster = Cluster([connection_params['host']], 
                                    port=connection_params.get('port', 9042),
                                    auth_provider=auth_provider)
                else:
                    cluster = Cluster([connection_params['host']], 
                                    port=connection_params.get('port', 9042))
                
                session = cluster.connect()
                if connection_params.get('keyspace'):
                    session.set_keyspace(connection_params['keyspace'])
                
                return {'cluster': cluster, 'session': session, 'type': 'cassandra'}, None, None
            
            else:
                return None, None, f"Unsupported database type: {db_type}"
            
            return conn, None, None
        except ImportError as e:
            driver_name = str(e).split()[-1].replace("'", "")
            install_map = {
                'psycopg2': 'psycopg2-binary',
                'mysql': 'mysql-connector-python',
                'pyodbc': 'pyodbc',
                'pymongo': 'pymongo',
                'redis': 'redis',
                'cassandra': 'cassandra-driver'
            }
            pkg = install_map.get(driver_name, driver_name)
            return None, None, f"Missing database driver. Install: pip install {pkg}"
        except Exception as e:
            return None, None, f"Connection error: {str(e)}"
    
    @staticmethod
    def get_tables(conn, db_type):
        """Get list of tables/collections from database"""
        try:
            # SQL Databases
            if db_type == "PostgreSQL":
                query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                tables = pd.read_sql_query(query, conn)
                return tables.iloc[:, 0].tolist()
            elif db_type == "MySQL":
                query = "SHOW TABLES"
                tables = pd.read_sql_query(query, conn)
                return tables.iloc[:, 0].tolist()
            elif db_type == "SQLite":
                query = "SELECT name FROM sqlite_master WHERE type='table'"
                tables = pd.read_sql_query(query, conn)
                return tables.iloc[:, 0].tolist()
            elif db_type == "SQL Server":
                query = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'"
                tables = pd.read_sql_query(query, conn)
                return tables.iloc[:, 0].tolist()
            
            # NoSQL Databases
            elif db_type == "MongoDB":
                return conn['db'].list_collection_names()
            
            elif db_type == "Redis":
                # Redis uses keys, we'll scan for patterns
                keys = []
                cursor = 0
                while True:
                    cursor, partial_keys = conn['client'].scan(cursor, count=100)
                    keys.extend(partial_keys)
                    if cursor == 0:
                        break
                
                # Extract unique key prefixes (patterns)
                prefixes = set()
                for key in keys[:1000]:  # Limit to first 1000 keys
                    if ':' in key:
                        prefixes.add(key.split(':')[0])
                    else:
                        prefixes.add('all_keys')
                
                return sorted(list(prefixes)) if prefixes else ['all_keys']
            
            elif db_type == "Cassandra":
                keyspace = conn['session'].keyspace
                if not keyspace:
                    # Get list of keyspaces
                    rows = conn['session'].execute("SELECT keyspace_name FROM system_schema.keyspaces")
                    return [row.keyspace_name for row in rows if not row.keyspace_name.startswith('system')]
                else:
                    # Get tables in current keyspace
                    query = f"SELECT table_name FROM system_schema.tables WHERE keyspace_name = '{keyspace}'"
                    rows = conn['session'].execute(query)
                    return [row.table_name for row in rows]
            
            else:
                return []
        except Exception as e:
            st.error(f"Error fetching tables: {str(e)}")
            return []
    
    @staticmethod
    def load_table(conn, table_name, db_type, limit=10000):
        """Load entire table/collection from database"""
        try:
            # SQL Databases
            if db_type in SUPPORTED_SQL_DB_TYPES:
                query = f"SELECT * FROM {table_name} LIMIT {limit}"
                df = pd.read_sql_query(query, conn)
                return df, None
            
            # NoSQL Databases
            elif db_type == "MongoDB":
                collection = conn['db'][table_name]
                cursor = collection.find().limit(limit)
                data = list(cursor)
                
                if not data:
                    return None, "Collection is empty"
                
                df = pd.DataFrame(data)
                # Convert ObjectId to string for display
                if '_id' in df.columns:
                    df['_id'] = df['_id'].astype(str)
                
                return df, None
            
            elif db_type == "Redis":
                redis_client = conn['client']
                
                # Get keys with the prefix (pattern)
                if table_name == 'all_keys':
                    pattern = '*'
                else:
                    pattern = f"{table_name}:*"
                
                keys = []
                cursor = 0
                while len(keys) < limit:
                    cursor, partial_keys = redis_client.scan(cursor, match=pattern, count=100)
                    keys.extend(partial_keys)
                    if cursor == 0:
                        break
                
                keys = keys[:limit]
                
                if not keys:
                    return None, f"No keys found matching pattern: {pattern}"
                
                # Get values for keys
                data = []
                for key in keys:
                    try:
                        key_type = redis_client.type(key)
                        
                        if key_type == 'string':
                            value = redis_client.get(key)
                        elif key_type == 'hash':
                            value = redis_client.hgetall(key)
                        elif key_type == 'list':
                            value = redis_client.lrange(key, 0, -1)
                        elif key_type == 'set':
                            value = list(redis_client.smembers(key))
                        elif key_type == 'zset':
                            value = redis_client.zrange(key, 0, -1, withscores=True)
                        else:
                            value = None
                        
                        data.append({
                            'key': key,
                            'type': key_type,
                            'value': str(value)
                        })
                    except Exception as e:
                        data.append({
                            'key': key,
                            'type': 'error',
                            'value': str(e)
                        })
                
                df = pd.DataFrame(data)
                return df, None
            
            elif db_type == "Cassandra":
                query = f"SELECT * FROM {table_name} LIMIT {limit}"
                rows = conn['session'].execute(query)
                
                data = []
                for row in rows:
                    data.append(row._asdict())
                
                if not data:
                    return None, "Table is empty"
                
                df = pd.DataFrame(data)
                return df, None
            
            else:
                return None, f"Unsupported database type: {db_type}"
        
        except Exception as e:
            return None, f"Error loading table: {str(e)}"
    
    @staticmethod
    def execute_query(conn, query):
        """Execute SQL query on database connection"""
        try:
            df = pd.read_sql_query(query, conn)
            return df, None
        except Exception as e:
            return None, f"Query error: {str(e)}"
    
    @staticmethod
    def generate_schema(df, source_type="csv", table_name=None):
        """Generate schema description from DataFrame"""
        rows, cols = df.shape
        schema_lines = [f"Data Source: {source_type.upper()}"]
        if table_name:
            schema_lines.append(f"Table: {table_name}")
        schema_lines.append(f"{rows:,} rows × {cols} columns")
        schema_lines.append("\nColumns:")
        
        for col in df.columns[:15]:
            dtype = df[col].dtype
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df) * 100) if len(df) > 0 else 0
            schema_lines.append(f"  - {col} ({dtype}) - {null_pct:.1f}% null")
        
        if cols > 15:
            schema_lines.append(f"  ... and {cols - 15} more columns")
        
        return "\n".join(schema_lines)
    
    @staticmethod
    def test_connection(db_type, connection_params):
        """Test database connection"""
        conn, _, error = DataHandler.load_from_database(db_type, connection_params)
        if error:
            return False, error
        
        try:
            # SQL Databases
            if db_type in SUPPORTED_SQL_DB_TYPES:
                if db_type == "SQLite":
                    pd.read_sql_query("SELECT 1", conn)
                else:
                    pd.read_sql_query("SELECT 1 as test", conn)
                conn.close()
            
            # NoSQL Databases
            elif db_type == "MongoDB":
                # Try to list databases
                conn['client'].list_database_names()
                conn['client'].close()
            
            elif db_type == "Redis":
                # Try to ping
                conn['client'].ping()
                conn['client'].close()
            
            elif db_type == "Cassandra":
                # Try a simple query
                conn['session'].execute("SELECT release_version FROM system.local")
                conn['cluster'].shutdown()
            
            return True, "Connection successful!"
        except Exception as e:
            # Clean up connections
            try:
                if db_type in SUPPORTED_SQL_DB_TYPES and conn:
                    conn.close()
                elif db_type == "MongoDB" and conn:
                    conn['client'].close()
                elif db_type == "Redis" and conn:
                    conn['client'].close()
                elif db_type == "Cassandra" and conn:
                    conn['cluster'].shutdown()
            except:
                pass
            
            return False, f"Connection test failed: {str(e)}"