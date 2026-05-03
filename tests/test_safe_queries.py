import pytest

from app_core.db import safe_queries


class FakeStreamlit:
    def __init__(self):
        self.session_state = {}

    def error(self, *_args, **_kwargs):
        return None


@pytest.fixture(autouse=True)
def fake_streamlit(monkeypatch):
    fake = FakeStreamlit()
    monkeypatch.setattr(safe_queries, "st", fake)
    return fake


def test_safe_fetch_one_allows_system_query_case_insensitive(monkeypatch):
    monkeypatch.setattr(safe_queries, "fetch_one", lambda query, params=None: (1,))

    result = safe_queries.safe_fetch_one(
        "SELECT ID FROM BARBERIAS ORDER BY ID LIMIT 1"
    )

    assert result == (1,)


def test_safe_fetch_all_blocks_sensitive_read_without_barberia_id(monkeypatch):
    monkeypatch.setattr(safe_queries, "fetch_all", lambda query, params=None: [])

    with pytest.raises(Exception, match="missing barberia_id WHERE filter"):
        safe_queries.safe_fetch_all("SELECT id, nombre FROM reservas WHERE estado = %s", ("x",))


def test_safe_fetch_all_requires_barberia_id_in_where_clause(monkeypatch):
    monkeypatch.setattr(safe_queries, "fetch_all", lambda query, params=None: [])

    with pytest.raises(Exception, match="missing barberia_id WHERE filter"):
        safe_queries.safe_fetch_all("SELECT id, barberia_id FROM reservas")


def test_barberias_system_read_does_not_allow_tenant_join(monkeypatch):
    monkeypatch.setattr(safe_queries, "fetch_all", lambda query, params=None: [])

    with pytest.raises(Exception, match="missing barberia_id WHERE filter"):
        safe_queries.safe_fetch_all(
            "SELECT b.id, r.id FROM barberias b JOIN reservas r ON r.barberia_id = b.id"
        )


def test_safe_execute_allows_tenant_scoped_update(monkeypatch):
    calls = []

    def fake_execute(query, params=None, fetch_one_result=False):
        calls.append((query, params, fetch_one_result))
        return True

    monkeypatch.setattr(safe_queries, "execute_write", fake_execute)

    ok = safe_queries.safe_execute(
        "UPDATE usuarios SET cortes_acumulados = 0 WHERE usuario = %s AND barberia_id = %s",
        ("cliente", 7),
    )

    assert ok is True
    assert calls


def test_safe_execute_blocks_write_without_barberia_id(monkeypatch):
    monkeypatch.setattr(safe_queries, "execute_write", lambda *args, **kwargs: True)

    with pytest.raises(Exception, match="write missing barberia_id WHERE filter"):
        safe_queries.safe_execute("UPDATE usuarios SET rol = %s WHERE id = %s", ("ADMIN", 1))


def test_safe_execute_allows_explicit_system_exception(monkeypatch):
    monkeypatch.setattr(safe_queries, "execute_write", lambda *args, **kwargs: True)

    ok = safe_queries.safe_execute(
        "UPDATE usuarios SET password = %s WHERE id = %s",
        ("hashed", 1),
        allow_system=True,
        system_reason="login legacy password rehash before tenant context",
    )

    assert ok is True


def test_safe_fetch_all_allows_super_admin_global_query(fake_streamlit, monkeypatch):
    fake_streamlit.session_state["rol"] = "SUPER_ADMIN"
    fake_streamlit.session_state["super_admin_all_barberias"] = True
    monkeypatch.setattr(safe_queries, "fetch_all", lambda query, params=None: [(1,)])

    result = safe_queries.safe_fetch_all("SELECT id FROM reservas WHERE 1=1")

    assert result == [(1,)]
