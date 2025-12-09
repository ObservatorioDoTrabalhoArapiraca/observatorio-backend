
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

# 📤 Exportar dados do Local para Railway

## Pré-requisitos (uma vez)
```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link do projeto
cd /home/usuario/Github/observatorio-backend
railway link
# Selecione: observatorio-backend → production
```

## Exportar 25 linhas por ano do banco local

```bash
cd /home/usuario/Github/observatorio-backend

# Exporta
docker-compose exec -T postgres psql -U postgres -d postgres <<'EOF' > dump_completo.csv
CREATE TEMP TABLE temp_export AS
SELECT 
  id, competencia_mov, municipio, secao, subclasse, saldo_movimentacao,
  cbo_2002_ocupacao, categoria, grau_de_instrucao, idade, horas_contratuais,
  raca_cor, sexo, tipo_empregador, tipo_estabelecimento, tipo_movimentacao,
  tipo_de_deficiencia, ind_trab_intermitente, ind_trab_parcial, salario,
  tam_estab_jan, indicador_aprendiz, origem_da_informacao, 
  indicador_de_fora_do_prazo, unidade_salario_codigo, faixa_etaria,
  faixa_hora_contrat, ano
FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY ano ORDER BY id) as rn
  FROM core_movimentacao WHERE ano IS NOT NULL
) sub WHERE rn <= 25;
COPY temp_export TO STDOUT WITH CSV HEADER;
EOF

# Remove cabeçalho
tail -n +2 dump_completo.csv > dump_sem_header.csv

# Verifica
echo "Linhas: $(wc -l < dump_sem_header.csv)"
head -2 dump_sem_header.csv
```

## Importar no Railway

```bash
# Importa
psql "postgresql://postgres:XSMVTMlWCTYPOixJKOrCBOFqACbBoVws@hopper.proxy.rlwy.net:58047/railway" <<'SQL'
COPY core_movimentacao (
  id, competencia_mov, municipio, secao, subclasse, saldo_movimentacao,
  cbo_2002_ocupacao, categoria, grau_de_instrucao, idade, horas_contratuais,
  raca_cor, sexo, tipo_empregador, tipo_estabelecimento, tipo_movimentacao,
  tipo_de_deficiencia, ind_trab_intermitente, ind_trab_parcial, salario,
  tam_estab_jan, indicador_aprendiz, origem_da_informacao, 
  indicador_de_fora_do_prazo, unidade_salario_codigo, faixa_etaria,
  faixa_hora_contrat, ano
) FROM STDIN WITH CSV;
SQL
 < dump_sem_header.csv

# Verifica
psql "postgresql://postgres:XSMVTMlWCTYPOixJKOrCBOFqACbBoVws@hopper.proxy.rlwy.net:58047/railway" \
  -c "SELECT ano, COUNT(*) as total FROM core_movimentacao GROUP BY ano ORDER BY ano;"

# Testa API
curl https://observatorio-backend-production.up.railway.app/api/ano-total-movimentacoes/

# Limpa cache
curl -X POST https://observatorio-backend-production.up.railway.app/api/limpar-cache/

# Limpa arquivos
rm dump_completo.csv dump_sem_header.csv
```

## Alterar quantidade de linhas

Para exportar mais linhas por ano, mude:
```sql
WHERE rn <= 50   -- 50 linhas por ano
WHERE rn <= 100  -- 100 linhas por ano
WHERE rn <= 200  -- 200 linhas por ano
```

---

# 🧹 Limpar cache

```bash
curl -X POST https://observatorio-backend-production.up.railway.app/api/limpar-cache/
```

---

# 🔍 Verificar dados no Railway

## Via SQL
```bash
psql "postgresql://postgres:XSMVTMlWCTYPOixJKOrCBOFqACbBoVws@hopper.proxy.rlwy.net:58047/railway" \
  -c "SELECT ano, COUNT(*) as total FROM core_movimentacao GROUP BY ano ORDER BY ano;"
```

## Via API
```bash
curl https://observatorio-backend-production.up.railway.app/api/ano-total-movimentacoes/
```








# limpar cache

https://observatorio-backend-production.up.railway.app/api/arapiraca/
