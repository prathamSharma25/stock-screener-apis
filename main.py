from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
import mysql.connector
from datetime import datetime, time
import os
import asyncio
from typing import AsyncGenerator


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


def get_db_connection():
    conn = mysql.connector.connect(
        host=os.environ['SS_DB_HOST'],
        user=os.environ['SS_DB_USER'],
        password=os.environ['SS_DB_PASSWORD'],
        database=os.environ['SS_DB_NAME']
    )
    return conn


def fetch_data(ticker):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM stockdatarealtime WHERE symbol=%s order by timestamp", (ticker, ))
    data = cursor.fetchall()
    conn.close()
    return data


async def data_streamer(ticker) -> AsyncGenerator[str, None]:
    while datetime.now().time()<=time(17, 45, 0, 000000):
        data = fetch_data(ticker)
        yield f"data: {data}\n\n"
        await asyncio.sleep(300)


@app.get("/stream", response_class=StreamingResponse)
async def stream_data(ticker):
    return StreamingResponse(data_streamer(ticker), media_type="text/event-stream")


@app.get("/ticker", response_class=JSONResponse)
def get_data(ticker):
    return JSONResponse(fetch_data(ticker))
