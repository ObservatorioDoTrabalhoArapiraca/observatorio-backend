from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from django.http import FileResponse, Http404
from urllib.parse import quote
import os


class ListarPdfsView(APIView):
    """
    Lista todos os PDFs disponíveis na pasta media/pdfs/
    GET /api/pdfs/
    """
    def get(self, request):
        pasta_pdfs = os.path.join(settings.BASE_DIR, 'media', 'pdfs')
        
        if not os.path.exists(pasta_pdfs):
            return Response({
                'erro': 'Pasta media/pdfs/ não encontrada',
                'caminho': str(pasta_pdfs),
                'pdfs': []
            })
        
        pdfs = []
        for arquivo in os.listdir(pasta_pdfs):
            if arquivo.endswith('.pdf'):
                caminho_completo = os.path.join(pasta_pdfs, arquivo)
                tamanho = os.path.getsize(caminho_completo)
                
                # ✅ Codifica o nome do arquivo para URL (espaços viram %20)
                arquivo_encoded = quote(arquivo)
                
                pdfs.append({
                    'nome': arquivo,  # Nome original (com espaços)
                    'url': f"/media/pdfs/{arquivo_encoded}",  # URL codificada
                    'tamanho_bytes': tamanho,
                    'tamanho_mb': round(tamanho / (1024 * 1024), 2)
                })
        
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
        filename = os.path.basename(filename)
        caminho_pdf = os.path.join(settings.BASE_DIR, 'media', 'pdfs', filename)
        
        if not os.path.exists(caminho_pdf):
            raise Http404("PDF não encontrado")
        
        if not filename.endswith('.pdf'):
            raise Http404("Arquivo inválido")
        
        return FileResponse(
            open(caminho_pdf, 'rb'),
            content_type='application/pdf',
            as_attachment=False
        )