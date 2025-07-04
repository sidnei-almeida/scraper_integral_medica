# 🚀 Scraper Integral Médica - Dados Nutricionais

Coleta dados nutricionais de **TODOS** os produtos da Integral Médica de forma automatizada e organizada.

## 📋 O que faz este programa?

- **Acessa automaticamente** o site da Integral Médica
- **Carrega TODOS os produtos** (clica até 8 vezes em "Ver mais produtos")
- **Extrai dados nutricionais** de cada produto individual
- **Salva tudo em CSV** para análise posterior

## 🎯 Dados Coletados

| Campo | Descrição |
|-------|-----------|
| URL | Link do produto |
| PORÇÃO (g) | Tamanho da porção |
| CALORIAS (kcal) | Valor energético |
| CARBOIDRATOS (g) | Quantidade de carboidratos |
| PROTEÍNAS (g) | Quantidade de proteínas |
| GORDURAS_TOTAIS (g) | Gorduras totais |
| GORDURAS_SATURADAS (g) | Gorduras saturadas |
| FIBRAS (g) | Fibras alimentares |
| AÇÚCARES (g) | Açúcares |
| SÓDIO (mg) | Sódio |

## 🛠️ Instalação (Apenas uma vez)

### 1. Baixar o projeto
```bash
git clone <url-do-repositorio>
cd scraper_integral_medica
```

### 2. Instalar Python
- Baixe Python 3.8+ em: https://python.org/downloads/

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Instalar Chrome
- Baixe e instale o Google Chrome
- O ChromeDriver é gerenciado automaticamente

## 🚀 Como usar (Super simples!)

### Execução Principal
```bash
python main.py
```

### Teste rápido
```bash
python config/teste.py
```

### Teste pandas e Excel
```bash
python config/teste_pandas.py
```

## 📁 Estrutura do Projeto

```
scraper_integral_medica/
├── main.py                     # 🎯 ARQUIVO PRINCIPAL - Execute este!
├── requirements.txt            # 📦 Dependências
├── README.md                  # 📖 Este arquivo
├── config/                    # ⚙️ Configurações e scripts
│   ├── scraper_completo.py    #    Script principal do scraper
│   ├── scraper_nutricional.py #    Script original (sem Selenium)
│   ├── teste_scraper_completo.py #  Teste detalhado
│   ├── teste.py               #    Teste rápido
│   ├── teste_pandas.py        #    Teste pandas e Excel
│   └── test_page_structure.py #    Teste de estrutura da página
└── dados/                     # 📊 Dados coletados
    ├── csv/                   #    Arquivos CSV gerados
    │   └── produtos_nutricional_completo.csv
    ├── excel/                 #    Arquivos Excel (futuro)
    └── scraper_completo.log   #    Log de execução
```

## 🎮 Modo de Uso Interativo

Quando executar `python main.py`, você verá:

1. **Verificação de dependências** - Testa se tudo está instalado
2. **Confirmação** - Pergunta se você quer continuar
3. **Configurações** - Mostra as configurações automáticas
4. **Modo visual** - Pergunta se quer ver o navegador funcionando
5. **Execução** - Faz todo o trabalho automaticamente
6. **Resultados** - Mostra estatísticas e onde encontrar os dados

## 📊 Arquivos Gerados

Após a execução, você terá:

- **`dados/csv/produtos_nutricional_completo_YYYYMMDD_HHMMSS.csv`** - Planilha CSV com todos os dados
- **`dados/excel/produtos_nutricional_completo_YYYYMMDD_HHMMSS.xlsx`** - Planilha Excel formatada
- **`dados/scraper_completo.log`** - Log detalhado da execução

### 📈 **Tecnologias Utilizadas:**
- **pandas** - Manipulação e análise de dados
- **openpyxl** - Geração de arquivos Excel
- **Selenium** - Automação do navegador
- **BeautifulSoup** - Parsing de HTML

## ⚙️ Configurações Automáticas

O programa usa as seguintes configurações otimizadas:

- **8 cliques máximos** no botão "Ver mais produtos"
- **5 segundos** de espera entre cada clique
- **2 segundos** de delay entre produtos (para ser respeitoso)
- **Modo headless** por padrão (sem interface gráfica)

## 🐛 Solução de Problemas

### "Dependências não instaladas"
```bash
pip install -r requirements.txt
```

### "ChromeDriver não encontrado"
1. Certifique-se que o Chrome está instalado
2. Atualize o Chrome para a versão mais recente
3. Reinicie o terminal

### "Poucos produtos encontrados"
- Execute com modo visual (`python main.py` → responda 's' para ver navegador)
- Verifique sua conexão com a internet
- Tente executar em horários diferentes

### "Erro inesperado"
- Verifique o arquivo `dados/scraper_completo.log`
- Execute `python config/teste.py` para verificar se tudo está funcionando

## 📈 Exemplo de Execução

