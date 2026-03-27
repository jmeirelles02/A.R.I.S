@echo off
echo =========================================
echo Setup do A.R.I.S para Windows
echo =========================================

echo.
echo ^> Criando ambiente virtual (venv)...
python -m venv venv

echo.
echo ^> Instalando dependencias Python...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ^> Instalando dependencias do Agent-ui (NPM)...
cd Agent-ui
call npm install
cd ..

echo.
echo Setup concluido com sucesso!
echo Para rodar, basta executar o aris.vbs ou iniciar.bat
pause
