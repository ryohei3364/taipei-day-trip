from .dbconf import sql_pool

class Model:
  def __init__(self, query=None, params=(), fetch_one=False):
    self.data = None
    if query:
      self.data = self.find(query, params, fetch_one)
      
  def find(self, query, params, fetch_one):
    cnx = None
    try:
      cnx = sql_pool.get_connection()
      with cnx.cursor(dictionary=True) as cursor:
        cursor.execute(query, params)
        return cursor.fetchone() if fetch_one else cursor.fetchall()
    except Exception as e:
      raise RuntimeError("Database query failed") from e
    finally:
      if cnx:
        cnx.close()
  
  def to_dict(self):
    return self.data

  def __repr__(self):
    return str(self.data)
  
class Attraction(Model):
  base_query = """
    SELECT id, name, category, description, address, transport, mrt, lat, lng, images
    FROM attraction
  """
  select_query = " WHERE id = %s"
  
  def __init__(self, attraction_id=None):
    if attraction_id:
      full_query = self.base_query + self.select_query
      super().__init__(query=full_query, params=(attraction_id,), fetch_one=True)
    else:
      self.data = None
  
  def search_attractions(self, page: int=0, keyword: str=None, page_size: int = 12):
    offset = page * page_size
    base_query = self.base_query
    select_query = " WHERE name LIKE %s OR mrt = %s"
    page_query = " LIMIT %s OFFSET %s"
    
    if keyword:
      full_query = base_query + select_query + page_query
      keyword_param = f"%{keyword}%"
      params = (keyword_param, keyword, page_size, offset)
    else:
      full_query = base_query + page_query
      params = (page_size, offset)
    
    result = self.find(full_query, params, fetch_one=False)
    
    next_page = page + 1 if len(result) == page_size else None
    return {
      "nextPage": next_page,
      "data": result
    }
