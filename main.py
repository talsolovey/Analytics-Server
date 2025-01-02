from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone
import sqlite3

# Pydantic model for incoming request data
class EventData(BaseModel):
    userid: str
    eventname: str

# Initialize FastAPI app
app = FastAPI()

# --- Database setup ---
# Create a connection to the SQLite database (will create the DB file if it doesn't exist)
conn = sqlite3.connect("events.db", check_same_thread=False)
cursor = conn.cursor()

# Create a table if it doesn't already exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        eventtimestamputc TEXT NOT NULL,
        userid TEXT NOT NULL,
        eventname TEXT NOT NULL
    )
''')
conn.commit()

@app.post("/process_event")
def process_event(event_data: EventData):
    """
    Save data into an SQLite database with:
      - eventtimestamputc (UTC time)
      - userid
      - eventname
    """
    # Get the current UTC timestamp (in ISO format, for example)
    eventtimestamputc = datetime.now(timezone.utc).isoformat()

    # Insert the event data into the database
    cursor.execute('''
        INSERT INTO events (eventtimestamputc, userid, eventname)
        VALUES (?, ?, ?)
    ''', (eventtimestamputc, event_data.userid, event_data.eventname))
    conn.commit()

    return {
        "status": "success",
        "eventtimestamputc": eventtimestamputc,
        "userid": event_data.userid,
        "eventname": event_data.eventname
    }
