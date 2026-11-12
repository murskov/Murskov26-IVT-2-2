from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SERVICES = ROOT / "src" / "tourism" / "services"

def test_services_do_not_access_database_directly():
    for path in SERVICES.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "sqlite3" not in source
        assert "get_connection" not in source


def test_models_are_separate_dataclasses():
    model_files = list((ROOT / "src" / "tourism" / "models").glob("*.py"))
    names = {path.stem for path in model_files}
    assert {"client", "tour", "booking", "manager", "administrator"}.issubset(names)
