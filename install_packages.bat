@echo off
REM Verify pip
py -m ensurepip --upgrade

REM Install packages from requirements.txt
py -m pip install -r requirements.txt