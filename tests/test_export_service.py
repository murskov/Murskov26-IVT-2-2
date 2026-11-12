import csv
import json
import xml.etree.ElementTree as ET

from tourism.services.export_service import ExportService


class FakeExportRepository:
    def get_clients_with_related_data(self):
        return [
            {
                "client_id": 1,
                "full_name": "Иванов Иван",
                "phone": "+79990000000",
                "email": "ivanov@example.com",
                "balance": 1200.0,
                "bookings": [
                    {
                        "booking_id": 5,
                        "booking_date": "2026-11-12",
                        "status": "Новая",
                        "tour": {"tour_id": 2, "title": "Отдых в Сочи", "destination": "Сочи", "price": 45000.0},
                        "manager": None,
                    }
                ],
            }
        ]


def test_export_creates_four_valid_files(tmp_path):
    service = ExportService(FakeExportRepository(), tmp_path / "out")
    paths = service.export_all()

    assert {path.name for path in paths} == {"data.json", "data.csv", "data.xml", "data.yaml"}
    data = json.loads((tmp_path / "out" / "data.json").read_text(encoding="utf-8"))
    assert data[0]["bookings"][0]["tour"]["title"] == "Отдых в Сочи"

    with (tmp_path / "out" / "data.csv").open(encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    assert rows[0]["booking_booking_id"] == "5"
    assert rows[0]["booking_tour_title"] == "Отдых в Сочи"

    root = ET.parse(tmp_path / "out" / "data.xml").getroot()
    assert root.find("client/bookings/item/tour/title").text == "Отдых в Сочи"

    yaml_text = (tmp_path / "out" / "data.yaml").read_text(encoding="utf-8")
    assert '"Иванов Иван"' in yaml_text
    assert '"booking_id": 5' in yaml_text
