# arrange json data into MySQL database

from dotenv import load_dotenv
import mysql.connector, os, json, re

load_dotenv()
MYSQL_USER=os.getenv("MYSQL_USER")
MYSQL_PW=os.getenv("MYSQL_PW")
MYSQL_DB=os.getenv("MYSQL_DB")

con = mysql.connector.pooling.MySQLConnectionPool(
  pool_name = "mypool",
  pool_size = 10,
  user = MYSQL_USER,
  password = MYSQL_PW,
  host = "localhost",
  database = MYSQL_DB,
  charset='utf8'
)

cnx=con.get_connection()
cursor = cnx.cursor()

with open('data/taipei-attractions.json', 'r', encoding='utf-8') as json_file:
    data = json.load(json_file)

spots = data['result']['results']
query = """
  INSERT INTO attraction (id, name, category, description, address, transport, mrt, lat, lng, images)
  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

for spot in spots:
  id = spot['_id']
  name = spot['name']
  category = spot['CAT']
  description = spot['description']
  address = spot['address']
  transport = spot['direction']
  mrt = spot['MRT']
  lat = spot['latitude']
  lng = spot['longitude']
  file = spot['file'].split("https://")
  images = []
  for img in file:
    if img:
      match = re.search(r"(^https?:(.{10,})*.(jpg|png))", "https://" + img, re.I)
      if match:
        images.append(match.group(0))
        
  images_json = json.dumps(images)
  val = (id, name, category, description, address, transport, mrt, lat, lng, images_json)
  cursor.execute(query, val)  

cnx.commit()