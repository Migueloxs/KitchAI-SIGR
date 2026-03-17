from datetime import datetime
from pathlib import Path


class MigrationRunner:
    def __init__(self, db_client):
        self.db = db_client
        self.migrations_dir = Path(__file__).parent / "versions"

    def run(self) -> None:
        self._ensure_migrations_table()

        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        for migration_file in migration_files:
            version = migration_file.stem
            if self._is_applied(version):
                continue

            sql = migration_file.read_text(encoding="utf-8")
            statements = [stmt.strip() for stmt in sql.split(";") if stmt.strip()]
            for statement in statements:
                self.db.execute(statement)
            self.db.execute(
                "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                [version, datetime.now().isoformat()],
            )
            print(f"✅ Migracion aplicada: {version}")

    def _ensure_migrations_table(self) -> None:
        self.db.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
            """
        )

    def _is_applied(self, version: str) -> bool:
        result = self.db.execute(
            "SELECT COUNT(*) FROM schema_migrations WHERE version = ?",
            [version],
        )
        return result.rows[0][0] > 0


def run_migrations(db_client) -> None:
    runner = MigrationRunner(db_client)
    runner.run()
