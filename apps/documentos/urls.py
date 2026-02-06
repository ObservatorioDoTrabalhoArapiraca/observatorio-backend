from django.urls import path
from .views import ListarPdfsView, ServePdfView

app_name = 'documentos'

urlpatterns = [
    path('pdfs/', ListarPdfsView.as_view(), name='listar-pdfs'),
    path('pdfs/<str:filename>/', ServePdfView.as_view(), name='serve-pdf'),
]