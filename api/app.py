import datetime
import sqlite3
import uvicorn
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
import sys
import os
sys.path.insert(0, os.path.realpath(os.path.pardir))

STATIC_FOLDER = 'static'

isdir = os.path.isdir(STATIC_FOLDER)
if not isdir:
    os.makedirs(STATIC_FOLDER)

DB_FOLDER = 'db'

isdir = os.path.isdir(DB_FOLDER)
if not isdir:
    os.makedirs(DB_FOLDER)


origins = [
    # "http://localhost",
    # "http://localhost:8080",
    '*'
]

app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_FOLDER), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
sqlite_db_filenbame = os.path.join(DB_FOLDER, 'example.db')

if not os.path.isfile(sqlite_db_filenbame):
    with sqlite3.connect(sqlite_db_filenbame) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                CREATE TABLE check_table (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        print('check_table created')
        conn.commit()


@app.post('/api/process')
async def process():
    # 為資料庫新增一筆打卡資料
    with sqlite3.connect(sqlite_db_filenbame) as conn:
        t = datetime.datetime.now()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO check_table (created_at)
            VALUES (?)
        """, (t,))
        conn.commit()

    return JSONResponse(status_code=200, content={"result": "ok", "data": t.strftime("%Y-%d-%m %H:%M:%S")})


@app.get('/api/get_all_records')
async def get_all_records():
    rows = []
    stander_time_string = " 07:10:00"
    str_sql = f"""
    SELECT 
        created_at,
        CAST(
            (JULIANDAY(created_at) - JULIANDAY(DATE(created_at) || ' {stander_time_string}')) * 24 * 60 
            AS INTEGER
        ) AS difference_min
    FROM 
        check_table 
    order by 
        created_at desc;
  """
    with sqlite3.connect(sqlite_db_filenbame) as conn:
        cursor = conn.cursor()
        cursor.execute(str_sql)
        rows = cursor.fetchall()
    return JSONResponse(status_code=200, content={"result": "ok", "data": rows})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run(app, log_level='info', host='0.0.0.0', port=port)
