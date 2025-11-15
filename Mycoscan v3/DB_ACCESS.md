MycoScan — MySQL / MariaDB integration & access guide

This guide shows how to run MySQL (or MariaDB), create a database and user for MycoScan, point the app to that DB, run migrations, and access the DB both via client tools and from Python.

1) Quick option — Docker (recommended for local testing)

PowerShell (run from an elevated prompt if needed):

```powershell
# Pull and run MySQL 8 container
docker run --name mycoscan-mysql -e MYSQL_ROOT_PASSWORD=rootpw -e MYSQL_DATABASE=mycoscan -e MYSQL_USER=myuser -e MYSQL_PASSWORD=mypass -p 3306:3306 -d mysql:8

# Check logs to see when it is ready
docker logs -f mycoscan-mysql
```

2) Create DB / user (if not created by Docker env)

Use the MySQL CLI or Workbench. Example CLI commands:

```powershell
# Connect as root
mysql -u root -p

# In mysql> prompt:
CREATE DATABASE mycoscan;
CREATE USER 'myuser'@'%' IDENTIFIED BY 'mypass';
GRANT ALL PRIVILEGES ON mycoscan.* TO 'myuser'@'%';
FLUSH PRIVILEGES;
EXIT;
```

3) Point MycoScan to the MySQL server

- Edit or create `.env` in the project root (do not commit secrets). Use the same format as `.env.example`:

```
DATABASE_URL=mysql+pymysql://myuser:mypass@localhost:3306/mycoscan
SECRET_KEY=change-me
FLASK_ENV=development
```

4) Install Python dependencies (including `pymysql`)

PowerShell:

```powershell
pip install -r requirements.txt
```

5) Run migrations (Flask-Migrate)

The app uses an app factory (`create_app()`), so set `FLASK_APP` to `main:create_app` before running the Flask CLI migrations.

PowerShell example:

```powershell
# Set env vars for current shell
$env:FLASK_APP = "main:create_app"
$env:FLASK_ENV = "development"

# Initialize migrations (only once)
flask db init

# Create migration script
flask db migrate -m "init"

# Apply migrations
flask db upgrade
```

If `flask db init` fails because a `migrations` folder already exists, skip the `init` step.

6) Start the app

Use the project's runner which prints the DB URI during startup:

```powershell
python run_app.py
```

7) Accessing the DB directly

- GUI: Use MySQL Workbench, DBeaver, or TablePlus with host `localhost` and port `3306`.
- CLI:

```powershell
mysql -u myuser -p -h 127.0.0.1 -P 3306 mycoscan
```

8) Accessing DB from Python (quick test)

This repo includes a small script `tools/test_mysql.py` that reads `DATABASE_URL` and prints whether it can connect and lists tables.

Run:

```powershell
python tools/test_mysql.py
```

9) Notes & troubleshooting

- Firewall/port: ensure `3306` is reachable if running remote DB.
- Driver: `pymysql` is pure-Python and recommended on Windows to avoid compiling `mysqlclient`.
- Production: consider using managed DB services (RDS/Azure Database) and secure credentials via environment or secrets manager.
- If you see `Access denied`, double-check user host (use '%' for remote access) and password.

9) MySQL Workbench (connect to local Docker/MySQL)

- Open MySQL Workbench and create a new connection with:
	- **Connection Method:** Standard (TCP/IP)
	- **Hostname:** 127.0.0.1
	- **Port:** 3306
	- **Username:** myuser
	- **Password:** (enter `mypass` and optionally save in the vault)
	- **Default Schema:** mycoscan

After connecting you will see the `mycoscan` schema and any tables created by migrations.

10) Convenience PowerShell helper

Use `run_with_mysql.ps1` (provided) to set environment variables, run migrations and start the app. Run it from the project root in PowerShell:

```powershell
.\run_with_mysql.ps1
```

The script will:
- set `DATABASE_URL` to the local MySQL container
- install requirements if needed
- initialize migrations (if missing), create migration script, and apply migrations
- start the app via `python run_app.py`

If you prefer to run commands manually, follow the steps in section 5 and 6.

11) Docker Compose (one-command local setup)

This repository includes a `docker-compose.yml` that runs MySQL and the web app together. It mounts the project into the container so you can edit locally and have the container use your code.

From the project root run:

```powershell
docker compose up --build
```

What it does:
- Starts a MySQL 8 container (`mycoscan-db`) with the database `mycoscan` and user `myuser`/`mypass` exposed on port `3306`.
- Builds and starts a `mycoscan-web` container that installs requirements, runs migrations, and starts the Flask app on port `5000`.

After `docker compose up` completes, connect with MySQL Workbench to `127.0.0.1:3306` using `myuser` / `mypass` and open the `mycoscan` schema.

To stop and remove containers and volumes:

```powershell
docker compose down -v
```

Notes:
- If you already started a separate MySQL container on port `3306` (like you did earlier), either stop/remove it first (`docker rm -f mycoscan-mysql`) or modify the `docker-compose.yml` db port mapping to avoid collision.
- The web container mounts the project directory into the container so file changes reflect immediately. This is convenient for development but not ideal for production images.


