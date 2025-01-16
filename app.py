from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
import sqlite3
from typing import Dict, List, Any
import logging
from logging.handlers import RotatingFileHandler
import json

# Configure logging
handler = RotatingFileHandler("app.log", maxBytes=1_000_000, backupCount=3)
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Pydantic models
class EventData(BaseModel):
    userid: str
    eventname: str

class ReportRequest(BaseModel):
    lastseconds: int
    userid: str

# Initialize FastAPI app
app = FastAPI()

# Create a connection to the SQLite database
conn: sqlite3.Connection = sqlite3.connect("events.db", check_same_thread=False)
cursor: sqlite3.Cursor = conn.cursor()

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
def process_event(event_data: EventData) -> Dict[str, str]:
    """
    Save data into an SQLite database with:
      - eventtimestamputc (UTC time)
      - userid
      - eventname
    """
    # Get the current UTC timestamp (in ISO format, for example)
    eventtimestamputc: str = datetime.now(timezone.utc).isoformat()

    try:
        # Insert the event data into the database
        cursor.execute('''
            INSERT INTO events (eventtimestamputc, userid, eventname)
            VALUES (?, ?, ?)
        ''', (eventtimestamputc, event_data.userid, event_data.eventname))
        conn.commit()
        logger.info(json.dumps({
            "action": "process_event",
            "userid": event_data.userid,
            "eventname": event_data.eventname,
            "timestamp": eventtimestamputc,
        }))
    except Exception as e:
        logger.exception("Error processing event for userid: %s", event_data.userid)

    return {"status": "success", "eventtimestamputc": eventtimestamputc}


@app.get("/get_reports")
def get_reports(report_req: ReportRequest) -> Dict[str, List[Dict[str, Any]]]:
    """
    Returns all events for the given 'userid' that occurred
    within the last 'lastseconds' seconds.
    """

    # Calculate the cutoff time
    now_utc: datetime = datetime.now(timezone.utc)
    cutoff_datetime: datetime = now_utc - timedelta(seconds=report_req.lastseconds)
    cutoff_str: str = cutoff_datetime.isoformat()

    try:
        # Retrieve matching events from the database
        cursor.execute('''
            SELECT id, eventtimestamputc, userid, eventname
            FROM events
            WHERE userid = ?
            AND eventtimestamputc >= ?
            ORDER BY eventtimestamputc DESC
        ''', (report_req.userid, cutoff_str))
        rows: List[tuple] = cursor.fetchall()
        logger.info("Fetched %d events for user %s", len(rows), report_req.userid)
    except Exception as e:
        logger.exception("Error retrieving events for user %s", report_req.userid)
        return {"events": []}

    # Convert rows to a list of dicts for JSON response
    events_list: List[Dict[str, Any]] = [
        {"id": row[0], "eventtimestamputc": row[1], "userid": row[2], "eventname": row[3]}
        for row in rows
    ]

    return {
        "events": events_list
    }
