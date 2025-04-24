from django.contrib import admin
from django.urls import path
from core.views import MedianaSalarioView, AnoTotalMovimentacoesView, MedianaSalarioPorEscolaridadeView, MedianaSalarioPorFaixaEtariaView, SalarioPorProfissaoView

#TO DO:Melhorar nome das rotas

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/mediana-salario/', MedianaSalarioView.as_view(), name='mediana-salario'),
    path('api/ano-total-movimentacoes/', AnoTotalMovimentacoesView.as_view(), name='ano-total-movimentacoes'),
    path('api/salario-por-escolaridade/', MedianaSalarioPorEscolaridadeView.as_view(), name='salario-por-escolaridade'),
    path('api/salario-por-faixa-etaria/', MedianaSalarioPorFaixaEtariaView.as_view(), name='salario-por-faixa-etaria'),
    path('api/salario-por-profissao/', SalarioPorProfissaoView.as_view(), name='salario-por-profissao'),  
]