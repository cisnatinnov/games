# games
AI and Games Launcher

# YourGoogleAPIKey
## Create .env File
GOOGLE_API_KEY=YourGoogleAPIKey

## Install Necessary depedencies
pip install -r requirements.txt

## Activate The Virtual Environment
.venv/Scripts/Activate.ps1
## To Create aim_trainer.exe
pyinstaller --noconsole --onefile aim_trainer.py
## To Create coin_catcher.exe
pyinstaller --noconsole --onefile --add-data "assets;assets" coin_catcher.py
## To Create dual_clocker.exe
pyinstaller --noconsole --onefile dual_clocker.py

## Run scripts as modules
You can run the utility scripts with Python's `-m` flag now that `scripts` is a package:

```bash
python -m games.scripts.train_translator --target jawa --epochs 10
python -m games.scripts.infer_translator "salam"
```

The Flask app can be started as before:

```bash
python ai.py
# then open http://localhost:5000/static/translate_demo.html
```