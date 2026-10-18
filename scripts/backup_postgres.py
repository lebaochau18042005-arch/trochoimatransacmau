#!/usr/bin/env python3
"""Private PostgreSQL backup using local pg_dump (PostgreSQL 18 recommended).

Usage:
  Set DATABASE_URL in your local terminal (never commit it).
  python scripts/backup_postgres.py
Requires pg_dump and pg_restore installed locally. Never upload backups to a public repo.
"""
import datetime
import os
import pathlib
import subprocess
import sys

def main():
    url = os.environ.get("DATABASE_URL", "").strip()
    if not url.startswith(("postgresql://", "postgres://")):
        sys.exit("Set DATABASE_URL to the EXTERNAL PostgreSQL URL in your local terminal.")
    folder = pathlib.Path(os.environ.get("BACKUP_DIR", "private_backups"))
    folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination = folder / f"matrix_{stamp}.dump"
    if destination.exists():
        sys.exit("Backup file already exists; refusing to overwrite.")
    try:
        subprocess.run(
            ["pg_dump", "--format=custom", "--no-owner", "--no-acl",
             "--file", str(destination), "--dbname", url],
            check=True,
        )
        subprocess.run(["pg_restore", "--list", str(destination)],
                       check=True, stdout=subprocess.DEVNULL)
        if destination.stat().st_size == 0:
            raise RuntimeError("Backup file is empty")
    except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
        destination.unlink(missing_ok=True)
        sys.exit(f"Backup failed: {type(exc).__name__}; check local PostgreSQL tools and connection.")
    print(f"Backup validated locally: {destination} ({destination.stat().st_size} bytes)")
    print("Keep this file private and test a restore into a disposable database.")

if __name__ == "__main__":
    main()
