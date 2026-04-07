@echo off
title BRVM Tracker - Assistant de Collecte
setlocal

:menu
cls
echo.
echo =======================================================
echo          BRVM TRACKER - GESTIONNAIRE DE DONNEES
echo =======================================================
echo.
echo  [1] METTRE A JOUR MAINTENANT (Immediate)
echo      - Recupere les cours, indices et news tout de suite.
echo.
echo  [2] LANCER LE ROBOT AUTOMATIQUE (Planifie)
echo      - Tourne en fond et s'active chaque jour a 16h00 GMT.
echo.
echo  [3] QUITTER
echo.
echo =======================================================
set /p choice="Selectionnez une option (1, 2 ou 3) : "

if "%choice%"=="1" goto update_now
if "%choice%"=="2" goto start_scheduler
if "%choice%"=="3" goto end
goto menu

:update_now
echo.
echo [INFO] Lancement de la collecte immediate...
echo [INFO] Cela peut prendre 1 a 2 minutes (Scraping en cours).
echo.
cd /d "%~dp0"
call scraper\venv\Scripts\activate.bat
cd scraper
python main_collect.py --now
echo.
echo [OK] Mise a jour terminee !
pause
goto menu

:start_scheduler
echo.
echo [INFO] Activation du robot automatique...
echo [INFO] Gardez cette fenetre ouverte (ou reduisez-la).
echo [INFO] Prochaine collecte : Demain a 16h00 GMT.
echo.
cd /d "%~dp0"
call scraper\venv\Scripts\activate.bat
cd scraper
python main_collect.py
pause
goto menu

:end
exit
