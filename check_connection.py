"""
Quick check that MySQL is running and the database is set up.
Run:  python check_connection.py
"""
import sys

try:
    import db_config
except ModuleNotFoundError as exc:
    sys.exit(f"Missing package: {exc.name}. Run:  python -m pip install -r requirements.txt")

settings = db_config.load_settings()
print(f"Connecting to {settings['user']}@{settings['host']}:{settings['port']} "
      f"database '{settings['database']}' ...")

try:
    conn = db_config.connect()
except Exception as exc:  # show a friendly hint for the common errors
    msg = str(exc)
    print("\nFAILED:", msg)
    if "2003" in msg:
        print("-> MySQL server is not running (or not installed). Start the MySQL service.")
    elif "1045" in msg:
        print("-> Wrong user or password. Create config.ini from config.example.ini.")
    elif "1049" in msg:
        print("-> Database does not exist. Run database/setup_database.sql in MySQL Workbench.")
    sys.exit(1)

cur = conn.cursor()
tables = ["Student", "Instructor", "Vehicle", "Package",
          "StudentPackage", "Lesson", "Exam", "Payment"]
print("\nConnected. Row counts:")
for t in tables:
    cur.execute(f"SELECT COUNT(*) FROM {t}")
    print(f"  {t:<15}{cur.fetchone()[0]:>5}")
conn.close()
print("\nAll good - you can run:  python DrivingSchoolGUI.py")
