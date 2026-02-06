# Rota
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.movimentacoes.views import (
    DistribuicaoSexoView,   DistribuicaoIdadeView,
    DistribuicaoEscolaridadeView, DistribuicaoRacaCorView, DistribuicaoPcdView, SalarioMedioPorOcupacaoView, DistribuicaoOcupacaoView, MovimentacoesListView
)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('apps.documentos.urls')),
  
    # meus novos paths aqui ver quais pode excluir acima..
    path('api/analises/sexo/', DistribuicaoSexoView.as_view(), name='analise-sexo'),
    path('api/analises/idade/', DistribuicaoIdadeView.as_view(), name='analise-idade'),
    path('api/analises/escolaridade/', DistribuicaoEscolaridadeView.as_view(), name='analise-escolaridade'),
    path('api/analises/raca-cor/', DistribuicaoRacaCorView.as_view(), name='distribuicao-raca-cor'),
    path('api/analises/pcd/', DistribuicaoPcdView.as_view(), name='distribuicao-pcd'),
    path('api/analises/salario-ocupacao/', SalarioMedioPorOcupacaoView.as_view(), name='salario-ocupacao'),
    path('api/analises/ocupacao/', DistribuicaoOcupacaoView.as_view(), name='distribuicao-ocupacao'), 
    path('api/movimentacoes/', MovimentacoesListView.as_view(), name='movimentacoes-list'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
