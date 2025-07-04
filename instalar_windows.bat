@echo off
echo ======================================================
echo    INSTALADOR SCRAPER INTEGRAL MEDICA - WINDOWS
echo ======================================================
echo.

echo 📋 Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python não encontrado!
    echo 💡 Instale o Python em: https://www.python.org/downloads/
    echo    IMPORTANTE: Marque "Add Python to PATH" durante a instalação
    pause
    exit /b 1
)

echo ✅ Python encontrado!
echo.

echo 📦 Instalando dependências...
echo.

pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Erro ao instalar dependências!
    echo 🔧 Tentando com python -m pip...
    python -m pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ Falha na instalação!
        pause
        exit /b 1
    )
)

echo.
echo ✅ Dependências instaladas com sucesso!
echo.

echo 🧪 Executando teste de ambiente...
echo.

python teste_windows.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ Alguns testes falharam!
    echo 🔧 Verifique os erros acima
    pause
    exit /b 1
)

echo.
echo ======================================================
echo    🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!
echo ======================================================
echo.
echo Para usar o scraper:
echo    python main.py
echo.
echo Arquivos serão salvos em:
echo    dados/csv/dados.csv
echo    dados/excel/dados.xlsx
echo.
echo ======================================================
pause 