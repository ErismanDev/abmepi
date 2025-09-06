# app/views.py
from django.http import HttpResponse
from .utils.carne_generator import gerar_carne

def download_carne(request):
    # Criar lista de mensalidades simuladas para teste
    mensalidades_teste = []
    for i in range(6):
        mensalidade = {
            'numero_doc': f"{235 + i:08d}/2025",
            'vencimento': f"{(5 + i) % 12 + 1:02d}/08/2025",
            'valor': 5.00
        }
        mensalidades_teste.append(mensalidade)
    
    pdf = gerar_carne(
        nome_associado="JOSE ERISMAN DE SOUSA",
        endereco="RUA TENENTE ARAÚJO, 1254",
        mensalidades_lista=mensalidades_teste,
        pix="86 988197790",
        titular="Gustavo Henrique de Araujo Sousa",
        banco="MERCADO PAGO"
    )

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="carne.pdf"'
    return response
