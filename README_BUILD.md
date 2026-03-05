Packaging and building a Windows executable

1) Prepare environment

- Create and activate a virtual environment (recommended):

  python -m venv .venv
  .venv\Scripts\activate

- Install requirements:

  pip install -r requirements.txt

2) Test locally

- Run the app normally to ensure it works:

  python run_app.py

3) Build the executable (Windows)

- Use the provided `build.bat` from project root (PowerShell or cmd):

  build.bat

- The script runs PyInstaller and produces a single-file executable in `dist\run_app.exe`.

Notes & gotchas
- `--add-data "templates;templates"` bundles the `templates` folder so Flask can render templates from the frozen app.
- `todo.db` is copied into the same folder as the executable. If you want a user-writable DB outside the exe, consider placing the DB in `%APPDATA%` or another writable location and adjust `get_db_connection()` accordingly.
- If you prefer a multi-file bundle instead of onefile, remove `--onefile` and PyInstaller will generate a folder with dependencies (simpler for debugging).
- Test the built exe on a clean Windows machine (no Python required).
