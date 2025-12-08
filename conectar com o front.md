. URL Base da API: https://observatorio-backend-production.up.railway.app

Endpoints disponíveis:
// Exemplo de uso no frontend (fetch/axios)

const API_URL = 'https://observatorio-backend-production.up.railway.app'

// Arapiraca
fetch(`${API_URL}/api/arapiraca/`)
fetch(`${API_URL}/api/arapiraca/serie/`)
fetch(`${API_URL}/api/arapiraca/2019/`)
fetch(`${API_URL}/api/arapiraca/comparacao/`)

// CAGED Geral
fetch(`${API_URL}/api/mediana-salario/`)
fetch(`${API_URL}/api/ano-total-movimentacoes/`)
fetch(`${API_URL}/api/salario-por-escolaridade/`)
fetch(`${API_URL}/api/salario-por-faixa-etaria/`)
fetch(`${API_URL}/api/salario-por-profissao/`)

// Estabelecimentos
fetch(`${API_URL}/api/cagedest/`)
fetch(`${API_URL}/api/cagedest/stats/municipio/`)
fetch(`${API_URL}/api/cagedest/stats/setor/`)
fetch(`${API_URL}/api/cagedest/top-empregadores/`)
