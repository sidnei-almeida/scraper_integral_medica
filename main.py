#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 SCRAPER INTEGRAL MÉDICA - Interface Profissional
==================================================
Script avançado para coleta de dados nutricionais da Integral Médica

FUNCIONALIDADES:
1. Coleta automatizada de URLs de produtos
2. Extração completa de dados nutricionais  
3. Testes individuais de produtos
4. Geração de relatórios em CSV e Excel
"""

import os
import sys
import time
import glob
from datetime import datetime
from typing import List, Dict, Optional

# Adicionar pasta config ao path para importar scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))

# ============================================================================
# 🎨 SISTEMA DE CORES ANSI PARA TERMINAL
# ============================================================================
class Cores:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    VERDE = '\033[92m'
    AZUL = '\033[94m'
    AMARELO = '\033[93m'
    VERMELHO = '\033[91m'
    CIANO = '\033[96m'
    MAGENTA = '\033[95m'
    BRANCO = '\033[97m'

# ============================================================================
# 🛠️ FUNÇÕES UTILITÁRIAS
# ============================================================================
def limpar_terminal():
    """Limpa o terminal"""
    os.system('clear' if os.name == 'posix' else 'cls')

def mostrar_banner():
    """Exibe o banner principal do programa"""
    banner = f"""
{Cores.CIANO}{Cores.BOLD}
╔══════════════════════════════════════════════════════════════╗
║                🚀 SCRAPER INTEGRAL MÉDICA                    ║
║                                                              ║
║              Coleta Automatizada de Dados v2.0              ║
║                                                              ║
║  📊 Extração de Dados Nutricionais                          ║
║  🎯 Coleta de URLs de Produtos                              ║
║  📝 Geração de Relatórios CSV/Excel                         ║
╚══════════════════════════════════════════════════════════════╝
{Cores.RESET}"""
    print(banner)

def mostrar_barra_progresso(texto: str, duracao: float = 2.0):
    """Exibe uma barra de progresso animada"""
    print(f"\n{Cores.AMARELO}⏳ {texto}...{Cores.RESET}")
    barra_tamanho = 40
    for i in range(barra_tamanho + 1):
        progresso = i / barra_tamanho
        barra = "█" * i + "░" * (barra_tamanho - i)
        porcentagem = int(progresso * 100)
        print(f"\r{Cores.VERDE}[{barra}] {porcentagem}%{Cores.RESET}", end="", flush=True)
        time.sleep(duracao / barra_tamanho)
    print()

def mostrar_menu():
    """Exibe o menu principal"""
    menu = f"""
{Cores.AZUL}{Cores.BOLD}═══════════════════ MENU PRINCIPAL ═══════════════════{Cores.RESET}

{Cores.VERDE}🚀 OPERAÇÕES PRINCIPAIS:{Cores.RESET}
  {Cores.AMARELO}1.{Cores.RESET} 🔗 {Cores.BRANCO}Coletar URLs{Cores.RESET} - Extrai URLs de todos os produtos
  {Cores.AMARELO}2.{Cores.RESET} 📊 {Cores.BRANCO}Coleta Completa{Cores.RESET} - URLs + Dados nutricionais
  {Cores.AMARELO}3.{Cores.RESET} 🧪 {Cores.BRANCO}Teste Individual{Cores.RESET} - Testa um produto específico

{Cores.VERDE}📁 GERENCIAR DADOS:{Cores.RESET}
  {Cores.AMARELO}4.{Cores.RESET} 📋 {Cores.BRANCO}Ver Arquivos{Cores.RESET} - Lista arquivos gerados
  {Cores.AMARELO}5.{Cores.RESET} 🗑️  {Cores.BRANCO}Limpar Dados{Cores.RESET} - Remove arquivos antigos

{Cores.VERDE}ℹ️  INFORMAÇÕES:{Cores.RESET}
  {Cores.AMARELO}6.{Cores.RESET} 📖 {Cores.BRANCO}Sobre o Programa{Cores.RESET} - Informações e estatísticas
  {Cores.AMARELO}7.{Cores.RESET} ❌ {Cores.BRANCO}Sair{Cores.RESET} - Encerrar programa

