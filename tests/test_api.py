"""Tests for the FastAPI endpoints, including the bonus features.

The single most important rule under test: an empty result is ``[]`` with a
200 status, never a 500; a missing file is a 404.
"""

from __future__ import annotations


# --- GET /api/files -------------------------------------------------------


def test_files_empty_db_returns_empty_list(client):
    resp = client.get("/api/files")
    assert resp.status_code == 200
    assert resp.json() == []


def test_files_lists_with_function_counts(client, seeded):
    resp = client.get("/api/files")
    assert resp.status_code == 200
    data = resp.json()

    by_name = {f["name"]: f for f in data}
    assert by_name["auth.py"]["function_count"] == 2   # issue + hash_password
    assert by_name["empty.py"]["function_count"] == 0   # no defs, still listed


def test_files_pagination(client, seeded):
    first = client.get("/api/files", params={"limit": 1, "offset": 0}).json()
    second = client.get("/api/files", params={"limit": 1, "offset": 1}).json()

    assert len(first) == 1
    assert len(second) == 1
    assert first[0]["name"] != second[0]["name"]
    # ordering is by file name, so auth.py comes before empty.py
    assert first[0]["name"] == "auth.py"


# --- GET /api/files/{name}/structure --------------------------------------


def test_structure_returns_definitions(client, seeded):
    resp = client.get("/api/files/auth.py/structure")
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "auth.py"
    assert len(body["definitions"]) == 3


def test_structure_empty_file_returns_empty_definitions(client, seeded):
    resp = client.get("/api/files/empty.py/structure")
    assert resp.status_code == 200
    assert resp.json()["definitions"] == []


def test_structure_missing_file_is_404(client, seeded):
    resp = client.get("/api/files/does_not_exist.py/structure")
    assert resp.status_code == 404


# --- GET /api/search ------------------------------------------------------


def test_search_matches_name_and_docstring(client, seeded):
    # "token" appears in TokenService (name) and in issue's docstring text? no;
    # it matches TokenService by name and the class docstring "...tokens.".
    resp = client.get("/api/search", params={"q": "token"})
    assert resp.status_code == 200
    names = {item["name"] for item in resp.json()}
    assert "TokenService" in names


def test_search_is_case_insensitive(client, seeded):
    lower = client.get("/api/search", params={"q": "token"}).json()
    upper = client.get("/api/search", params={"q": "TOKEN"}).json()
    assert {d["id"] for d in lower} == {d["id"] for d in upper}


def test_search_no_match_returns_empty_list_not_500(client, seeded):
    resp = client.get("/api/search", params={"q": "zzz-nothing-here"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_search_empty_db_returns_empty_list(client):
    resp = client.get("/api/search", params={"q": "anything"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_search_type_filter(client, seeded):
    classes = client.get("/api/search", params={"q": "", "type": "class"}).json()
    functions = client.get("/api/search", params={"q": "", "type": "function"}).json()

    assert all(item["kind"] == "class" for item in classes)
    assert all(item["kind"] == "function" for item in functions)
    assert len(classes) == 1   # only TokenService
    assert len(functions) == 2  # issue + hash_password


def test_search_invalid_type_is_422(client, seeded):
    resp = client.get("/api/search", params={"q": "x", "type": "module"})
    assert resp.status_code == 422


def test_search_pagination(client, seeded):
    page = client.get("/api/search", params={"q": "", "limit": 1, "offset": 0}).json()
    assert len(page) == 1


# --- GET /api/stats -------------------------------------------------------


def test_stats_counts(client, seeded):
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    assert resp.json() == {
        "files": 2,
        "functions": 2,
        "classes": 1,
        "definitions": 3,
    }


def test_stats_empty_db(client):
    resp = client.get("/api/stats")
    assert resp.status_code == 200
    assert resp.json() == {
        "files": 0,
        "functions": 0,
        "classes": 0,
        "definitions": 0,
    }
