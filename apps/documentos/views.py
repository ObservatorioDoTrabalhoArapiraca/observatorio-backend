from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.http import FileResponse, Http404
import os


class ListarPdfsView(APIView):
    """
    Lista todos os PDFs disponíveis na pasta media/pdfs/
    GET /api/pdfs/
    """
    def get(self, request):
        pasta_pdfs = os.path.join(settings.MEDIA_ROOT, 'pdfs')
        
        if not os.path.exists(pasta_pdfs):
            return Response({'pdfs': []})
        
        pdfs = []
        for arquivo in os.listdir(pasta_pdfs):
            if arquivo.endswith('.pdf'):
                tamanho = os.path.getsize(os.path.join(pasta_pdfs, arquivo))
                pdfs.append({
                    'nome': arquivo,
                    'url': f"{settings.MEDIA_URL}pdfs/{arquivo}",
                    'tamanho_bytes': tamanho
                })
        
        # Ordena por nome
        pdfs.sort(key=lambda x: x['nome'])
        
        return Response({
            'total': len(pdfs),
            'pdfs': pdfs
        })


class ServePdfView(APIView):
    """
    Serve um PDF específico
    GET /media/pdfs/<filename>
    """
    def get(self, request, filename):
        # Sanitiza o nome do arquivo por segurança
        filename = os.path.basename(filename)
        caminho_pdf = os.path.join(settings.MEDIA_ROOT, 'pdfs', filename)
        
        if not os.path.exists(caminho_pdf):
            raise Http404("PDF não encontrado")
        
        if not filename.endswith('.pdf'):
            raise Http404("Arquivo inválido")
        
        return FileResponse(
            open(caminho_pdf, 'rb'),
            content_type='application/pdf',
            as_attachment=False  # Abre no navegador ao invés de baixar
        )