# Rota
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from apps.movimentacoes.views import (DistribuicaoSexoView,   DistribuicaoIdadeView,
    DistribuicaoEscolaridadeView, DistribuicaoRacaCorView, DistribuicaoPcdView, SalarioMedioPorOcupacaoView, DistribuicaoOcupacaoView,)
from core.views import (
    MedianaSalarioView,
    LimparCacheView,
    AnoTotalMovimentacoesView,
    MedianaSalarioPorEscolaridadeView,
    MedianaSalarioPorFaixaEtariaView,
    SalarioPorProfissaoView,
    ListarPdfsView,
    CagedEstListView,
    CagedEstStatsByMunicipioView,
    CagedEstStatsBySetorView,
    CagedEstDetailView,
    CagedEstTopEmpregadoresView,
    SaldoArapiracaListView,
    SaldoArapiracaSerieView,
    SaldoArapiracaByYearView,
    ServePdfView,
    SaldoArapiracaComparisonView)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/mediana-salario/', MedianaSalarioView.as_view(), name='mediana-salario'),
    path('api/ano-total-movimentacoes/', AnoTotalMovimentacoesView.as_view(), name='ano-total-movimentacoes'),
    path('api/salario-por-escolaridade/', MedianaSalarioPorEscolaridadeView.as_view(), name='salario-por-escolaridade'),
    path('api/salario-por-faixa-etaria/', MedianaSalarioPorFaixaEtariaView.as_view(), name='salario-por-faixa-etaria'),
    path('api/salario-por-profissao/', SalarioPorProfissaoView.as_view(), name='salario-por-profissao'),
    path('api/pdfs/', ListarPdfsView.as_view(), name='listar-pdfs'),
    path('api/limpar-cache/', LimparCacheView.as_view(), name='limpar-cache'),


    # NOVOS ENDPOINTS CAGEDEST
    path('api/cagedest/', CagedEstListView.as_view(), name='cagedest-list'),
    path('api/cagedest/<int:pk>/', CagedEstDetailView.as_view(), name='cagedest-detail'),
    path('api/cagedest/stats/municipio/', CagedEstStatsByMunicipioView.as_view(), name='cagedest-stats-municipio'),
    path('api/cagedest/stats/setor/', CagedEstStatsBySetorView.as_view(), name='cagedest-stats-setor'),
    path('api/cagedest/top-empregadores/', CagedEstTopEmpregadoresView.as_view(), name='cagedest-top-empregadores'),


  # ENDPOINTS ARAPIRACA (NOVO)
    path('api/arapiraca/', SaldoArapiracaListView.as_view(), name='arapiraca-list'),
    path('api/arapiraca/serie/', SaldoArapiracaSerieView.as_view(), name='arapiraca-serie'),
    path('api/arapiraca/<int:ano>/', SaldoArapiracaByYearView.as_view(), name='arapiraca-by-year'),
    path('api/arapiraca/comparacao/', SaldoArapiracaComparisonView.as_view(), name='arapiraca-comparison'),
    path('media/pdfs/<str:filename>', ServePdfView.as_view(), name='serve-pdf'),
    
    
    # meus novos paths aqui ver quais pode excluir acima..
    path('api/analises/sexo/', DistribuicaoSexoView.as_view(), name='analise-sexo'),
    path('api/analises/idade/', DistribuicaoIdadeView.as_view(), name='analise-idade'),
    path('api/analises/escolaridade/', DistribuicaoEscolaridadeView.as_view(), name='analise-escolaridade'),
    path('api/analises/raca-cor/', DistribuicaoRacaCorView.as_view(), name='distribuicao-raca-cor'),
    path('api/analises/pcd/', DistribuicaoPcdView.as_view(), name='distribuicao-pcd'),
    path('api/analises/salario-ocupacao/', SalarioMedioPorOcupacaoView.as_view(), name='salario-ocupacao'),
    path('api/analises/ocupacao/', DistribuicaoOcupacaoView.as_view(), name='distribuicao-ocupacao'), 
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
