from fastapi import APIRouter, HTTPException, Query
import httpx

router = APIRouter()

BASE_URL = "https://script.googleusercontent.com/macros/"

pdfsListLinks = [
    {
        "label": "mensal",
        "url": "s/AKfycbwQdKuILH--r7y_MHl5DcIFLiuTr91vtJ9BzmXBLEBDH97FzhV8iUgrBS6NenTHZHYN/exec",
    },
    {
        "label": "anual",
        "url": "s/AKfycbzqVXFv6SIvMIPEQ9vp1goXYJFe-RCLrzO3qn-cWVzmyvk2NrqscHZ44c2BcAcr4kin0w/exec",
    },
    {
        "label": "conjuntural",
        "url": "s/AKfycbyaU0I6oMTKt-FEMe2OSlQ_ntgEMavIHJXBfvZY1mhkw_KNIXzDoKbTpi7iqJOqOMZbTQ/exec"
    },
    {
        "label": "tematico",
        "url": "s/AKfycbx1-q7mLw2d8STcyIrKaUa4ee9K4NvveLvpCo2biPuZbNDMhXmz28_e_qrwXD0h50lyfg/exec"
    },
]

@router.get("/pdfs")
async def get_pdfs(tipo: str = Query(..., description="Tipo de PDF a ser buscado: mensal, anual, conjuntural ou tematico")):
  item = next((x for x in pdfsListLinks if x["label"] == tipo), None)
  if not item:
    raise HTTPException(status_code=400, detail="Tipo de PDF inválido.")     
    
  headers = {
        "Accept": "aplication/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0",
    }
  async with httpx.AsyncClient(follow_redirects=True, timeout=30.0, max_redirects=5) as client: 
    try:
      full_url = BASE_URL + item["url"]
      response = await client.get(full_url, headers=headers)
      
      if "text/html" in response.headers.get("Content-Type", ""):
        raise HTTPException(status_code=502, detail="Google retornou HTML em vez de JSON. Verifique as permissões do Script.")
      
      return response.json()
   
    except httpx.HTTPStatusError as e:
      raise HTTPException(status_code=e.response.status_code, detail=f"Erro na API do Google: {str(e)}")
    except Exception as e:
      raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")