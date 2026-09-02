# Running This Project on Linux with VirtualBox

This guide is written for a complete beginner. Follow it in order.

Your project is a Flask Python app.

Important things about this project:

- Start command: `python run.py`
- Dependencies file: `requirements.txt`
- It uses `.env` for configuration
- By default it can run with SQLite
- It can also use MySQL if `USE_MYSQL=true`

For your first Linux run, I strongly recommend using SQLite because it is much easier.

## 1. What you need before starting

Make sure you already have:

- VirtualBox installed on Windows
- A Linux ISO downloaded
- Your project uploaded to GitHub
- Internet connection inside the Linux VM

Recommended Linux:

- Ubuntu 24.04 LTS or Ubuntu 22.04 LTS

## 2. Create the Linux virtual machine

1. Open VirtualBox.
2. Click `New`.
3. Give the VM a name like `Ubuntu-Project`.
4. Select your Linux ISO file.
5. Choose enough RAM.
   A good safe option is `4096 MB` if your PC can handle it.
6. Give it at least `25 GB` storage.
7. Finish the setup and start the VM.

## 3. Install Linux inside the VM

1. Start the VM.
2. Follow the Ubuntu installer.
3. Choose your language, keyboard, username, and password.
4. Complete installation.
5. Restart when Ubuntu asks.
6. Log in.

## 4. Open the terminal in Linux

In Ubuntu:

- Press `Ctrl + Alt + T`

You will use this terminal for almost everything below.

## 5. Update Linux first

Run:

```bash
sudo apt update
sudo apt upgrade -y
```

It may ask for your Linux password.

## 6. Install Python and basic tools

Run:

```bash
sudo apt install -y python3 python3-pip python3-venv git build-essential python3-dev libffi-dev
```

This installs:

- Python
- pip
- virtual environment support
- Git
- basic build tools needed by some Python packages

## 7. Get your project into Linux

You have 2 ways to do this.

### Option A: Clone from GitHub (Recommended)

This is the easiest and cleanest method.

Run:

```bash
git clone YOUR_GITHUB_REPO_URL
```

Example:

```bash
git clone https://github.com/yourname/your-repo.git
```

Then move into the project:

```bash
cd your-repo-folder
```

### Option B: Use a shared folder from Windows

Only use this if you do not want to clone from GitHub.

1. Shut down the VM.
2. In VirtualBox, open `Settings` for your VM.
3. Go to `Shared Folders`.
4. Add your Windows project folder.
5. Start the VM again.
6. Open the shared folder inside Linux.

If both options are available, use Option A.

## 8. Confirm the project files are present

Inside the project folder, run:

```bash
ls
```

You should see files like:

- `run.py`
- `requirements.txt`
- `app/`
- `tests/`

## 9. Create a Python virtual environment

Run:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

After activation, your terminal usually shows `(.venv)` at the left.

## 10. Install project dependencies

Run:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If this finishes without errors, your Python setup is ready.

## 11. Set up the `.env` file

This project reads configuration from `.env`.

Because you already have a working Windows project, the easiest way is:

1. Open the `.env` from your Windows project
2. Copy the same values into the Linux project `.env`

If your project folder from GitHub does not contain `.env`, create it manually.

For the easiest Linux setup, use SQLite first.

Example `.env` for SQLite:

```env
SECRET_KEY=your_secret_key_here
USE_MYSQL=False
DATABASE_URL=sqlite:///expense_portal.db
```

Notes:

- `SECRET_KEY` can be any long random text
- Leave `USE_MYSQL=False` for the first run
- With SQLite, you do not need to install MySQL

## 12. Run the project

Make sure you are:

- inside the project folder
- virtual environment is activated

Then run:

```bash
python3 run.py
```

If everything is correct, Flask should start and show a local address, usually:

```bash
http://127.0.0.1:5000
```

## 13. Open the app in Linux

Inside the Linux VM, open the browser and go to:

```text
http://127.0.0.1:5000
```

If the app loads, your project is running successfully on Linux.

## 14. Stop the app

In the terminal where the app is running:

- Press `Ctrl + C`

## 15. Run the tests

To check whether the project works properly on Linux, run:

```bash
pytest
```

If you want more detailed output:

```bash
pytest -v
```

## 16. Daily workflow after the first setup

Whenever you open the VM later, do this:

```bash
cd your-repo-folder
source .venv/bin/activate
python3 run.py
```

For tests:

```bash
cd your-repo-folder
source .venv/bin/activate
pytest
```

## 17. If you want to pull the latest code from GitHub

Inside the project folder, run:

```bash
git pull
```

If you install new packages later, run:

```bash
pip install -r requirements.txt
```

## 18. Optional: Run with MySQL instead of SQLite

Only do this if your instructor specifically wants MySQL on Linux.

### Install MySQL

```bash
sudo apt install -y mysql-server
```

Start MySQL:

```bash
sudo systemctl start mysql
sudo systemctl enable mysql
```

Secure MySQL:

```bash
sudo mysql_secure_installation
```

### Update `.env`

Example:

```env
SECRET_KEY=your_secret_key_here
USE_MYSQL=True
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_NAME=expense_portal
```

Then run the app:

```bash
python3 run.py
```

This project already tries to create the MySQL database automatically when it starts.

## 19. Common problems and fixes

### Problem: `python3: command not found`

Run:

```bash
sudo apt install -y python3
```

### Problem: `pip: command not found`

Run:

```bash
sudo apt install -y python3-pip
```

### Problem: `No module named venv`

Run:

```bash
sudo apt install -y python3-venv
```

### Problem: package install fails during `pip install -r requirements.txt`

Run:

```bash
sudo apt install -y build-essential python3-dev libffi-dev
```

Then try again:

```bash
pip install -r requirements.txt
```

### Problem: `.env` is missing

Create a `.env` file in the project root and add:

```env
SECRET_KEY=your_secret_key_here
USE_MYSQL=False
DATABASE_URL=sqlite:///expense_portal.db
```

### Problem: port 5000 already in use

Run the app on another port:

```bash
flask run --port 5001
```

If you use this command, first set the app variable:

```bash
export FLASK_APP=run.py
flask run --port 5001
```

### Problem: Git is not installed

Run:

```bash
sudo apt install -y git
```

## 20. Easiest full command flow

If you want the shortest version of the full process, it is this:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git build-essential python3-dev libffi-dev
git clone YOUR_GITHUB_REPO_URL
cd your-repo-folder
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Then create `.env` with:

```env
SECRET_KEY=your_secret_key_here
USE_MYSQL=False
DATABASE_URL=sqlite:///expense_portal.db
```

Then run:

```bash
python3 run.py
```

## 21. What I recommend you do

For your instructor demo or submission:

1. Create Ubuntu VM
2. Install Python tools
3. Clone the project from GitHub
4. Create and activate `.venv`
5. Install `requirements.txt`
6. Add `.env`
7. Keep `USE_MYSQL=False`
8. Run `python3 run.py`
9. Open `http://127.0.0.1:5000`
10. Run `pytest` to prove it works on Linux

## 22. Final note

Do not copy your Windows `.venv` folder into Linux.

Always create a fresh virtual environment in Linux with:

```bash
python3 -m venv .venv
```

That is the correct way.
