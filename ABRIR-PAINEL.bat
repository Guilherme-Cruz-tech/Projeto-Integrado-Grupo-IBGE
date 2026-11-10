@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Ambiente virtual nao encontrado.
  echo Primeiro crie e instale as dependencias com os comandos do arquivo LEIA-ME-EXECUCAO.md.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m streamlit run app_home.py
pause
