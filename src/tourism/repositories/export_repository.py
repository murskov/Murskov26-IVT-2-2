"""Получение связанных данных для экспорта."""

from tourism.database import get_connection


class ExportRepository:
    """Репозиторий данных клиентов и связанных с ними заявок/туров."""

    def get_clients_with_related_data(self):
        query = """
            SELECT
                c.client_id,
                c.full_name,
                c.phone,
                c.email,
                c.balance,
                b.booking_id,
                b.booking_date,
                b.status AS booking_status,
                t.tour_id,
                t.title AS tour_title,
                t.destination,
                t.price AS tour_price,
                m.manager_id,
                m.full_name AS manager_name
            FROM clients AS c
            LEFT JOIN bookings AS b ON b.client_id = c.client_id
            LEFT JOIN tours AS t ON t.tour_id = b.tour_id
            LEFT JOIN managers AS m ON m.manager_id = b.manager_id
            ORDER BY c.client_id, b.booking_id
        """
        with get_connection() as db:
            rows = db.execute(query).fetchall()

        clients_by_id = {}
        for row in rows:
            client_id = row["client_id"]
            if client_id not in clients_by_id:
                clients_by_id[client_id] = {
                    "client_id": client_id,
                    "full_name": row["full_name"],
                    "phone": row["phone"],
                    "email": row["email"],
                    "balance": row["balance"],
                    "bookings": [],
                }

            if row["booking_id"] is not None:
                booking = {
                    "booking_id": row["booking_id"],
                    "booking_date": row["booking_date"],
                    "status": row["booking_status"],
                    "tour": None,
                    "manager": None,
                }
                if row["tour_id"] is not None:
                    booking["tour"] = {
                        "tour_id": row["tour_id"],
                        "title": row["tour_title"],
                        "destination": row["destination"],
                        "price": row["tour_price"],
                    }
                if row["manager_id"] is not None:
                    booking["manager"] = {
                        "manager_id": row["manager_id"],
                        "full_name": row["manager_name"],
                    }
                clients_by_id[client_id]["bookings"].append(booking)

        return list(clients_by_id.values())
