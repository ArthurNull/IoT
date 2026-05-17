import tempfile
from pathlib import Path
import app as featherfield_app

def test_leaderboard_route_loads():
    database_path = Path(tempfile.gettempdir()) / "featherfield_test_leaderboard.sqlite"
    featherfield_app.app.config.update(TESTING=True, DATABASE=str(database_path))
    if database_path.exists():
        database_path.unlink()
    client = featherfield_app.app.test_client()
    response = client.get("/leaderboard")
    assert response.status_code == 200
    assert b"Ranger Board" in response.data
    assert b"Ranger Sandy" in response.data
