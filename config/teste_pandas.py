#!/usr/bin/env python3
"""
Teste específico para pandas e Excel
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Adicionar pasta config ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

def teste_pandas_excel():
    """Testa criação de DataFrame e exportação em CSV e Excel"""
    
    print("🧪 Testando funcionalidades do pandas e Excel...")
    
    try:
        # Dados de exemplo
        dados_exemplo = [
            {
                'URL': 'https://exemplo.com/produto1',
                'PORÇÃO (g)': '30',
                'CALORIAS (kcal)': '120',
                'CARBOIDRATOS (g)': '5',
                'PROTEÍNAS (g)': '25',
                'GORDURAS_TOTAIS (g)': '2',
                'GORDURAS_SATURADAS (g)': '1',
                'FIBRAS (g)': '0',
                'AÇÚCARES (g)': '3',
                'SÓDIO (mg)': '80'
            },
            {
                'URL': 'https://exemplo.com/produto2',
                'PORÇÃO (g)': '25',
                'CALORIAS (kcal)': '100',
                'CARBOIDRATOS (g)': '3',
                'PROTEÍNAS (g)': '20',
                'GORDURAS_TOTAIS (g)': '1',
                'GORDURAS_SATURADAS (g)': '0',
                'FIBRAS (g)': '1',
                'AÇÚCARES (g)': '2',
                'SÓDIO (mg)': '60'
            }
        ]
        
        # Criar DataFrame
        df = pd.DataFrame(dados_exemplo)
        print("✅ DataFrame criado com sucesso")
        print(f"   - {len(df)} linhas")
        print(f"   - {len(df.columns)} colunas")
        
        # Preparar pastas
        dados_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dados')
        csv_dir = os.path.join(dados_dir, 'csv')
        excel_dir = os.path.join(dados_dir, 'excel')
        
        os.makedirs(csv_dir, exist_ok=True)
        os.makedirs(excel_dir, exist_ok=True)
        
        # Timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Testar CSV
        csv_file = os.path.join(csv_dir, f'teste_pandas_{timestamp}.csv')
        df.to_csv(csv_file, index=False, encoding='utf-8')
        print(f"✅ CSV salvo em: {csv_file}")
        
        # Testar Excel
        excel_file = os.path.join(excel_dir, f'teste_pandas_{timestamp}.xlsx')
        with pd.ExcelWriter(excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Teste', index=False)
            
            # Formatação básica
            worksheet = writer.sheets['Teste']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✅ Excel salvo em: {excel_file}")
        
        # Verificar se arquivos existem
        if os.path.exists(csv_file) and os.path.exists(excel_file):
            print("\n🎉 Teste de pandas e Excel passou com sucesso!")
            print("✅ CSV e Excel estão funcionando perfeitamente")
            
            # Limpar arquivos de teste
            os.remove(csv_file)
            os.remove(excel_file)
            print("🧹 Arquivos de teste removidos")
            
            return True
        else:
            print("❌ Arquivos não foram criados corretamente")
            return False
            
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False

if __name__ == "__main__":
    sucesso = teste_pandas_excel()
    sys.exit(0 if sucesso else 1) 