#!/usr/bin/env python3
"""
Script de teste para verificar se o ambiente está funcionando corretamente no Windows
"""

import sys
import os
import platform

def test_python_version():
    """Testa se a versão do Python é compatível"""
    print("🐍 Testando versão do Python...")
    version = sys.version_info
    print(f"   Versão: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("   ✅ Versão do Python compatível")
        return True
    else:
        print("   ❌ Versão do Python incompatível. Necessário Python 3.8+")
        return False

def test_imports():
    """Testa se todas as dependências estão instaladas"""
    print("\n📦 Testando importações...")
    
    dependencies = [
        ('requests', 'requests'),
        ('beautifulsoup4', 'bs4'),
        ('selenium', 'selenium'),
        ('pandas', 'pandas'),
        ('webdriver-manager', 'webdriver_manager'),
        ('lxml', 'lxml'),
        ('openpyxl', 'openpyxl')
    ]
    
    all_ok = True
    for package_name, import_name in dependencies:
        try:
            __import__(import_name)
            print(f"   ✅ {package_name}")
        except ImportError as e:
            print(f"   ❌ {package_name} - {e}")
            all_ok = False
    
    return all_ok

def test_chrome():
    """Testa se o Chrome/Chromium está instalado"""
    print("\n🌐 Testando navegadores...")
    
    import platform
    system = platform.system().lower()
    
    if system == "windows":
        # Windows: testar Chrome primeiro, depois Chromium
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files\Chromium\Application\chrome.exe",
            r"C:\Program Files (x86)\Chromium\Application\chrome.exe"
        ]
    elif system == "linux":
        # Linux: testar Chromium primeiro, depois Chrome
        paths = [
            "/usr/bin/chromium",
            "/usr/bin/chromium-browser", 
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable"
        ]
    elif system == "darwin":  # macOS
        paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium"
        ]
    else:
        print(f"   ❌ Sistema operacional não suportado: {system}")
        return False
    
    for path in paths:
        if os.path.exists(path):
            print(f"   ✅ Navegador encontrado: {path}")
            return True
    
    print("   ❌ Nenhum navegador encontrado")
    print("   💡 Instale Chrome: https://www.google.com/chrome/")
    print("   💡 Ou Chromium: https://www.chromium.org/")
    return False

def test_webdriver():
    """Testa se o WebDriver Manager funciona"""
    print("\n🚗 Testando WebDriver Manager...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("   📥 Baixando ChromeDriver...")
        
        # Configurar opções do Chrome
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # Criar serviço com WebDriver Manager
        service = Service(ChromeDriverManager().install())
        
        # Criar driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Testar navegação
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        
        print(f"   ✅ WebDriver funcionando! Título da página: {title}")
        return True
        
    except Exception as e:
        print(f"   ❌ Erro no WebDriver: {e}")
        return False

def test_folders():
    """Testa se as pastas necessárias podem ser criadas"""
    print("\n📁 Testando criação de pastas...")
    
    try:
        folders = ['dados', 'dados/csv', 'dados/excel', 'logs']
        
        for folder in folders:
            os.makedirs(folder, exist_ok=True)
            print(f"   ✅ Pasta {folder} criada/verificada")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erro ao criar pastas: {e}")
        return False

def main():
    """Função principal de teste"""
    print("🧪 TESTE DE AMBIENTE - SCRAPER INTEGRAL MÉDICA")
    print("=" * 50)
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Arquitetura: {platform.architecture()[0]}")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_imports,
        test_chrome,
        test_folders,
        test_webdriver
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    if all(results):
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ O scraper está pronto para uso no Windows")
        print("\nPara usar:")
        print("   python main.py")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique os erros acima e:")
        print("   1. Instale as dependências: pip install -r requirements.txt")
        print("   2. Instale o Chrome: https://www.google.com/chrome/")
        print("   3. Verifique se o Python está no PATH")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main() 