"""Универсальный экспорт структурированных данных в JSON, CSV, XML и YAML."""

import csv
import json
from pathlib import Path
import xml.etree.ElementTree as ET


class ExportService:
    def __init__(self, repository, output_directory=None):
        self.repository = repository
        project_root = Path(__file__).resolve().parents[3]
        self.output_directory = Path(output_directory) if output_directory else project_root / "out"

    @staticmethod
    def _xml_value(parent, name, value):
        element = ET.SubElement(parent, str(name))
        if isinstance(value, dict):
            for key, nested_value in value.items():
                ExportService._xml_value(element, key, nested_value)
        elif isinstance(value, list):
            for item in value:
                ExportService._xml_value(element, "item", item)
        elif value is None:
            element.set("nil", "true")
        elif isinstance(value, bool):
            element.text = "true" if value else "false"
        else:
            element.text = str(value)
        return element

    @staticmethod
    def _yaml_scalar(value):
        if value is None:
            return "null"
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, (int, float)):
            return str(value)
        # JSON-строки являются корректными строковыми скалярами YAML 1.2.
        return json.dumps(str(value), ensure_ascii=False)

    @classmethod
    def _yaml_lines(cls, value, indent=0):
        space = " " * indent
        lines = []
        if isinstance(value, dict):
            if not value:
                return [space + "{}"]
            for key, nested in value.items():
                key_text = cls._yaml_scalar(str(key))
                if isinstance(nested, (dict, list)) and nested:
                    lines.append(f"{space}{key_text}:")
                    lines.extend(cls._yaml_lines(nested, indent + 2))
                else:
                    scalar = "{}" if nested == {} else "[]" if nested == [] else cls._yaml_scalar(nested) if not isinstance(nested, (dict, list)) else "{}"
                    lines.append(f"{space}{key_text}: {scalar}")
        elif isinstance(value, list):
            if not value:
                return [space + "[]"]
            for item in value:
                if isinstance(item, (dict, list)) and item:
                    lines.append(space + "-")
                    lines.extend(cls._yaml_lines(item, indent + 2))
                else:
                    scalar = "{}" if item == {} else "[]" if item == [] else cls._yaml_scalar(item) if not isinstance(item, (dict, list)) else "{}"
                    lines.append(f"{space}- {scalar}")
        else:
            lines.append(space + cls._yaml_scalar(value))
        return lines

    @staticmethod
    def _flatten_record(record, prefix=""):
        result = {}
        for key, value in record.items():
            column = f"{prefix}{key}" if not prefix else f"{prefix}_{key}"
            if isinstance(value, dict):
                result.update(ExportService._flatten_record(value, column))
            elif isinstance(value, list):
                result[column] = json.dumps(value, ensure_ascii=False)
            else:
                result[column] = value
        return result

    @classmethod
    def _csv_rows(cls, records):
        """Разворачивает вложенные списки в отдельные строки CSV."""
        rows = []
        for record in records:
            base = {key: value for key, value in record.items() if not isinstance(value, (dict, list))}
            bookings = record.get("bookings")
            if isinstance(bookings, list) and bookings:
                for booking in bookings:
                    combined = dict(base)
                    combined.update(cls._flatten_record({key: value for key, value in booking.items() if key != "manager"}, "booking"))
                    if booking.get("manager"):
                        combined.update(cls._flatten_record(booking["manager"], "manager"))
                    rows.append(combined)
            else:
                rows.append(dict(base))
        return rows

    def export_all(self):
        records = self.repository.get_clients_with_related_data()
        self.output_directory.mkdir(parents=True, exist_ok=True)

        json_path = self.output_directory / "data.json"
        csv_path = self.output_directory / "data.csv"
        xml_path = self.output_directory / "data.xml"
        yaml_path = self.output_directory / "data.yaml"

        json_path.write_text(json.dumps(records, ensure_ascii=False, indent=4), encoding="utf-8")

        csv_rows = self._csv_rows(records)
        fieldnames = list(dict.fromkeys(key for row in csv_rows for key in row))
        with csv_path.open("w", encoding="utf-8-sig", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, extrasaction="ignore")
            if fieldnames:
                writer.writeheader()
                writer.writerows(csv_rows)

        root = ET.Element("clients")
        for record in records:
            self._xml_value(root, "client", record)
        ET.indent(root, space="  ")
        ET.ElementTree(root).write(xml_path, encoding="utf-8", xml_declaration=True)

        yaml_path.write_text("\n".join(self._yaml_lines(records)) + "\n", encoding="utf-8")

        return [json_path, csv_path, xml_path, yaml_path]
