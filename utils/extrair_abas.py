#  PYTHONPATH=. python utils/extrair_abas.py

import pandas as pd

# Carrega o arquivo excel com todas as abas

caminho_planilha = '/mnt/c/Users/Usuário/Downloads/202603-20260527T131109Z-3-001/202603/3-tabelas_Março de 2026.xlsx'
excel_file = pd.ExcelFile(caminho_planilha)
txt_final = ""

for sheet_name in excel_file.sheet_names:
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    
    # Transforma cada aba em uma seção textual
    txt_final += f"\n\n=========================================\n"
    txt_final += f"NOME DA ABA: {sheet_name}\n"
    txt_final += f"=========================================\n\n"
    txt_final += df.to_string(index=False)

# Salva tudo em um único arquivo TXT aceito pelo NotebookLM
with open("3-tabelas_Março_2026.txt", "w", encoding="utf-8") as f:
    f.write(txt_final)

print("Conversão concluída para o NotebookLM!")