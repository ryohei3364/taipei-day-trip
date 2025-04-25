from .dbconf import sql_pool

class Model:
  def __init__(self):
    self.data = []
  
  @classmethod   
  def find(cls, query, params=(), fetch_one=True):
    cnx = None
    try:
      cnx = sql_pool.get_connection()
      with cnx.cursor(dictionary=True) as cursor:
        cursor.execute(query, params)
        return cursor.fetchone() if fetch_one else cursor.fetchall()
    except Exception as e:
      print(f"[DB ERROR] 查詢失敗: {e}")
      return None  
    finally:
      if cnx and cnx.is_connected():
        cnx.close()

  @classmethod   
  def insert(cls, params, values):
    table_name = cls.__name__.lower() 
    columns = ", ".join(f"`{param}`" for param in params)
    placeholders = ", ".join(["%s"] * len(params))
    query = f"INSERT INTO `{table_name}`({columns}) VALUES({placeholders})"
    cnx = None
    try:
      cnx = sql_pool.get_connection()
      with cnx.cursor() as cursor:
        cursor.execute(query, values)
      cnx.commit()
    except Exception as e:
      print(f"[DB ERROR] 查詢失敗: {e}")
      return None 
    finally:
      if cnx and cnx.is_connected():
        cnx.close() 

  @classmethod
  def delete_by_column(cls, column: str, value):
    table_name = cls.__name__.lower() 
    query = f"DELETE FROM `{table_name}` WHERE `{column}`=%s"
    cnx = None
    try:
      cnx = sql_pool.get_connection()
      with cnx.cursor() as cursor:
        cursor.execute(query, (value,))
        cnx.commit()
        return cursor.rowcount
    except Exception as e:
      print(f"[Model ERROR] 刪除資料失敗: {e}")
      return 0
    finally:
      if cnx and cnx.is_connected():
        cnx.close()
                 
  @classmethod
  def search_all(cls):
    table_name = cls.__name__.lower() 
    query = f"SELECT * FROM `{table_name}`"
    return cls.find(query, (), fetch_one=False)

  @classmethod
  def search_by_column(cls, column: str, value):
    table_name = cls.__name__.lower() 
    query = f"SELECT * FROM `{table_name}` WHERE `{column}`=%s"
    return cls.find(query=query, params=(value,)) 

  @classmethod
  def search_by_columns(cls, filters: dict):
    table_name = cls.__name__.lower() 
    where_clauses = []
    params = []

    for column, value in filters.items():
      where_clauses.append(f"`{column}` = %s")
      params.append(value)

    where_statement = " AND ".join(where_clauses)
    query = f"SELECT * FROM `{table_name}` WHERE {where_statement}"

    return cls.find(query=query, params=tuple(params))

  @classmethod
  def update_by_column(cls, target_column: str, target_value, update_fields: dict):
    table_name = cls.__name__.lower() 
    set_clause = ", ".join(f"`{key}` = %s" for key in update_fields.keys())
    query = f"UPDATE `{table_name}` SET {set_clause} WHERE `{target_column}` = %s"
    params = tuple(update_fields.values()) + (target_value,)

    cnx = None
    try:
      cnx = sql_pool.get_connection()
      with cnx.cursor() as cursor:
        cursor.execute(query, params)
        cnx.commit()
        return cursor.rowcount
    except Exception as e:
        print(f"[DB ERROR] 更新失敗: {e}")
        return 0
    finally:
      if cnx and cnx.is_connected():
        cnx.close()  
   
  def to_dict(self):
    return self.data

  def __str__(self):
    return str(self.data)
  
class Attraction(Model):
  @classmethod
  def search_by_keyword(cls, page=0, keyword=None, page_size=12):
    table_name = cls.__name__.lower() 
    offset = page * page_size
    if keyword:
        query = f"SELECT * FROM `{table_name}` WHERE name LIKE %s OR mrt = %s LIMIT %s OFFSET %s"
        params = (f"%{keyword}%", keyword, page_size, offset)
    else:
        query = f"SELECT * FROM `{table_name}` LIMIT %s OFFSET %s"
        params = (page_size, offset)
        
    result = cls.find(query, params, fetch_one=False)
    next_page = page + 1 if len(result) == page_size else None
    return {
      "nextPage": next_page,
      "data": result
    }

class Mrt(Model):
  @classmethod
  def search_all(cls):
    query = "SELECT mrt, COUNT(mrt) AS count FROM attraction GROUP BY mrt ORDER BY count DESC"
    return cls.find(query, (), fetch_one=False)
  
class Member(Model):
  pass 

class Booking(Model):
  @classmethod
  def get_booking_by_userId(cls, userId: int):
    query = """
      SELECT * FROM attraction 
      INNER JOIN booking ON attraction.id=booking.attractionId 
      WHERE booking.userId=%s;
    """
    result = cls.find(query=query, params=(userId,), fetch_one=True)
    return result
  
class Orders(Model):
  @classmethod
  def get_data_by_orderNumber(cls, orderNumber: int):
    query = """
      SELECT * FROM attraction 
      INNER JOIN orders ON attraction.id=orders.attractionId 
      WHERE orders.orderNumber=%s;
    """
    result = cls.find(query=query, params=(orderNumber,), fetch_one=True)
    return result
  
  @classmethod
  def search_by_column(cls, column: str, value):
    table_name = cls.__name__.lower() 
    query = f"SELECT * FROM `{table_name}` WHERE `{column}`=%s ORDER BY orderTime DESC"
    return cls.find(query=query, params=(value,), fetch_one=False) 
  
