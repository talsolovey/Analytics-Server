from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import sqlite3

# Pydantic models
class EventData(BaseModel):
    userid: str
    eventname: str

class ReportRequest(BaseModel):
    lastseconds: int
    userid: str

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

@app.get("/get_reports")
def get_reports(report_req: ReportRequest):
    """
    Returns all events for the given 'userid' that occurred
    within the last 'lastseconds' seconds.
    """

    # Calculate the cutoff time
    now_utc = datetime.now(timezone.utc)
    cutoff_datetime = now_utc - timedelta(seconds=report_req.lastseconds)
    cutoff_str = cutoff_datetime.isoformat()

    # Retrieve matching events from the database
    cursor.execute('''
        SELECT id, eventtimestamputc, userid, eventname
          FROM events
         WHERE userid = ?
           AND eventtimestamputc >= ?
         ORDER BY eventtimestamputc DESC
    ''', (report_req.userid, cutoff_str))
    rows = cursor.fetchall()

    # Convert rows to a list of dicts for JSON response
    events_list = []
    for row in rows:
        events_list.append({
            "id": row[0],
            "eventtimestamputc": row[1],
            "userid": row[2],
            "eventname": row[3]
        })

    return {
        "events": events_list
    }