{Cores.AZUL}══════════════════════════════════════════════════════{Cores.RESET}
"""
    print(menu)

def obter_escolha() -> str:
    """Obtém a escolha do usuário"""
    try:
        escolha = input(f"{Cores.MAGENTA}👉 Digite sua opção (1-7): {Cores.RESET}").strip()
        return escolha
    except KeyboardInterrupt:
        print(f"\n\n{Cores.AMARELO}⚠️  Programa interrompido pelo usuário{Cores.RESET}")
        sys.exit(0)

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    print(f"\n{Cores.CIANO}🔧 Verificando dependências...{Cores.RESET}")
    dependencias_faltando = []
    
    dependencias = {
        'requests': 'requests',
        'selenium': 'selenium', 
        'beautifulsoup4': 'bs4'
    }
    
    for nome_pacote, modulo in dependencias.items():
        try:
            if modulo == 'bs4':
                from bs4 import BeautifulSoup
            else:
                __import__(modulo)
            print(f"   ✅ {nome_pacote}")
        except ImportError:
            dependencias_faltando.append(nome_pacote)
            print(f"   ❌ {nome_pacote}")
    
    if dependencias_faltando:
        print(f"\n{Cores.VERMELHO}❌ ERRO: Dependências não instaladas!{Cores.RESET}")
        print(f"{Cores.AMARELO}🔧 Execute: pip install {' '.join(dependencias_faltando)}{Cores.RESET}")
        print(f"{Cores.AMARELO}💡 Ou execute: pip install -r requirements.txt{Cores.RESET}")
        return False
    
    print(f"{Cores.VERDE}✅ Todas as dependências estão instaladas!{Cores.RESET}")
    return True

# ============================================================================
# 🎯 FUNÇÕES ESPECÍFICAS DO SCRAPER
# ============================================================================

def executar_coleta_urls():
    """Executa apenas a coleta de URLs"""
    print(f"\n{Cores.CIANO}{Cores.BOLD}🔗 COLETANDO URLs DOS PRODUTOS{Cores.RESET}")
    print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
    
    print(f"\n{Cores.VERDE}✅ Configurações:{Cores.RESET}")
    print(f"   📊 Site: {Cores.AMARELO}Integral Médica{Cores.RESET}")
    print(f"   🔄 Carregamento: {Cores.AMARELO}Automático (até 8 cliques 'Ver mais'){Cores.RESET}")
    print(f"   📁 Saída: {Cores.AMARELO}dados/{Cores.RESET}")
    
    # Perguntar sobre modo visual
    print(f"\n{Cores.MAGENTA}🖥️  Deseja ver o navegador funcionando? (s/N): {Cores.RESET}", end="")
    resposta_visual = input().strip().lower()
    headless = resposta_visual not in ['s', 'sim', 'y', 'yes']
    
    if headless:
        print(f"{Cores.AZUL}🤖 Modo headless ativado (sem interface gráfica){Cores.RESET}")
    else:
        print(f"{Cores.AZUL}🖥️  Modo visual ativado (você verá o navegador){Cores.RESET}")
    
    confirmar = input(f"\n{Cores.MAGENTA}🤔 Continuar com a coleta? (s/N): {Cores.RESET}").lower()
    
    if confirmar in ['s', 'sim', 'y', 'yes']:
        try:
            mostrar_barra_progresso("Inicializando navegador", 1.0)
            
            # Importar e executar coletor de URLs
            from coletar_urls import URLCollector
            
            print(f"{Cores.VERDE}🚀 Iniciando coleta de URLs...{Cores.RESET}")
            inicio = time.time()
            
            # Criar coletor
            collector = URLCollector(headless=headless)
            
            # Executar coleta
            urls = collector.run()
            
            # Calcular tempo
            fim = time.time()
            tempo_execucao = fim - inicio
            
            if urls:
                print(f"\n{Cores.VERDE}✅ Sucesso! {len(urls)} URLs coletadas{Cores.RESET}")
                print(f"{Cores.AZUL}⏱️  Tempo de execução: {tempo_execucao:.1f} segundos{Cores.RESET}")
                
                # Mostrar algumas URLs
                print(f"\n{Cores.CIANO}🔍 Primeiras 5 URLs coletadas:{Cores.RESET}")
                for i, url in enumerate(urls[:5]):
                    print(f"   {Cores.AMARELO}{i+1}.{Cores.RESET} {url}")
                
                if len(urls) > 5:
                    print(f"   {Cores.AZUL}... e mais {len(urls) - 5} URLs{Cores.RESET}")
                
                print(f"\n{Cores.VERDE}📁 URLs salvas na pasta: dados/{Cores.RESET}")
            else:
                print(f"\n{Cores.VERMELHO}❌ Nenhuma URL foi coletada.{Cores.RESET}")
                
        except KeyboardInterrupt:
            print(f"\n{Cores.AMARELO}⚠️  Operação interrompida pelo usuário.{Cores.RESET}")
        except Exception as e:
            print(f"\n{Cores.VERMELHO}❌ Erro inesperado: {e}{Cores.RESET}")
    else:
        print(f"{Cores.AMARELO}⏭️  Operação cancelada{Cores.RESET}")

def executar_coleta_completa():
    """Executa a coleta completa de dados nutricionais"""
    print(f"\n{Cores.CIANO}{Cores.BOLD}📊 COLETA COMPLETA DE DADOS NUTRICIONAIS{Cores.RESET}")
    print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
    
    print(f"\n{Cores.VERDE}✅ Este processo irá:{Cores.RESET}")
    print(f"   🔗 Coletar URLs de todos os produtos")
    print(f"   📊 Extrair dados nutricionais de cada produto")
    print(f"   💾 Salvar em CSV e Excel")
    print(f"   📋 Gerar logs detalhados")
    
    print(f"\n{Cores.AMARELO}⚠️  ATENÇÃO:{Cores.RESET}")
    print(f"   • Esta operação pode demorar {Cores.VERMELHO}vários minutos{Cores.RESET}")
    print(f"   • Serão processados {Cores.VERMELHO}centenas de produtos{Cores.RESET}")
    print(f"   • Recomendado para uso noturno ou em horários livres")
    
    print(f"\n{Cores.VERDE}📁 Arquivos de saída:{Cores.RESET}")
    print(f"   📄 dados/csv/dados.csv")
    print(f"   📊 dados/excel/dados.xlsx")
    print(f"   📋 logs/scraper_completo.log")
    
    confirmar = input(f"\n{Cores.MAGENTA}🤔 Continuar com a coleta completa? (s/N): {Cores.RESET}").lower()
    
    if confirmar in ['s', 'sim', 'y', 'yes']:
        try:
            mostrar_barra_progresso("Preparando coleta completa", 1.5)
            
            # Importar e executar scraper completo
            from scraper_completo_integrado import main as scraper_main
            
            print(f"{Cores.VERDE}🚀 Iniciando coleta completa...{Cores.RESET}")
            inicio = time.time()
            
            # Executar scraper
            scraper_main()
            
            fim = time.time()
            tempo_execucao = fim - inicio
            
            print(f"\n{Cores.VERDE}✅ Coleta completa finalizada!{Cores.RESET}")
            print(f"{Cores.AZUL}⏱️  Tempo total: {tempo_execucao:.1f} segundos{Cores.RESET}")
            
        except KeyboardInterrupt:
            print(f"\n{Cores.AMARELO}⚠️  Operação interrompida pelo usuário.{Cores.RESET}")
        except Exception as e:
            print(f"\n{Cores.VERMELHO}❌ Erro: {e}{Cores.RESET}")
    else:
        print(f"{Cores.AMARELO}⏭️  Operação cancelada{Cores.RESET}")

def executar_teste_produto():
    """Executa teste em um produto específico"""
    print(f"\n{Cores.CIANO}{Cores.BOLD}🧪 TESTE DE PRODUTO ESPECÍFICO{Cores.RESET}")
    print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
    
    try:
        print(f"\n{Cores.VERDE}📋 Insira a URL completa do produto para teste:{Cores.RESET}")
        print(f"{Cores.AZUL}Exemplo: https://www.integralmedica.com.br/produto/whey-protein{Cores.RESET}")
        
        url = input(f"\n{Cores.MAGENTA}🔗 URL do produto: {Cores.RESET}").strip()
        
        if not url:
            print(f"{Cores.VERMELHO}❌ URL obrigatória!{Cores.RESET}")
            return
        
        if "integralmedica.com.br" not in url:
            print(f"{Cores.VERMELHO}❌ URL deve ser da Integral Médica!{Cores.RESET}")
            return
            
        print(f"\n{Cores.VERDE}✅ Testando produto: {Cores.AMARELO}{url}{Cores.RESET}")
        
        mostrar_barra_progresso("Executando teste", 1.0)
        
        # Importar e executar teste
        from teste_nutricional import testar_produto_especifico
        
        resultado = testar_produto_especifico(url)
        
        if resultado:
            print(f"{Cores.VERDE}✅ Teste concluído com sucesso!{Cores.RESET}")
            print(f"{Cores.AZUL}📄 Dados salvos em: teste_produto.json{Cores.RESET}")
        else:
            print(f"{Cores.VERMELHO}❌ Falha no teste do produto{Cores.RESET}")
        
    except Exception as e:
        print(f"\n{Cores.VERMELHO}❌ Erro: {e}{Cores.RESET}")

def listar_arquivos_gerados():
    """Lista arquivos gerados pelo programa"""
    print(f"\n{Cores.CIANO}{Cores.BOLD}📋 ARQUIVOS GERADOS{Cores.RESET}")
    print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
    
    pastas_dados = ["dados", "logs"]
    extensoes = ["*.csv", "*.xlsx", "*.json", "*.log", "*.txt"]
    
    total_arquivos = 0
    
    for pasta in pastas_dados:
        if not os.path.exists(pasta):
            print(f"{Cores.AMARELO}📁 Pasta '{pasta}' não encontrada{Cores.RESET}")
            continue
            
        print(f"\n{Cores.VERDE}📂 Pasta: {pasta}/{Cores.RESET}")
        
        arquivos_pasta = []
        for ext in extensoes:
            arquivos_pasta.extend(glob.glob(f"{pasta}/**/{ext}", recursive=True))
        
        if not arquivos_pasta:
            print(f"   {Cores.AMARELO}📄 Nenhum arquivo encontrado{Cores.RESET}")
            continue
        
        for i, arquivo in enumerate(sorted(arquivos_pasta, reverse=True), 1):
            nome_arquivo = os.path.basename(arquivo)
            tamanho = os.path.getsize(arquivo)
            data_modificacao = datetime.fromtimestamp(os.path.getmtime(arquivo))
            
            # Calcula o tamanho em formato legível
            if tamanho < 1024:
                tamanho_str = f"{tamanho} B"
            elif tamanho < 1024 * 1024:
                tamanho_str = f"{tamanho / 1024:.1f} KB"
            else:
                tamanho_str = f"{tamanho / (1024 * 1024):.1f} MB"
            
            print(f"   {Cores.AMARELO}{i:2d}.{Cores.RESET} {Cores.BRANCO}{nome_arquivo}{Cores.RESET}")
            print(f"      📅 {data_modificacao.strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"      📏 {tamanho_str}")
            
            total_arquivos += 1
    
    print(f"\n{Cores.VERDE}📊 Total de arquivos encontrados: {total_arquivos}{Cores.RESET}")

def limpar_dados_antigos():
    """Remove arquivos antigos"""
    print(f"\n{Cores.CIANO}{Cores.BOLD}🗑️  LIMPAR DADOS ANTIGOS{Cores.RESET}")
    print(f"{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}")
    
    pastas_dados = ["dados", "logs"]
    extensoes = ["*.csv", "*.xlsx", "*.json", "*.log", "*.txt"]
    
    arquivos_para_remover = []
    
    for pasta in pastas_dados:
        if os.path.exists(pasta):
            for ext in extensoes:
                arquivos_para_remover.extend(glob.glob(f"{pasta}/**/{ext}", recursive=True))
    
    if not arquivos_para_remover:
        print(f"{Cores.VERDE}✅ Nenhum arquivo para limpar{Cores.RESET}")
        return
    
    print(f"\n{Cores.AMARELO}⚠️  ATENÇÃO:{Cores.RESET}")
    print(f"   • Serão removidos {Cores.VERMELHO}{len(arquivos_para_remover)} arquivos{Cores.RESET}")
    print(f"   • Esta ação {Cores.VERMELHO}NÃO PODE ser desfeita{Cores.RESET}")
    print(f"   • Inclui: CSV, Excel, JSON, Logs e arquivos de texto")
    
    confirmar = input(f"\n{Cores.MAGENTA}🤔 Tem certeza? Digite 'CONFIRMAR' para prosseguir: {Cores.RESET}")
    
    if confirmar == "CONFIRMAR":
        try:
            for arquivo in arquivos_para_remover:
                os.remove(arquivo)
            print(f"\n{Cores.VERDE}✅ {len(arquivos_para_remover)} arquivos removidos com sucesso!{Cores.RESET}")
        except Exception as e:
            print(f"\n{Cores.VERMELHO}❌ Erro ao remover arquivos: {e}{Cores.RESET}")
    else:
        print(f"{Cores.AMARELO}⏭️  Operação cancelada{Cores.RESET}")

def mostrar_sobre():
    """Exibe informações sobre o programa"""
    sobre = f"""
{Cores.CIANO}{Cores.BOLD}📖 SOBRE O SCRAPER INTEGRAL MÉDICA{Cores.RESET}
{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}

