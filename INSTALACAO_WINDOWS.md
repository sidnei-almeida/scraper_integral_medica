# 🪟 Instalação do Scraper Integral Médica - Windows

## Pré-requisitos

### 1. Instalar Python
- Baixar Python 3.8+ em: https://www.python.org/downloads/
- ✅ **IMPORTANTE**: Marcar a opção "Add Python to PATH" durante a instalação

### 2. Instalar Navegador
- **Google Chrome** (recomendado): https://www.google.com/chrome/
- **OU Chromium**: https://www.chromium.org/getting-involved/download-chromium/

⚡ **DETECÇÃO AUTOMÁTICA**: O scraper detecta automaticamente qual navegador está instalado:
- Windows: Procura Chrome primeiro, depois Chromium
- Linux: Procura Chromium primeiro, depois Chrome
- macOS: Procura Chrome primeiro, depois Chromium

## Instalação do Scraper

### 1. Abrir Prompt de Comando
- Pressionar `Windows + R`
- Digitar `cmd` e pressionar Enter

### 2. Navegar até a pasta do projeto
```cmd
cd C:\caminho\para\scraper_integral_medica
```

### 3. Instalar dependências
```cmd
pip install -r requirements.txt
```

### 4. Executar o scraper
```cmd
python main.py
```

## ✅ Vantagens da Detecção Automática

- **Inteligente**: Detecta automaticamente Chrome ou Chromium
- **Multiplataforma**: Funciona em Windows, Linux e macOS
- **Sem configuração**: Não precisa especificar qual navegador usar
- **Fallback**: Se não encontrar, usa WebDriver Manager automaticamente

## 🔧 Solução de Problemas

### Erro: "pip não é reconhecido"
```cmd
python -m pip install -r requirements.txt
```

### Erro: "python não é reconhecido"
- Reinstalar Python marcando "Add Python to PATH"
- Ou usar: `py main.py` ao invés de `python main.py`

### Erro: "Navegador não encontrado"
- Instalar Chrome OU Chromium
- O scraper detecta automaticamente qual está disponível

### Erro de ChromeDriver
- O WebDriver Manager resolve automaticamente
- Primeiro tenta detecção automática, depois WebDriver Manager

## 📞 Suporte

Se tiver problemas, forneça:
1. Versão do Python: `python --version`
2. Navegador instalado: Chrome ou Chromium
3. Sistema operacional
4. Mensagem de erro completa

## 🚀 Uso

Após instalação:
1. Execute `python main.py`
2. Escolha a opção desejada:
   - **1**: Coletar apenas URLs
   - **2**: Coletar dados nutricionais completos
   - **3**: Testar produto específico
   - **4**: Cancelar

Os dados serão salvos em:
- `dados/csv/dados.csv`
- `dados/excel/dados.xlsx`

## 🌍 Compatibilidade

### ✅ Navegadores Suportados
- Google Chrome (qualquer versão)
- Chromium (qualquer versão)
- Detecção automática por sistema operacional

### ✅ Sistemas Operacionais
- Windows 10/11
- Linux (Ubuntu, Debian, Arch, etc.)
- macOS

### 🔧 Estratégia de Detecção

**Windows:**
1. `C:\Program Files\Google\Chrome\Application\chrome.exe`
2. `C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`
3. `C:\Program Files\Chromium\Application\chrome.exe`
4. `C:\Program Files (x86)\Chromium\Application\chrome.exe`

**Linux:**
1. `/usr/bin/chromium`
2. `/usr/bin/chromium-browser`
3. `/usr/bin/google-chrome`
4. `/usr/bin/google-chrome-stable`

**macOS:**
1. `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
2. `/Applications/Chromium.app/Contents/MacOS/Chromium` 