
# migrações


# importar dados

docker exec -it django_backend python manage.py import_arapiraca dados/6-saldomunicipioajustado.xls

# inspecionar tebelas Xls

docker exec -it django_backend python manage.py inspect_xls dados/3-sintesedoempregoform




📊 RESUMO DO QUE VOCÊ TEM AGORA:
✅ Modelos criados:
Movimentacao - Dados CAGED de movimentações
CagedEst - Dados de estabelecimentos
SaldoArapiraca - Dados consolidados de Arapiraca
✅ Endpoints disponíveis:
Movimentação (original):

/api/mediana-salario/
/api/ano-total-movimentacoes/
/api/salario-por-escolaridade/
/api/salario-por-faixa-etaria/
/api/salario-por-profissao/
/api/pdfs/
CAGED Estabelecimentos:

/api/cagedest/
/api/cagedest/{id}/
/api/cagedest/stats/municipio/
/api/cagedest/stats/setor/
/api/cagedest/top-empregadores/
Arapiraca (novo):

/api/arapiraca/ - Lista todos os períodos
/api/arapiraca/serie/ - Série histórica 2002-2019
/api/arapiraca/{ano}/ - Dados de um ano específico
/api/arapiraca/comparacao/ - Comparação ano a ano
✅ Comandos de importação:
import_parquet - Importa arquivos Parquet
import_all_parquet - Importa múltiplos Parquets
import_csv - Converte CSV → Parquet → Importa
import_all_csv - Múltiplos CSVs
import_xls - XLS → CSV → Importa
import_arapiraca - Específico para Arapiraca
inspect_xls - Inspeciona estrutura de XLS