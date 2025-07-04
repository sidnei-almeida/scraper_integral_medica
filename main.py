#!/usr/bin/env python3
"""
🚀 SCRAPER INTEGRAL MÉDICA - SCRIPT PRINCIPAL
============================================

Este é o script principal para coletar dados nutricionais de todos os produtos
da Integral Médica. Simplesmente execute este arquivo para começar!

Como usar:
    python main.py

Os dados serão salvos em:
    - dados/csv/produtos_nutricional_completo.csv
    - logs/scraper_completo.log (arquivo de log)

Campos coletados:
    - URL, PORÇÃO, CALORIAS, CARBOIDRATOS, PROTEÍNAS, GORDURAS_TOTAIS,
      GORDURAS_SATURADAS, FIBRAS, AÇÚCARES, SÓDIO
"""

import sys
import os
import time
from datetime import datetime

# Adicionar pasta config ao path para importar scripts
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))

def print_header():
    """Imprime cabeçalho do programa"""
    print("=" * 60)
    print("🚀 SCRAPER INTEGRAL MÉDICA - DADOS NUTRICIONAIS")
    print("=" * 60)
    print()
    print("📋 Este programa irá:")
    print("   ✅ Acessar o site da Integral Médica")
    print("   ✅ Carregar TODOS os produtos (até 8 cliques)")
    print("   ✅ Coletar dados nutricionais de cada produto")
    print("   ✅ Salvar os dados em formato CSV")
    print()
    print("📁 Arquivos de saída:")
    print("   📄 dados/csv/produtos_nutricional_completo.csv")
    print("   📋 logs/scraper_completo.log")
    print()

