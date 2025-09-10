# games
AI and Games Launcher

# YourGoogleAPIKey
## Create .env File
GOOGLE_API_KEY=YourGoogleAPIKey

## activate the venv
.venv/Scripts/Activate.ps1

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