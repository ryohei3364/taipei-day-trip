from mysql.connector import pooling, Error
from dotenv import load_dotenv
import os

load_dotenv()
MYSQL_PW=os.getenv("MYSQL_PW")

class SQLPool:
  
  def __init__(self):
    try:
      self.pool = pooling.MySQLConnectionPool(
        pool_name = "mypool",
        pool_size = 10,
        user = "demo",
        password = MYSQL_PW,
        host = "localhost",
        database = "website",
        charset='utf8',
        pool_reset_session=True,
        connection_timeout=30
      )
      test_con = self.pool.get_connection()
      test_con.ping(reconnect=True, attempts=3)
      test_con.close()
    except Exception as e:
      print(f"資料庫連線池建立失敗: {e}")
      self.pool = None 
      raise
      
  def get_connection(self):
    if not self.pool:
      raise RuntimeError("資料庫連線池未建立")
    try:
      con =  self.pool.get_connection()
      if not con.is_connected():
        con.reconnect(attempts=3, delay=1)
      con.autocommit = True
      return con
    except Error as err:
      print(f"[ERROR] 取得連線失敗: {err}")
      raise RuntimeError("資料庫暫時無法使用") from err
    
sql_pool = SQLPool()