```bash
$ python main.py

============================================================
🚀 SCRAPER INTEGRAL MÉDICA - DADOS NUTRICIONAIS
============================================================

📋 Este programa irá:
   ✅ Acessar o site da Integral Médica
   ✅ Carregar TODOS os produtos (até 8 cliques)
   ✅ Coletar dados nutricionais de cada produto
   ✅ Salvar os dados em formato CSV

🤔 Deseja continuar? (s/n): s

⚙️  CONFIGURAÇÕES:
   🔧 Máximo de 8 cliques em 'Ver mais produtos'
   ⏱️  5 segundos entre cada clique
   🤖 Modo automático (sem interface gráfica)

🚀 Iniciando scraper...
⏳ Isso pode demorar alguns minutos... Por favor, aguarde!

[...processo automático...]

============================================================
✅ SCRAPING CONCLUÍDO COM SUCESSO!
============================================================
📦 Total de produtos processados: 150
📊 Produtos com dados nutricionais: 142
⏱️  Tempo de execução: 847.3 segundos
```

## 💡 Dicas para Leigos

1. **Primeira vez?** Execute `python config/teste.py` para verificar se tudo está funcionando
2. **Quer ver funcionando?** Use modo visual quando perguntado
3. **Demora muito?** É normal! O programa coleta dados de centenas de produtos
4. **Deu erro?** Verifique o arquivo `dados/scraper_completo.log`
5. **Planilha não abre?** Use Excel, LibreOffice ou Google Sheets

## 🤝 Contribuição

Este projeto é open source! Para contribuir:

1. Faça fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Abra um Pull Request

## 📄 Licença

Este projeto é apenas para fins educacionais e de pesquisa. Respeite os termos de uso do site da Integral Médica.

## ⚠️ Aviso Importante

- **Use responsavelmente** - Não abuse do site
- **Respeite os delays** - Não modifique os tempos de espera
- **Termos de uso** - Verifique os termos do site antes de usar
- **Dados pessoais** - Este scraper não coleta dados pessoais

---

## 🎉 Resumo para Pressa

**Para usar:**
1. `pip install -r requirements.txt`
2. `python main.py`
3. Aguarde e encontre os dados em `dados/csv/`

**Pronto!** 🚀

## 🧬 Scraper Integral Médica

## 📋 Descrição

Este projeto é um scraper automatizado para coletar dados nutricionais dos produtos da **Integral Médica**. O scraper navega pelo site, coleta URLs dos produtos e extrai informações nutricionais detalhadas, salvando os dados em formato CSV e Excel.

## 🚀 Funcionalidades

- **Coleta de URLs**: Navega pela página de produtos e coleta todos os links
- **Extração de dados nutricionais**: Extrai informações como calorias, proteínas, carboidratos, etc.
- **Salvamento múltiplo**: Salva em CSV e Excel automaticamente
- **Logs detalhados**: Registra todo o processo para monitoramento
- **Interface amigável**: Menu interativo para escolher ações
- **Compatibilidade multiplataforma**: Funciona em Windows, Linux e macOS

## 💻 Compatibilidade

### ✅ Sistemas Operacionais Suportados
- **Windows 10/11** (testado)
- **Linux** (testado no Arch Linux)
- **macOS** (compatível)

### 🔧 WebDriver Manager
O projeto usa **WebDriver Manager** para garantir compatibilidade:
- ✅ Baixa automaticamente o ChromeDriver correto
- ✅ Funciona com qualquer versão do Chrome
- ✅ Sem necessidade de configuração manual
- ✅ Atualização automática de drivers

## 📦 Instalação

### 🪟 Windows (Instalação Automática)

