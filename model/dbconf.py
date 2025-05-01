from mysql.connector import pooling, Error
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
  "user": os.getenv("MYSQL_USER"),
  "password": os.getenv("MYSQL_PW"),
  "host": "localhost",
  "database": os.getenv("MYSQL_DB"),
  "charset": "utf8"
}

class SQLPool:
  
  def __init__(self):
    try:
      self.pool = pooling.MySQLConnectionPool(
        pool_name = "mypool",
        pool_size = 10,
        **DB_CONFIG,
        pool_reset_session=True,
        connection_timeout=30
      )
      test_con = self.pool.get_connection()
      test_con.ping(reconnect=True, attempts=3)
      test_con.close()
      print("連線池建立成功，檢查 Processlist 中...")
      self.check_processlist()
      
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
    
  def check_processlist(self):
    con = self.get_connection()
    try:
      cursor = con.cursor(dictionary=True)
      cursor.execute("SHOW FULL PROCESSLIST")
      processlist = cursor.fetchall()
      total = len(processlist)
      sleeping = sum(1 for p in processlist if p["Command"] == "Sleep")
      running = sum(1 for p in processlist if p["Command"] == "Query")
      long_running = [p for p in processlist if p["Command"] == "Query" and p["Time"] > 5]

      print(f"總連線數：{total}")
      print(f"Sleep 狀態連線數：{sleeping}")
      print(f"執行中查詢數：{running}")
      print(f"長時間執行中的查詢（> 5 秒）:{long_running}")
      
      for process in processlist:
        if process["Command"] == "Sleep" and process["Time"] > 10:
          cursor.execute(f"KILL {process['Id']}")
          print(f"Killed connection {process['Id']} - Sleep for {process['Time']} seconds.")
      
    finally:
        cursor.close()
        con.close()
    
sql_pool = SQLPool()
