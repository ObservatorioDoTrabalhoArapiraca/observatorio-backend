import numpy as np
import pandas as pd
import csv
import os
from django.core.management.base import BaseCommand
from apps.referenciais import models

class Command(BaseCommand):
    help = 'Importa tabela de referência de setor a partir de abas do Excel'

    def handle(self, *args, **kwargs):
        caminho = 'apps/referenciais/Layout Não-identificado Novo Caged Movimentação.xlsx'
        aba_nome = 'setor'

        df = pd.read_excel(caminho, sheet_name=aba_nome)
        
        # 2. Normaliza colunas: remove espaços extras e põe em minúsculo
        # O .strip() aqui limpa " Seção_inicio " para "seção_inicio"
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # 3. Limpa a tabela antes de começar
        models.SetorAgregadoReferencia.objects.all().delete()

        def converter_valor_para_int(valor):
            """Garante que '1', '1.0' ou 1 virem o inteiro 1, e vazios virem None."""
            if valor is None or str(valor).strip().lower() in ['nan', 'none', '', '(nada)']:
                return None
            try:
                return int(float(str(valor).replace(',', '.')))
            except (ValueError, TypeError):
                return None

        def limpar_secao(valor):
            """Limpa a letra da seção (A, B, etc)"""
            v = str(valor).strip().upper()
            if v in ['NAN', 'NONE', '', '(NADA)', '(NÃO TEM NADA)']:
                return None
            return v

        setores_criados = 0
        for _, row in df.iterrows():
            # Mapeamento dinâmico baseado no que você mandou (ajustado para o .lower())
            # Tentamos pegar com ou sem o sufixo '_inicio'/'_fim'
            s_ini = limpar_secao(row.get('seção_inicio', row.get('secao_inicio', row.get('seção'))))
            s_fim = limpar_secao(row.get('seção_fim', row.get('secao_fim', row.get('seção_fim'))))
            
            d_ini = converter_valor_para_int(row.get('divisão_inicio', row.get('divisao_inicio')))
            d_fim = converter_valor_para_int(row.get('divisão_fim', row.get('divisao_fim')))
            
            denom = str(row.get('denominação', row.get('denominacao', ''))).strip()

            # Só cria se tiver pelo menos uma seção ou uma divisão
            if s_ini or d_ini:
                models.SetorAgregadoReferencia.objects.create(
                    secao_inicio=s_ini,
                    secao_fim=s_fim,
                    divisao_inicio=d_ini,
                    divisao_fim=d_fim,
                    denominacao=denom
                )
                setores_criados += 1

        self.stdout.write(self.style.SUCCESS(f"✅ {setores_criados} setores importados com sucesso!"))