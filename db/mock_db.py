from pathlib import Path

from config.settings import DATA_DIR
from utils.io import load_json


class MockDB:
    def __init__(self, data_dir: Path | None = None):
        root = data_dir or DATA_DIR
        self.customers = load_json(root / "customers.json")
        self.products = load_json(root / "products.json")
        self.orders = load_json(root / "orders.json")
        self.tickets = load_json(root / "tickets.json")

        kb_path = root / "knowledge-base.md"
        try:
            with open(kb_path, "r", encoding="utf-8") as f:
                self.kb = f.read()
        except FileNotFoundError:
            self.kb = "Knowledge base not found."


db = MockDB()
