import app as brevet_app

client = brevet_app.app.test_client()

def clear_db():
    brevet_app.db.times.delete_many({})

ROW = {"km": "200", "open": "Sun 1/1 5:53", "close": "Sun 1/1 13:20", "location": ""}

def test_submit_empty():
    clear_db()
    resp = client.post("/insert", json={"items": []})
    assert "error" in resp.get_json()

def test_submit_with_rows():
    clear_db()
    resp = client.post("/insert", json={"items": [dict(ROW)]})
    assert resp.get_json()["status"] == "ok"

def test_display_with_data():
    clear_db()
    client.post("/insert",json={"items": [dict(ROW)]})
    resp = client.get("/fetch")
    assert "result" in resp.get_json()


def test_display_empty():
   clear_db()
   resp = client.get("/fetch")
   assert "error" in resp.get_json()