{Cores.VERDE}🎯 OBJETIVO:{Cores.RESET}
   Automatizar a coleta de dados nutricionais de todos os produtos
   disponíveis no site da Integral Médica, gerando relatórios
   estruturados para análise e pesquisa.

{Cores.VERDE}📊 FUNCIONALIDADES:{Cores.RESET}
   • Coleta automatizada de URLs de produtos
   • Extração de dados nutricionais completos
   • Testes individuais para debugging
   • Geração de relatórios CSV e Excel
   • Sistema de logs detalhado

{Cores.VERDE}🛠️  TECNOLOGIAS:{Cores.RESET}
   • Python 3.8+
   • Selenium WebDriver
   • BeautifulSoup4
   • Requests
   • Pandas

{Cores.VERDE}📂 ARQUIVOS GERADOS:{Cores.RESET}
   • Formato: CSV, Excel, JSON
   • Localização: dados/, logs/
   • Nomenclatura: dados.csv, dados.xlsx

{Cores.VERDE}📋 DADOS COLETADOS:{Cores.RESET}
   • URL do produto
   • Porção recomendada
   • Calorias
   • Carboidratos
   • Proteínas
   • Gorduras totais e saturadas
   • Fibras alimentares
   • Açúcares
   • Sódio

{Cores.VERDE}⚡ CARACTERÍSTICAS:{Cores.RESET}
   • Carregamento automático de produtos (até 8 cliques)
   • Tratamento de erros robusto
   • Interface visual profissional
   • Modo headless para execução em background
   • Sistema de progresso em tempo real