def print_footer(total_produtos, produtos_com_dados, tempo_execucao):
    """Imprime resumo final"""
    print("\n" + "=" * 60)
    print("✅ SCRAPING CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print(f"📦 Total de produtos processados: {total_produtos}")
    print(f"📊 Produtos com dados nutricionais: {produtos_com_dados}")
    print(f"⏱️  Tempo de execução: {tempo_execucao:.1f} segundos")
    print()
    print("📁 Verifique os arquivos gerados:")
    print("   📄 dados/csv/produtos_nutricional_completo.csv")
    print("   📋 logs/scraper_completo.log")
    print()
    print("🎉 Processo finalizado!")
    print("=" * 60)

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    dependencias_faltando = []
    
    try:
        import requests
    except ImportError:
        dependencias_faltando.append("requests")
    
    try:
        import selenium
    except ImportError:
        dependencias_faltando.append("selenium")
    
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        dependencias_faltando.append("beautifulsoup4")
    
    if dependencias_faltando:
        print("❌ ERRO: Dependências não instaladas!")
        print(f"🔧 Execute: pip install {' '.join(dependencias_faltando)}")
        print("💡 Ou execute: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Função principal"""
    print_header()
    
    # Verificar dependências
    if not verificar_dependencias():
        print("💡 Você pode executar o teste rápido com: python config/teste.py")
        sys.exit(1)
    
    # Opções para o usuário
    print("🔧 OPÇÕES DISPONÍVEIS:")
    print("   1️⃣  Coletar apenas URLs dos produtos")
    print("   2️⃣  Coletar dados nutricionais completos (URLs + Dados)")
    print("   3️⃣  Testar um produto específico")
    print("   4️⃣  Cancelar")
    print()
    
    while True:
        print("🤔 Escolha uma opção (1, 2, 3 ou 4): ", end="")
        opcao = input().strip()
        
        if opcao == "1":
            executar_coleta_urls()
            break
        elif opcao == "2":
            executar_coleta_completa()
            break
        elif opcao == "3":
            executar_teste_produto()
            break
        elif opcao == "4":
            print("❌ Operação cancelada pelo usuário.")
            print("💡 Para testar se tudo está funcionando: python config/teste.py")
            sys.exit(0)
        else:
            print("❌ Opção inválida! Digite 1, 2, 3 ou 4.")

def executar_coleta_urls():
    """Executa apenas a coleta de URLs"""
    print("\n🔍 COLETA DE URLs")
    print("=" * 40)
    print("📋 Esta opção irá:")
    print("   ✅ Acessar o site da Integral Médica")
    print("   ✅ Carregar todos os produtos clicando 'Ver mais produtos'")
    print("   ✅ Coletar apenas as URLs dos produtos")
    print("   ✅ Salvar as URLs em arquivo texto")
    print()
    
    # Perguntar se quer ver o navegador funcionando
    print("🖥️  Deseja ver o navegador funcionando? (s/n): ", end="")
    resposta_visual = input().strip().lower()
    headless = resposta_visual not in ['s', 'sim', 'y', 'yes']
    
    if headless:
        print("🤖 Modo headless ativado (sem interface gráfica)")
    else:
        print("🖥️  Modo visual ativado (você verá o navegador)")
    
    print("\n🚀 Iniciando coleta de URLs...")
    inicio = time.time()
    
    try:
        # Importar e executar coletor de URLs
        from coletar_urls import URLCollector
        
        # Criar coletor
        collector = URLCollector(headless=headless)
        
        # Executar coleta
        urls = collector.run()
        
        # Calcular tempo
        fim = time.time()
        tempo_execucao = fim - inicio
        
        if urls:
            print(f"\n✅ Sucesso! {len(urls)} URLs coletadas")
            print(f"⏱️  Tempo de execução: {tempo_execucao:.1f} segundos")
            
            # Mostrar algumas URLs
            print("\n🔍 Primeiras 5 URLs coletadas:")
            for i, url in enumerate(urls[:5]):
                print(f"   {i+1}. {url}")
            
            if len(urls) > 5:
                print(f"   ... e mais {len(urls) - 5} URLs")
            
            print(f"\n📁 URLs salvas em: dados/")
        else:
            print("\n❌ Nenhuma URL foi coletada.")
            
    except KeyboardInterrupt:
        print("\n⚠️  Operação interrompida pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1)

def executar_coleta_completa():
    """Executa a coleta completa de dados nutricionais usando o script integrado"""
    print("\n📊 COLETA COMPLETA DE DADOS NUTRICIONAIS")
    print("=" * 50)
    print("📋 Esta opção irá:")
    print("   ✅ Coletar URLs de todos os produtos")
    print("   ✅ Extrair dados nutricionais de cada produto")
    print("   ✅ Salvar dados em CSV e XLSX")
    print("   📄 Arquivo CSV: dados/csv/dados.csv")
    print("   📊 Arquivo XLSX: dados/excel/dados.xlsx")
    print()
    
    # Perguntar ao usuário se deseja continuar
    print("🤔 Deseja continuar? (s/n): ", end="")
    resposta = input().strip().lower()
    
    if resposta not in ['s', 'sim', 'y', 'yes']:
        print("❌ Operação cancelada pelo usuário.")
        print("💡 Para testar se tudo está funcionando: python config/teste.py")
        sys.exit(0)
    
    # Perguntar se quer ver o navegador funcionando
    print("🖥️  Deseja ver o navegador funcionando? (s/n): ", end="")
    resposta_visual = input().strip().lower()
    headless = resposta_visual not in ['s', 'sim', 'y', 'yes']
    
    if headless:
        print("🤖 Modo headless ativado (sem interface gráfica)")
    else:
        print("🖥️  Modo visual ativado (você verá o navegador)")
    
    print("\n🚀 Iniciando scraper integrado...")
    print("⏳ Isso pode demorar alguns minutos... Por favor, aguarde!")
    
    # Registrar tempo de início
    inicio = time.time()
    
    try:
        # Importar e executar scraper integrado
        from scraper_completo_integrado import IntegratedScraper
        
        # Criar scraper
        scraper = IntegratedScraper(headless=headless)
        
        # Executar coleta
        dados = scraper.run()
        
        # Calcular estatísticas
        fim = time.time()
        tempo_execucao = fim - inicio
        
        if dados:
            total_produtos = len(dados)
            produtos_com_dados = sum(1 for produto in dados 
                                   if any(produto[field] != '0' for field in scraper.target_fields[2:]))
            
            print_footer(total_produtos, produtos_com_dados, tempo_execucao)
            
            # Mostrar exemplo de dados
            print("\n📋 EXEMPLO DOS DADOS COLETADOS:")
            print("-" * 40)
            for i, produto in enumerate(dados[:3]):
                print(f"\n{i+1}. {produto['NOME_PRODUTO']}")
                print(f"   URL: {produto['URL']}")
                for field in scraper.target_fields[2:]:
                    if produto[field] != '0':
                        print(f"   {field}: {produto[field]}")
            
            if len(dados) > 3:
                print(f"\n... e mais {len(dados) - 3} produtos!")
        else:
            print("\n❌ Nenhum dado foi coletado.")
            print("🔍 Verifique o arquivo de log para mais detalhes:")
            print("   📋 logs/scraper_integrado.log")
            
    except KeyboardInterrupt:
        print("\n⚠️  Operação interrompida pelo usuário.")
        print("🔄 Você pode executar novamente quando quiser.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        print("🔍 Verifique o arquivo de log para mais detalhes:")
        print("   📋 logs/scraper_integrado.log")
        sys.exit(1)

def executar_teste_produto():
    """Executa teste em um produto específico"""
    print("\n🧪 TESTE DE PRODUTO ESPECÍFICO")
    print("=" * 40)
    print("📋 Esta opção irá:")
    print("   ✅ Testar extração de dados de um produto específico")
    print("   ✅ Mostrar dados coletados na tela")
    print("   ✅ Salvar resultado em teste_produto.json")
    print()
    
    # Solicitar URL do produto
    print("🔗 Digite a URL do produto para testar:")
    print("   Exemplo: https://www.integralmedica.com.br/whey-protein-concentrado-pouch-900g/p")
    print()
    url_produto = input("URL: ").strip()
    
    if not url_produto:
        print("❌ URL não fornecida. Usando URL padrão para teste.")
        url_produto = "https://www.integralmedica.com.br/whey-protein-concentrado-pouch-900g/p"
    
    print(f"\n🔍 Testando produto: {url_produto}")
    
    try:
        # Importar e executar teste
        from teste_nutricional import NutritionalDataExtractor
        
        # Criar extrator
        extractor = NutritionalDataExtractor()
        
        # Extrair dados
        product_data = extractor.extract_all_data(url_produto)
        
        # Mostrar resultados
        extractor.print_results(product_data)
        
        print(f"\n💾 Dados salvos em: teste_produto.json")
        
    except KeyboardInterrupt:
        print("\n⚠️  Teste interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
        print("💡 Verifique se a URL está correta e tente novamente.")
        sys.exit(1)

if __name__ == "__main__":
    main() 