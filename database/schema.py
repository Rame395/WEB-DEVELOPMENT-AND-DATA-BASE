import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

load_dotenv()

class database:
    def __init__(self, host, user, password, db_name, pool_name="mypool", pool_size=5):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self._in_transaction = False
        self.connection = None
        self.cursor = None

       
        try:
            self.cnxpool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name=pool_name,
                pool_size=pool_size,
                pool_reset_session=True,
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.db_name,
                autocommit=True
            )
        except mysql.connector.Error as e:
            print(f"Connection Pool Error: {e}")
            raise

    def databaseConnection(self):
        """Get connection from the pool if not already connected"""
        if self.connection and self.connection.is_connected():
            return

        try:
            self.connection = self.cnxpool.get_connection()
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as e:
            print(f"Database Connection Error: {e}")
            raise

    def close(self):
        """Release connection back to the pool if not in transaction"""
        if self._in_transaction:
            return
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()  # releases back to pool
            self.connection = None

    def fetchQuery(self, query, values=None):
        try:
            self.databaseConnection()
            self.cursor.execute(query, values)
            return self.cursor.fetchall()
        finally:
            if not self._in_transaction:
                self.close()

    def executeQuery(self, query, values=None):
        try:
            self.databaseConnection()
            self.cursor.execute(query, values)
            self.connection.commit()
            return self.cursor.lastrowid
        finally:
            if not self._in_transaction:
                self.close()

    def executeTransaction(self, query, values=None):
        self.databaseConnection()
        self.cursor.execute(query, values)
        return self.cursor.lastrowid

    def begin(self):
        self.databaseConnection()
        self._in_transaction = True
        self.connection.start_transaction()

    def commit(self):
        if self.connection:
            self.connection.commit()
        self._in_transaction = False
        self.close()

    def rollback(self):
        if self.connection:
            self.connection.rollback()
        self._in_transaction = False
        self.close()



db = database(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", ""),
    db_name=os.getenv("DB_NAME", "hotel")
)