{Cores.VERDE}📝 DESENVOLVIDO POR:{Cores.RESET}
   • Sistema de Web Scraping Avançado
   • Versão: 2.0
   • Data: {datetime.now().strftime('%B %Y')}

{Cores.AZUL}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Cores.RESET}
"""
    print(sobre)

def pausar():
    """Pausa o programa aguardando input do usuário"""
    input(f"\n{Cores.CIANO}⏯️  Pressione Enter para continuar...{Cores.RESET}")

# ============================================================================
# 🚀 FUNÇÃO PRINCIPAL
# ============================================================================
def main():
    """Função principal do programa"""
    try:
        while True:
            limpar_terminal()
            mostrar_banner()
            
            # Verificar dependências na primeira execução
            if not verificar_dependencias():
                print(f"\n{Cores.AMARELO}💡 Instale as dependências e execute novamente{Cores.RESET}")
                print(f"{Cores.AZUL}🧪 Para teste rápido: python config/teste.py{Cores.RESET}")
                pausar()
                continue
            
            mostrar_menu()
            
            escolha = obter_escolha()
            
            if escolha == "1":
                executar_coleta_urls()
                pausar()
                
            elif escolha == "2":
                executar_coleta_completa()
                pausar()
                
            elif escolha == "3":
                executar_teste_produto()
                pausar()
                
            elif escolha == "4":
                listar_arquivos_gerados()
                pausar()
                
            elif escolha == "5":
                limpar_dados_antigos()
                pausar()
                
            elif escolha == "6":
                mostrar_sobre()
                pausar()
                
            elif escolha == "7":
                print(f"\n{Cores.VERDE}👋 Obrigado por usar o Scraper Integral Médica!{Cores.RESET}")
                print(f"{Cores.CIANO}🚀 Até a próxima!{Cores.RESET}\n")
                break
                
            else:
                print(f"\n{Cores.VERMELHO}❌ Opção inválida! Por favor, escolha entre 1-7{Cores.RESET}")
                time.sleep(2)
                
    except KeyboardInterrupt:
        print(f"\n\n{Cores.AMARELO}👋 Programa encerrado pelo usuário. Até logo!{Cores.RESET}\n")
    except Exception as e:
        print(f"\n{Cores.VERMELHO}❌ Erro inesperado: {e}{Cores.RESET}")

if __name__ == "__main__":
    main() 