@echo off
chcp 65001 >nul
cd /d "C:\leemay_project"
echo ==== START %date% %time% ==== > "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.out.log"
echo PYTHONPATH=%PYTHONPATH% >> "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.out.log"
echo PORT=%PORT% >> "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.out.log"
echo FLASK_RUN_PORT=%FLASK_RUN_PORT% >> "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.out.log"
echo. >> "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.out.log"
echo ==== STDERR ==== > "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.err.log"
where python >> "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.out.log" 2>> "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.err.log"
python --version >> "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.out.log" 2>> "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.err.log"
echo. >> "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.out.log"
python -u "C:\leemay_project\upbit-smart-bot-v8.0-ULTIMATE.py" >> "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.out.log" 2>> "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.err.log"
echo EXITCODE=%errorlevel% >> "C:\leemay_project\logs\ai_trading_5000_20260221_215423_324_23810.err.log"
