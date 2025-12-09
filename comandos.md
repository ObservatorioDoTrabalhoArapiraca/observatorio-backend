
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


## baixar dados no banco para importar
  # Cria o dump com LIMIT
docker-compose exec -T postgres psql -U postgres -d postgres <<'EOF' > dump_25_por_ano.csv
-- Cria tabela temporária
CREATE TEMP TABLE temp_export AS
SELECT * FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY ano ORDER BY id) as rn
  FROM core_movimentacao
  WHERE ano IS NOT NULL
) sub
WHERE rn <= 25;

-- Exporta a tabela temporária
COPY temp_export TO STDOUT WITH CSV HEADER;
EOF


# Verifica o tamanho
ls -lh dump_25_por_ano.sql
wc -l dump_25_por_ano.sql

# importar dados no railway

npm i -g @railway/cli

railway login

cd /home/charlie/Documentos/github/observatorio-backend
railway link


(Selecione o projeto observatorio-backend)

Execute o comando de importação:

railway run python manage.py import_arapiraca dados/6-saldomunicipioajustado.xls


psql $DATABASE_URL -c "
COPY core_movimentacao 
FROM STDIN 
WITH CSV HEADER;
" < dump_25_por_ano.sql

# limpar cache

https://observatorio-backend-production.up.railway.app/api/arapiraca/
