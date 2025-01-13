import pytest
from fastapi.testclient import TestClient
from app import app, conn, cursor
from typing import Tuple, Dict, Any

# Initialize the FastAPI test client
client = TestClient(app)

from typing import Generator

@pytest.fixture(autouse=True)
def setup_and_teardown_db() -> Generator[None, None, None]:
    """
    A fixture that clears the 'events' table before and after each test,
    ensuring each test runs in a clean state.
    """
    # Clear table before each test
    cursor.execute("DELETE FROM events")
    conn.commit()
    yield
    # Clear table after each test
    cursor.execute("DELETE FROM events")
    conn.commit()

@pytest.fixture
def post_process_event() -> Tuple[Any, Dict[str, str]]:
    """
    A fixture that sends a POST request to /process_event
    and returns (response, payload).
    """
    payload = {"userid": "test_user", "eventname": "test_event"}
    response = client.post("/process_event", json=payload)
    return response, payload

def test_status_code_is_200(post_process_event: Tuple[Any, Dict[str, str]]) -> None:
    response, _ = post_process_event
    assert response.status_code == 200

def test_response_status_is_success(post_process_event: Tuple[Any, Dict[str, str]]) -> None:
    response, _ = post_process_event
    data = response.json()
    assert data["status"] == "success"

def test_response_userid_matches_input(post_process_event: Tuple[Any, Dict[str, str]]) -> None:
    response, payload = post_process_event
    data = response.json()
    assert data["userid"] == payload["userid"]

def test_response_eventname_matches_input(post_process_event: Tuple[Any, Dict[str, str]]) -> None:
    response, payload = post_process_event
    data = response.json()
    assert data["eventname"] == payload["eventname"]

def test_response_includes_eventtimestamputc(post_process_event: Tuple[Any, Dict[str, str]]) -> None:
    response, _ = post_process_event
    data = response.json()
    assert "eventtimestamputc" in data

def test_db_inserted_record_exists(post_process_event: Tuple[Any, Dict[str, str]]) -> None:
    _, payload = post_process_event
    cursor.execute(
        """
        SELECT userid, eventname, eventtimestamputc
        FROM events
        WHERE userid = ? AND eventname = ?
        """,
        (payload["userid"], payload["eventname"]),
    )
    row = cursor.fetchone()
    assert row is not None

def test_db_userid_is_correct(post_process_event: Tuple[Any, Dict[str, str]]) -> None:
    _, payload = post_process_event
    cursor.execute(
        """
        SELECT userid FROM events
        WHERE userid = ? AND eventname = ?
        """,
        (payload["userid"], payload["eventname"]),
    )
    row = cursor.fetchone()
    assert row[0] == payload["userid"]

def test_db_eventname_is_correct(post_process_event: Tuple[Any, Dict[str, str]]) -> None:
    _, payload = post_process_event
    cursor.execute(
        """
        SELECT eventname FROM events
        WHERE userid = ? AND eventname = ?
        """,
        (payload["userid"], payload["eventname"]),
    )
    row = cursor.fetchone()
    assert row[0] == payload["eventname"]

def test_db_eventtimestamputc_is_not_null(post_process_event: Tuple[Any, Dict[str, str]]) -> None:
    _, payload = post_process_event
    cursor.execute(
        """
        SELECT eventtimestamputc FROM events
        WHERE userid = ? AND eventname = ?
        """,
        (payload["userid"], payload["eventname"]),
    )
    row = cursor.fetchone()
    assert row[0] is not None