1. **Instalar Python 3.8+** (https://python.org/downloads/)
   - ⚠️ **IMPORTANTE**: Marcar "Add Python to PATH"

2. **Instalar Google Chrome** (https://google.com/chrome/)

3. **Duplo clique em**: `instalar_windows.bat`

### 🐧 Linux/macOS (Manual)

```bash
# Instalar dependências
pip install -r requirements.txt

# Testar ambiente
python teste_windows.py

# Executar scraper
python main.py
```

## 🎯 Uso

### Execução Principal
```bash
python main.py
```

### Opções Disponíveis
1. **Coletar apenas URLs** - Coleta todos os links dos produtos
2. **Coletar dados nutricionais completos** - URLs + dados nutricionais
3. **Testar produto específico** - Teste com um produto
4. **Cancelar** - Sair do programa

### Exemplo de Execução
```
🧬 SCRAPER INTEGRAL MÉDICA v2.0
═══════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════════

Escolha uma opção:
1. 🔗 Coletar apenas URLs dos produtos
2. 📊 Coletar dados nutricionais completos (URLs + Dados)
3. 🧪 Testar produto específico
4. ❌ Cancelar

Opção: 2

🚀 Iniciando coleta completa de dados...
⏳ Isso pode demorar alguns minutos... Por favor, aguarde!
```

## 📁 Estrutura de Arquivos

```
scraper_integral_medica/
├── main.py                      # Script principal
├── requirements.txt              # Dependências
├── INSTALACAO_WINDOWS.md        # Instruções Windows
├── instalar_windows.bat         # Instalador Windows
├── teste_windows.py             # Teste de ambiente
├── config/                      # Scripts especializados
│   ├── scraper_completo_integrado.py
│   ├── coletar_urls.py
│   └── scraper_completo.py
├── dados/                       # Dados coletados
│   ├── csv/
│   │   └── dados.csv
│   └── excel/
│       └── dados.xlsx
└── logs/                        # Arquivos de log
    ├── scraper_integrado.log
    └── coleta_urls.log
```

## 🔍 Dados Coletados

### Campos Extraídos
- **URL**: Link do produto
- **NOME_PRODUTO**: Nome do produto
- **PORÇÃO (g)**: Tamanho da porção
- **CALORIAS (kcal)**: Valor energético
- **CARBOIDRATOS (g)**: Quantidade de carboidratos
- **PROTEÍNAS (g)**: Quantidade de proteínas
- **GORDURAS_TOTAIS (g)**: Gorduras totais
- **GORDURAS_SATURADAS (g)**: Gorduras saturadas
- **FIBRAS (g)**: Fibras alimentares
- **AÇÚCARES (g)**: Açúcares
- **SÓDIO (mg)**: Teor de sódio

### Formato dos Arquivos
- **CSV**: `dados/csv/dados.csv`
- **Excel**: `dados/excel/dados.xlsx`

## 📊 Exemplo de Saída

```csv
URL,NOME_PRODUTO,PORÇÃO (g),CALORIAS (kcal),CARBOIDRATOS (g),PROTEÍNAS (g)
https://...,Whey Protein,30,120,2,25
https://...,BCAA,10,0,0,10
```

## 🛠️ Requisitos Técnicos

### Dependências Python
- `requests==2.31.0` - Requisições HTTP
- `beautifulsoup4==4.12.2` - Parsing HTML
- `selenium==4.15.2` - Automação web
- `pandas==2.1.4` - Manipulação de dados
- `webdriver-manager==4.0.1` - Gerenciamento de drivers
- `lxml==4.9.3` - Parser XML/HTML
- `openpyxl==3.1.2` - Manipulação Excel

### Requisitos do Sistema
- **Python 3.8+**
- **Google Chrome** (qualquer versão)
- **Conexão com internet**

## 🧪 Testes

### Teste de Ambiente
```bash
python teste_windows.py
```

Este script verifica:
- ✅ Versão do Python
- ✅ Dependências instaladas
- ✅ Chrome instalado
- ✅ WebDriver funcionando
- ✅ Criação de pastas

### Teste de Produto Específico
Use a opção 3 no menu principal para testar um produto específico.

## 🔧 Solução de Problemas

### Windows
- **"python não é reconhecido"**: Reinstalar Python marcando "Add to PATH"
- **"pip não é reconhecido"**: Usar `python -m pip install -r requirements.txt`
- **Erro de ChromeDriver**: O WebDriver Manager resolve automaticamente

### Linux/macOS
- **Permissões**: `chmod +x *.py`
- **Chrome não encontrado**: Instalar Google Chrome
- **Dependências**: `pip3 install -r requirements.txt`

## 📝 Logs

O sistema gera logs detalhados em:
- `logs/scraper_integrado.log` - Coleta completa
- `logs/coleta_urls.log` - Apenas URLs

### Exemplo de Log
```
2024-01-15 10:30:15 - INFO - ✅ WebDriver configurado com WebDriver Manager
2024-01-15 10:30:20 - INFO - 🔍 Iniciando coleta de URLs...
2024-01-15 10:30:25 - INFO - 🎯 Botão "Mostrar mais" encontrado
2024-01-15 10:30:30 - INFO - 📊 150 dados nutricionais coletados
```

## 🎉 Principais Melhorias

### v2.0 - Compatibilidade Windows
- ✅ WebDriver Manager para compatibilidade automática
- ✅ Script de instalação automática Windows
- ✅ Teste de ambiente completo
- ✅ Instruções detalhadas para Windows

### v1.0 - Funcionalidades Base
- ✅ Coleta de URLs e dados nutricionais
- ✅ Salvamento em CSV e Excel
- ✅ Sistema de logs
- ✅ Menu interativo

## 🤝 Suporte

Para problemas ou dúvidas:
1. Execute `python teste_windows.py` para diagnóstico
2. Verifique os logs em `logs/`
3. Forneça informações do sistema:
   - Versão do Python: `python --version`
   - Versão do Chrome: Chrome > Ajuda > Sobre
   - Sistema operacional
   - Mensagem de erro completa

## 📄 Licença

Este projeto é para fins educacionais e de pesquisa. Respeite os termos de uso do site da Integral Médica.

---

**Desenvolvido com ❤️ para facilitar a coleta de dados nutricionais**
