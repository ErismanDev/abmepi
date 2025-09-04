# app/utils/carne_generator.py
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
import io
import os
from datetime import datetime

def gerar_carne(nome_associado, endereco, mensalidades_lista, config_cobranca=None, pix=None, titular=None, banco=None):
    """
    Gera carnê em PDF com layout de duas partes:
    - Esquerda: Comprovante (fica com o pagador)
    - Direita: Parte destacável (fica com a associação)
    
    Layout: 2 colunas × 3 linhas por página em paisagem
    Dimensões: 136 × 60 mm cada boletim
    Margens: 10mm, Gaps: 5mm
    
    Parâmetros:
    - config_cobranca: Objeto ConfiguracaoCobranca (preferencial)
    - pix, titular, banco: Parâmetros diretos (para compatibilidade)
    """
    # Usar configuração de cobrança se fornecida, senão usar parâmetros diretos
    if config_cobranca:
        pix = config_cobranca.chave_pix
        titular = config_cobranca.titular
        banco = config_cobranca.banco
        mensagem = config_cobranca.mensagem
        telefone_comprovante = config_cobranca.telefone_comprovante
        qr_code_ativo = config_cobranca.qr_code_ativo
        qr_code_tamanho = config_cobranca.qr_code_tamanho
    else:
        # Valores padrão para compatibilidade
        mensagem = "Pague Suas mensalidade na sede da associação ou pelo QRcode e mande o comprovante para"
        telefone_comprovante = "86 988197790"
        qr_code_ativo = True
        qr_code_tamanho = 15
    
    buffer = io.BytesIO()
    
    # Configuração da página em paisagem A4
    largura_pagina, altura_pagina = landscape(A4)
    
    # Criar canvas
    c = canvas.Canvas(buffer, pagesize=(largura_pagina, altura_pagina))
    
    # Configurações das dimensões
    margem = 10 * mm
    gap = 5 * mm
    largura_carne = 136 * mm
    altura_carne = 60 * mm
    
    # Calcular posições para 2x3 grid
    posicoes_x = [margem, margem + largura_carne + gap]
    posicoes_y = [altura_pagina - margem - altura_carne, 
                  altura_pagina - margem - 2*altura_carne - gap,
                  altura_pagina - margem - 3*altura_carne - 2*gap]
    
    # Contador para mensalidades
    mensalidade_index = 0
    pagina_atual = 1
    
    while mensalidade_index < len(mensalidades_lista):
        # Cabeçalho removido para layout mais limpo
        
        # Desenhar 6 boletins por página (2x3)
        for linha in range(3):
            for coluna in range(2):
                if mensalidade_index >= len(mensalidades_lista):
                    break
                
                # Posição do boletim
                x = posicoes_x[coluna]
                y = posicoes_y[linha]
                
                # Obter dados da mensalidade
                mensalidade = mensalidades_lista[mensalidade_index]
                
                # Verificar se é objeto ou dicionário
                if hasattr(mensalidade, 'id'):
                    numero_doc = f"{str(mensalidade.id).zfill(8)}/{mensalidade.data_vencimento.year}"
                    vencimento = mensalidade.data_vencimento.strftime('%d/%m/%Y')
                    valor = mensalidade.valor
                else:
                    numero_doc = mensalidade.get('numero_doc', '')
                    vencimento = mensalidade.get('vencimento', '')
                    valor = mensalidade.get('valor', 0)
                
                # Desenhar boletim
                desenhar_boletim(c, x, y, largura_carne, altura_carne, 
                                numero_doc, vencimento, valor, nome_associado, 
                                endereco, pix, titular, banco, mensagem, telefone_comprovante, qr_code_ativo, qr_code_tamanho, config_cobranca)
                
                mensalidade_index += 1
        
        # Quebra de página se não for a última
        if mensalidade_index < len(mensalidades_lista):
            c.showPage()
            pagina_atual += 1
    
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def desenhar_boletim(c, x, y, largura, altura, numero_doc, vencimento, valor, 
                     nome_associado, endereco, pix, titular, banco, mensagem, telefone_comprovante, qr_code_ativo, qr_code_tamanho, config_cobranca=None):
    """
    Desenha um boletim individual com duas partes:
    - Esquerda: Comprovante (27% da largura)
    - Direita: Parte destacável (73% da largura)
    """
    # Configurar cores e estilos
    c.setStrokeColorRGB(0, 0, 0)  # Preto
    c.setLineWidth(1)
    
    # Calcular proporções das duas partes
    largura_comprovante = largura * 0.27  # 27% para comprovante
    largura_destacavel = largura * 0.73   # 73% para parte destacável
    
    # Desenhar retângulo externo
    c.rect(x, y, largura, altura)
    
    # Desenhar linha separadora vertical (tracejada)
    x_separador = x + largura_comprovante
    c.setDash(3, 3)  # Linha tracejada
    c.line(x_separador, y, x_separador, y + altura)
    c.setDash()  # Reset para linha sólida
    
    # ===== PARTE ESQUERDA: COMPROVANTE =====
    # Logo ABMEPI no topo esquerdo (proporcional aos dados)
    try:
        from reportlab.lib.utils import ImageReader
        # Caminho absoluto para a logo
        import os
        # Navegar do diretório atual (app/utils/) para o diretório raiz do projeto
        current_dir = os.path.dirname(os.path.abspath(__file__))  # app/utils/
        app_dir = os.path.dirname(current_dir)                    # app/
        project_dir = os.path.dirname(app_dir)                    # raiz do projeto
        logo_path = os.path.join(project_dir, 'static', 'Logo_abmepi.png')
        
        if os.path.exists(logo_path):
            img = ImageReader(logo_path)
            # Calcular dimensões da logo (muito menor e proporcional)
            logo_width = largura_comprovante * 0.35  # 35% da largura do comprovante
            logo_height = logo_width * (img._image.height / img._image.width)  # Manter proporção
            # Centralizar a logo no topo
            logo_x = x + (largura_comprovante - logo_width) / 2
            logo_y = y + altura - logo_height - 2*mm  # 2mm do topo
            c.drawImage(logo_path, logo_x, logo_y, logo_width, logo_height)
        else:
            # Fallback: texto ABMEPI se a imagem não existir
            c.setFont("Helvetica-Bold", 12)
            c.drawCentredString(x + largura_comprovante/2, y + altura - 8*mm, "ABMEPI")
    except Exception as e:
        # Fallback: texto ABMEPI se houver erro
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(x + largura_comprovante/2, y + altura - 8*mm, "ABMEPI")
    
    # Dados do comprovante (distribuídos proporcionalmente abaixo da logo)
    c.setFont("Helvetica", 7)  # Fonte menor para títulos
    
    # Número do documento
    c.drawString(x + 2*mm, y + altura - 21*mm, "Nº do documento:")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 2*mm, y + altura - 24*mm, numero_doc)
    
    # Vencimento
    c.setFont("Helvetica", 7)
    c.drawString(x + 2*mm, y + altura - 29*mm, "Vencimento:")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 2*mm, y + altura - 32*mm, vencimento)
    
    # Valor
    c.setFont("Helvetica", 7)
    c.drawString(x + 2*mm, y + altura - 37*mm, "Valor:")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 2*mm, y + altura - 40*mm, f"R$ {valor:.2f}")
    
    # Associado (sempre em duas linhas no canhoto)
    c.setFont("Helvetica", 7)
    c.drawString(x + 2*mm, y + altura - 45*mm, "Associado:")
    c.setFont("Helvetica-Bold", 8)
    
    # Sempre dividir nome em duas linhas no canhoto
    nome_limpo = nome_associado.strip()
    # Encontrar o meio do nome para dividir
    palavras = nome_limpo.split()
    if len(palavras) > 1:
        meio = len(palavras) // 2
        linha1 = ' '.join(palavras[:meio])
        linha2 = ' '.join(palavras[meio:])
        c.drawString(x + 2*mm, y + altura - 48*mm, linha1[:18])  # Primeira linha
        c.drawString(x + 2*mm, y + altura - 51*mm, linha2[:18])  # Segunda linha
    else:
        # Se for uma palavra só, dividir no meio
        meio = len(nome_limpo) // 2
        c.drawString(x + 2*mm, y + altura - 48*mm, nome_limpo[:meio])
        c.drawString(x + 2*mm, y + altura - 51*mm, nome_limpo[meio:])
    
    # ===== PARTE DIREITA: DESTACÁVEL =====
    x_destacavel = x + largura_comprovante + 2*mm
    
    # Vencimento e Número do documento na mesma linha (topo)
    c.setFont("Helvetica", 7)
    c.drawString(x_destacavel, y + altura - 8*mm, "Nº do documento:")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_destacavel + 25*mm, y + altura - 8*mm, numero_doc)
    
    c.setFont("Helvetica", 7)
    c.drawString(x_destacavel + largura_destacavel - 35*mm, y + altura - 8*mm, "Vencimento:")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_destacavel + largura_destacavel - 20*mm, y + altura - 8*mm, vencimento)
    
    # Valor (abaixo do vencimento)
    c.setFont("Helvetica", 7)
    c.drawString(x_destacavel + largura_destacavel - 35*mm, y + altura - 13*mm, "Valor:")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x_destacavel + largura_destacavel - 20*mm, y + altura - 13*mm, f"R$ {valor:.2f}")
    
    # Dados principais (alinhados à esquerda)
    c.setFont("Helvetica", 7)
    
    # Mensagem (5mm abaixo do número do documento)
    c.setFont("Helvetica", 7)
    c.drawString(x_destacavel, y + altura - 13*mm, "MENSAGEM:")
    
    # Exibir mensagem personalizada quebrando em exatamente 3 linhas e justificando
    mensagem_limpa = mensagem.strip()
    telefone_limpo = telefone_comprovante.strip()
    
    # Dividir mensagem em exatamente 3 linhas
    palavras = mensagem_limpa.split()
    linhas_mensagem = []
    
    if len(palavras) >= 3:
        # Dividir em 3 partes aproximadamente iguais
        parte1 = len(palavras) // 3
        parte2 = 2 * len(palavras) // 3
        
        linha1 = ' '.join(palavras[:parte1])
        linha2 = ' '.join(palavras[parte1:parte2])
        linha3 = ' '.join(palavras[parte2:])
        
        linhas_mensagem = [linha1, linha2, linha3]
    elif len(palavras) == 2:
        # Se tiver 2 palavras, dividir cada uma no meio
        meio1 = len(palavras[0]) // 2
        meio2 = len(palavras[1]) // 2
        
        linha1 = palavras[0][:meio1]
        linha2 = palavras[0][meio1:] + " " + palavras[1][:meio2]
        linha3 = palavras[1][meio2:]
        
        linhas_mensagem = [linha1, linha2, linha3]
    else:
        # Se tiver 1 palavra só, dividir em 3 partes
        meio1 = len(mensagem_limpa) // 3
        meio2 = 2 * len(mensagem_limpo) // 3
        
        linha1 = mensagem_limpo[:meio1]
        linha2 = mensagem_limpo[meio1:meio2]
        linha3 = mensagem_limpo[meio2:]
        
        linhas_mensagem = [linha1, linha2, linha3]
    
    # Exibir mensagem em 3 linhas justificadas
    largura_texto = largura_destacavel - 2*mm  # Largura disponível para texto
    for i, linha in enumerate(linhas_mensagem):
        # Manter alinhamento à esquerda como o título, mas justificar o texto
        c.drawString(x_destacavel, y + altura - (17 + i*3)*mm, linha)
    
    # Exibir telefone na linha seguinte (alinhado à esquerda como o título)
    telefone_texto = f"Telefone: {telefone_limpo}"
    c.drawString(x_destacavel, y + altura - 26*mm, telefone_texto)
    
    # Associado (ajustado para acomodar mensagem em 3 linhas)
    c.setFont("Helvetica", 7)
    c.drawString(x_destacavel, y + altura - 32*mm, "Associado:")
    c.setFont("Helvetica-Bold", 8)
    
    # Dividir nome em duas linhas se for muito longo
    nome_limpo = nome_associado.strip()
    if len(nome_limpo) > 25:  # Se o nome for muito longo
        # Encontrar o meio do nome para dividir
        palavras = nome_limpo.split()
        if len(palavras) > 1:
            meio = len(palavras) // 2
            linha1 = ' '.join(palavras[:meio])
            linha2 = ' '.join(palavras[meio:])
            c.drawString(x_destacavel, y + altura - 35*mm, linha1)  # Primeira linha (nome completo)
            c.drawString(x_destacavel, y + altura - 38*mm, linha2)  # Segunda linha (nome completo)
        else:
            # Se for uma palavra só, dividir no meio
            meio = len(nome_limpo) // 2
            c.drawString(x_destacavel, y + altura - 35*mm, nome_limpo[:meio])
            c.drawString(x_destacavel, y + altura - 38*mm, nome_limpo[meio:])
    else:
        # Nome curto, uma linha só (nome completo)
        c.drawString(x_destacavel, y + altura - 35*mm, nome_limpo)
    
    # Endereço (ajustado para acomodar nova estrutura)
    c.setFont("Helvetica", 7)
    c.drawString(x_destacavel, y + altura - 43*mm, "Endereço:")
    c.setFont("Helvetica-Bold", 8)
    
    # Dividir endereço em três linhas (endereço completo)
    endereco_limpo = endereco.strip()
    palavras = endereco_limpo.split()
    
    if len(palavras) >= 3:  # Se tiver 3 ou mais palavras, dividir em 3 partes
        # Dividir em 3 partes aproximadamente iguais
        parte1 = len(palavras) // 3
        parte2 = 2 * len(palavras) // 3
        
        linha1 = ' '.join(palavras[:parte1])
        linha2 = ' '.join(palavras[parte1:parte2])
        linha3 = ' '.join(palavras[parte2:])
        
        c.drawString(x_destacavel, y + altura - 46*mm, linha1)  # Primeira linha (completa)
        c.drawString(x_destacavel, y + altura - 49*mm, linha2)  # Segunda linha (completa)
        c.drawString(x_destacavel, y + altura - 52*mm, linha3)  # Terceira linha (completa)
        
    elif len(palavras) == 2:  # Se tiver 2 palavras, dividir em 3 partes
        # Dividir cada palavra no meio
        meio1 = len(palavras[0]) // 2
        meio2 = len(palavras[1]) // 2
        
        linha1 = palavras[0][:meio1]
        linha2 = palavras[0][meio1:] + " " + palavras[1][:meio2]
        linha3 = palavras[1][meio2:]
        
        c.drawString(x_destacavel, y + altura - 46*mm, linha1)  # Primeira linha (completa)
        c.drawString(x_destacavel, y + altura - 49*mm, linha2)  # Segunda linha (completa)
        c.drawString(x_destacavel, y + altura - 52*mm, linha3)  # Terceira linha (completa)
        
    else:  # Se tiver 1 palavra só, dividir em 3 partes
        meio1 = len(endereco_limpo) // 3
        meio2 = 2 * len(endereco_limpo) // 3
        
        c.drawString(x_destacavel, y + altura - 46*mm, endereco_limpo[:meio1])  # Primeira linha
        c.drawString(x_destacavel, y + altura - 49*mm, endereco_limpo[meio1:meio2])  # Segunda linha
        c.drawString(x_destacavel, y + altura - 52*mm, endereco_limpo[meio2:])  # Terceira linha
    
    # QR Code (alinhado com o campo de vencimento - baixado 0,5cm e movido 0,5cm à esquerda)
    if qr_code_ativo:
        qr_size = qr_code_tamanho * mm
        # Alinhar o QR Code com o campo de vencimento (lado direito) - baixado 0,5cm e movido 0,5cm à esquerda
        qr_x = x_destacavel + largura_destacavel - qr_size - 5*mm - 5*mm  # Movido 0,5cm (5mm) à esquerda
        qr_y = y + altura - 35*mm  # Baixado 0,5cm (5mm) - era 40mm, agora 35mm
        
        # Tentar exibir imagem do QR Code se estiver configurada
        if config_cobranca and config_cobranca.qr_code_imagem:
            try:
                from reportlab.lib.utils import ImageReader
                # Obter o caminho completo da imagem
                if hasattr(config_cobranca.qr_code_imagem, 'path'):
                    # Se for um campo ImageField do Django
                    qr_image_path = config_cobranca.qr_code_imagem.path
                else:
                    # Se for um caminho string
                    qr_image_path = str(config_cobranca.qr_code_imagem)
                
                # Verificar se o arquivo existe
                if os.path.exists(qr_image_path):
                    img = ImageReader(qr_image_path)
                    c.drawImage(qr_image_path, qr_x, qr_y, qr_size, qr_size)
                else:
                    # Fallback para QR Code padrão se arquivo não existir
                    c.setStrokeColorRGB(0.8, 0.8, 0.8)
                    c.rect(qr_x, qr_y, qr_size, qr_size)
                    c.setFont("Helvetica", 6)
                    c.drawCentredString(qr_x + qr_size/2, qr_y + qr_size/2 + 2*mm, "QR CODE")
            except Exception as e:
                # Fallback para QR Code padrão se houver erro
                c.setStrokeColorRGB(0.8, 0.8, 0.8)
                c.rect(qr_x, qr_y, qr_size, qr_size)
                c.setFont("Helvetica", 6)
                c.drawCentredString(qr_x + qr_size/2, qr_y + qr_size/2 + 2*mm, "QR CODE")
        else:
            # QR Code padrão (retângulo com texto) se não houver imagem configurada
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.rect(qr_x, qr_y, qr_size, qr_size)
            c.setFont("Helvetica", 6)
            c.drawCentredString(qr_x + qr_size/2, qr_y + qr_size/2 + 2*mm, "QR CODE")
    
    # Dados de cobrança (espaçamento reduzido entre os campos)
    c.setStrokeColorRGB(0, 0, 0)
    
    # Chave Pix (sem título - espaçamento reduzido)
    c.setFont("Helvetica-Bold", 6)
    c.drawString(x_destacavel + largura_destacavel - 50*mm, y + altura - 42*mm, pix)
    
    # Titular (sem título - espaçamento reduzido)
    c.setFont("Helvetica-Bold", 6)  # Fonte menor para o texto
    
    # Dividir titular em duas linhas (espaçamento reduzido)
    titular_limpo = titular.strip()
    palavras = titular_limpo.split()
    
    if len(palavras) >= 2:
        # Dividir em 2 partes aproximadamente iguais
        meio = len(palavras) // 2
        
        linha1 = ' '.join(palavras[:meio])
        linha2 = ' '.join(palavras[meio:])
        
        c.drawString(x_destacavel + largura_destacavel - 50*mm, y + altura - 46*mm, linha1)
        c.drawString(x_destacavel + largura_destacavel - 50*mm, y + altura - 49*mm, linha2)
    else:
        # Se for uma palavra só, dividir no meio
        meio = len(titular_limpo) // 2
        c.drawString(x_destacavel + largura_destacavel - 50*mm, y + altura - 46*mm, titular_limpo[:meio])
        c.drawString(x_destacavel + largura_destacavel - 50*mm, y + altura - 49*mm, titular_limpo[meio:])
    
    # Banco (sem título - espaçamento reduzido)
    c.setFont("Helvetica-Bold", 6)  # Fonte menor para o texto
    
    # Dividir banco em duas linhas se for muito longo
    banco_limpo = banco.strip()
    if len(banco_limpo) > 20:  # Se o nome for muito longo
        # Encontrar o meio do nome para dividir
        palavras = banco_limpo.split()
        if len(palavras) > 1:
            meio = len(palavras) // 2
            linha1 = ' '.join(palavras[:meio])
            linha2 = ' '.join(palavras[meio:])
            c.drawString(x_destacavel + largura_destacavel - 50*mm, y + altura - 53*mm, linha1)
            c.drawString(x_destacavel + largura_destacavel - 50*mm, y + altura - 56*mm, linha2)
        else:
            # Se for uma palavra só, dividir no meio
            meio = len(banco_limpo) // 2
            c.drawString(x_destacavel + largura_destacavel - 50*mm, y + altura - 53*mm, banco_limpo[:meio])
            c.drawString(x_destacavel + largura_destacavel - 50*mm, y + altura - 56*mm, banco_limpo[meio:])
    else:
        # Nome curto, uma linha só
        c.drawString(x_destacavel + largura_destacavel - 50*mm, y + altura - 53*mm, banco_limpo)

# Função de compatibilidade para manter o código antigo funcionando
def gerar_carne_antigo(nome_associado, endereco, documento_inicial, data_inicio, meses, valor, pix, titular, banco):
    """
    Função de compatibilidade para o código antigo
    """
    from datetime import datetime, timedelta
    
    # Criar lista de mensalidades simuladas
    mensalidades_lista = []
    data_inicio_obj = datetime.strptime(data_inicio, "%d/%m/%Y")
    
    for i in range(meses):
        mensalidade = {
            'numero_doc': f"{documento_inicial + i:08d}/{data_inicio_obj.year}",
            'vencimento': (data_inicio_obj + timedelta(days=30 * i)).strftime("%d/%m/%Y"),
            'valor': valor
        }
        mensalidades_lista.append(mensalidade)
    
    return gerar_carne(nome_associado, endereco, mensalidades_lista, config_cobranca=None, pix=pix, titular=titular, banco=banco)
