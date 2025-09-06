from django.shortcuts import get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import AtaReuniao, CargoDiretoria, MembroDiretoria
import re


def get_logo_path(logo_filename):
    """Função auxiliar para obter o caminho do logo"""
    import os
    from django.conf import settings
    
    # Tentar diferentes caminhos para o logo
    possible_paths = [
        os.path.join(settings.STATIC_ROOT, logo_filename),
        os.path.join(settings.STATICFILES_DIRS[0], logo_filename),
        os.path.join(settings.BASE_DIR, 'static', logo_filename),
        os.path.join(settings.BASE_DIR, 'media', logo_filename),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None


def clean_html_for_pdf(html_content):
    """
    Limpar HTML complexo para ser usado no ReportLab, preservando formatação básica
    """
    if not html_content:
        return ""
    
    # Decodificar entidades HTML primeiro
    html_content = html_content.replace('&nbsp;', ' ')
    html_content = html_content.replace('&amp;', '&')
    html_content = html_content.replace('&lt;', '<')
    html_content = html_content.replace('&gt;', '>')
    html_content = html_content.replace('&quot;', '"')
    html_content = html_content.replace('&#39;', "'")
    html_content = html_content.replace('&ccedil;', 'ç')
    html_content = html_content.replace('&atilde;', 'ã')
    html_content = html_content.replace('&iacute;', 'í')
    html_content = html_content.replace('&ordm;', 'º')
    html_content = html_content.replace('&Oacute;', 'Ó')
    html_content = html_content.replace('&aacute;', 'á')
    html_content = html_content.replace('&eacute;', 'é')
    html_content = html_content.replace('&iacute;', 'í')
    html_content = html_content.replace('&oacute;', 'ó')
    html_content = html_content.replace('&uacute;', 'ú')
    html_content = html_content.replace('&Aacute;', 'Á')
    html_content = html_content.replace('&Eacute;', 'É')
    html_content = html_content.replace('&Iacute;', 'Í')
    html_content = html_content.replace('&Oacute;', 'Ó')
    html_content = html_content.replace('&Uacute;', 'Ú')
    
    # Converter quebras de linha
    html_content = html_content.replace('<br>', '\n')
    html_content = html_content.replace('<br/>', '\n')
    html_content = html_content.replace('<br />', '\n')
    
    # Converter parágrafos
    html_content = html_content.replace('<p>', '\n')
    html_content = html_content.replace('</p>', '\n')
    
    # Converter listas
    html_content = html_content.replace('<ul>', '\n')
    html_content = html_content.replace('</ul>', '\n')
    html_content = html_content.replace('<ol>', '\n')
    html_content = html_content.replace('</ol>', '\n')
    html_content = html_content.replace('<li>', '• ')
    html_content = html_content.replace('</li>', '\n')
    
    # Converter títulos
    html_content = re.sub(r'<h[1-6][^>]*>', '\n', html_content)
    html_content = re.sub(r'</h[1-6]>', '\n', html_content)
    
    # Converter negrito e itálico (manter como texto simples)
    html_content = re.sub(r'<(strong|b)[^>]*>', '', html_content)
    html_content = re.sub(r'</(strong|b)>', '', html_content)
    html_content = re.sub(r'<(em|i)[^>]*>', '', html_content)
    html_content = re.sub(r'</(em|i)>', '', html_content)
    
    # Remover todas as outras tags HTML
    html_content = re.sub(r'<[^>]+>', '', html_content)
    
    # Limpar espaços extras e quebras de linha
    html_content = re.sub(r'\n\s*\n', '\n\n', html_content)  # Múltiplas quebras viram dupla
    html_content = re.sub(r'[ \t]+', ' ', html_content)  # Múltiplos espaços viram um
    html_content = html_content.strip()
    
    return html_content


@login_required
def gerar_ata_pdf(request, pk):
    """
    Gerar PDF da ata de reunião com padrão institucional
    """
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, SimpleDocTemplate, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.graphics.shapes import Drawing, Rect, Line
    from reportlab.graphics import renderPDF
    import os
    from django.conf import settings
    
    # Buscar a ata
    try:
        print(f"Tentando gerar PDF para ata ID: {pk}")
        ata = AtaReuniao.objects.get(pk=pk)
        print(f"Ata encontrada: {ata.titulo}")
    except AtaReuniao.DoesNotExist:
        print(f"Ata com ID {pk} não encontrada")
        raise Http404("Ata não encontrada.")
    except Exception as e:
        print(f"Erro ao buscar ata: {e}")
        raise Http404("Erro ao buscar ata")
    
    # Criar PDF
    response = HttpResponse(content_type='application/pdf')
    
    # Nome do arquivo
    nome_arquivo = ata.titulo.replace(' ', '_').replace('/', '_')
    filename = f"ata_{nome_arquivo}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Verificar se é para download ou visualização
    if request.GET.get('download') == '1':
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    else:
        response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    # Criar documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4, 
                           rightMargin=50, leftMargin=50, 
                           topMargin=50, bottomMargin=80)
    story = []
    
    # Estilos personalizados
    styles = getSampleStyleSheet()
    
    # Estilo do título principal
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.black,
        spaceAfter=20,
        spaceBefore=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo do subtítulo
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.black,
        spaceAfter=15,
        spaceBefore=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para seções
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.black,
        spaceAfter=10,
        spaceBefore=15,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=6,
        spaceBefore=3,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=12
    )
    
    # Estilo para metadados
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=4,
        spaceBefore=2,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=10
    )
    
    # Cabeçalho com logo à esquerda e texto à direita
    try:
        import os
        from django.conf import settings
        from reportlab.platypus import Image, Table, TableStyle
        
        # Usar Logo_abmepi.png como primeira opção no cabeçalho
        logo_abmepi_path = get_logo_path('Logo_abmepi.png')
        logo_asejur2_path = get_logo_path('logo2assejur.png')
        logo_asejur_path = get_logo_path('Logo-assejur.png')
        
        logo = None
        if logo_abmepi_path:
            logo = Image(logo_abmepi_path, width=60, height=60)
        elif logo_asejur2_path:
            logo = Image(logo_asejur2_path, width=60, height=60)
        elif logo_asejur_path:
            logo = Image(logo_asejur_path, width=60, height=60)
        
        # Estilo para o texto do cabeçalho (centralizado)
        header_text_style = ParagraphStyle(
            'HeaderTextStyle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.black,
            alignment=TA_CENTER,  # Centralizado
            fontName='Helvetica-Bold',
            leading=16
        )
        
        # Texto do cabeçalho
        header_text = Paragraph("ASSOCIAÇÃO DOS BOMBEIROS E POLICIAIS MILITARES<br/>DO ESTADO DO PIAUÍ", header_text_style)
        
        # Criar tabela para layout do cabeçalho (centralizada na página)
        if logo:
            header_data = [[logo, header_text]]
            header_table = Table(header_data, colWidths=[60, 460])
        else:
            header_data = [[header_text]]
            header_table = Table(header_data, colWidths=[520])
        
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),  # Logo centralizada
            ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # Texto centralizado
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
            ('TOPPADDING', (0, 0), (-1, -1), 0),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        # Centralizar a tabela na página
        header_table.hAlign = 'CENTER'
        story.append(header_table)
        story.append(Spacer(1, 5))
        
    except Exception as e:
        # Fallback: apenas o texto se houver erro
        story.append(Paragraph("ASSOCIAÇÃO DOS BOMBEIROS E POLICIAIS MILITARES DO ESTADO DO PIAUÍ", title_style))
    story.append(Spacer(1, 20))
    
    # Título da Ata (centralizado)
    title_centered_style = ParagraphStyle(
        'TitleCenteredStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.black,
        spaceAfter=20,
        spaceBefore=28.35,  # 1 cm = 28.35 pontos
        alignment=TA_CENTER,  # Centralizado
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph(ata.titulo, title_centered_style))
    story.append(Spacer(1, 20))
    
    # Metadados da Ata - Apresentação limpa
    meta_info = [
        f"<b>Tipo de Reunião:</b> {ata.get_tipo_reuniao_display()}",
        f"<b>Data e Hora:</b> {ata.data_reuniao.strftime('%d/%m/%Y às %H:%M')}",
        f"<b>Local:</b> {ata.local}",
        f"<b>Presidente:</b> {ata.presidente.associado.nome if ata.presidente else 'Não informado'}",
        f"<b>Secretário:</b> {ata.secretario.associado.nome if ata.secretario else 'Não informado'}",
    ]
    
    # Estilo para metadados
    meta_style = ParagraphStyle(
        'MetaStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=8,
        spaceBefore=4,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=14
    )
    
    for info in meta_info:
        story.append(Paragraph(info, meta_style))
    
    story.append(Spacer(1, 20))
    
    # Conteúdo Completo da Ata (do editor avançado)
    if ata.conteudo_completo:
        # Limpar HTML complexo para o PDF
        conteudo_texto = clean_html_for_pdf(ata.conteudo_completo)
        story.append(Paragraph(conteudo_texto, normal_style))
        story.append(Spacer(1, 15))
    else:
        story.append(Paragraph("Nenhum conteúdo foi adicionado à ata.", normal_style))
        story.append(Spacer(1, 15))
    
    # Data e Local (após o texto principal)
    story.append(Spacer(1, 30))
    
    # Mapear meses para português
    meses_pt = {
        'January': 'janeiro', 'February': 'fevereiro', 'March': 'março',
        'April': 'abril', 'May': 'maio', 'June': 'junho',
        'July': 'julho', 'August': 'agosto', 'September': 'setembro',
        'October': 'outubro', 'November': 'novembro', 'December': 'dezembro'
    }
    
    # Usar apenas a cidade do campo local da ata (sem UF)
    cidade = ata.local
    
    # Converter para fuso horário do Brasil
    import pytz
    
    # Garantir que a data está no fuso horário correto
    if timezone.is_aware(ata.data_reuniao):
        data_brasil = ata.data_reuniao.astimezone(pytz.timezone('America/Sao_Paulo'))
    else:
        data_brasil = pytz.timezone('America/Sao_Paulo').localize(ata.data_reuniao)
    
    mes_pt = meses_pt.get(data_brasil.strftime('%B'), data_brasil.strftime('%B'))
    
    story.append(Paragraph(f"{cidade}, {data_brasil.strftime('%d')} de {mes_pt} de {data_brasil.strftime('%Y')}", 
                          ParagraphStyle('DataStyle', parent=styles['Normal'], fontSize=11, 
                                       alignment=TA_CENTER, fontName='Helvetica-Bold')))
    
    # Assinaturas dos Membros da Diretoria (centralizadas)
    story.append(Spacer(1, 30))
    story.append(Paragraph("Membros da Diretoria", ParagraphStyle('DiretoriaTitle', parent=styles['Heading3'], 
                                                                  fontSize=12, alignment=TA_CENTER, 
                                                                  fontName='Helvetica-Bold')))
    story.append(Spacer(1, 15))
    
    # Buscar membros da diretoria
    from diretoria.models import MembroDiretoria
    membros_diretoria = MembroDiretoria.objects.filter(ativo=True).select_related('associado', 'cargo')
    
    for membro in membros_diretoria:
        # Linha para assinatura centralizada (acima do nome)
        story.append(Paragraph("_" * 60, 
                              ParagraphStyle('LinhaAssinatura', parent=styles['Normal'], fontSize=10, 
                                           alignment=TA_CENTER, fontName='Helvetica')))
        
        # Nome centralizado
        story.append(Paragraph(f"{membro.associado.nome}", 
                              ParagraphStyle('MembroNome', parent=styles['Normal'], fontSize=11, 
                                           alignment=TA_CENTER, fontName='Helvetica-Bold')))
        
        # Cargo centralizado
        story.append(Paragraph(f"{membro.cargo.nome}", 
                              ParagraphStyle('MembroCargo', parent=styles['Normal'], fontSize=10, 
                                           alignment=TA_CENTER, fontName='Helvetica')))
        story.append(Spacer(1, 20))
    
    # Lista numerada dos Associados Presentes (não membros da diretoria)
    if ata.associados_presentes.exists():
        story.append(Spacer(1, 20))
        story.append(Paragraph("Associados Presentes", ParagraphStyle('PresentesTitle', parent=styles['Heading3'], 
                                                                      fontSize=12, alignment=TA_CENTER, 
                                                                      fontName='Helvetica-Bold')))
        story.append(Spacer(1, 15))
        
        # Criar tabela para associados presentes
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors
        
        # Cabeçalho da tabela
        associados_data = [["Nº", "Nome Completo", "CPF", "Assinatura"]]
        
        # Adicionar dados dos associados
        for i, associado in enumerate(ata.associados_presentes.all(), 1):
            # Criptografar CPF (mostrar apenas os primeiros 3 e últimos 2 dígitos)
            cpf = str(associado.cpf).replace('.', '').replace('-', '')  # Remove formatação
            if len(cpf) == 11:
                cpf_criptografado = f"{cpf[:3]}.***.***-{cpf[-2:]}"
            else:
                cpf_criptografado = "***.***.***-**"  # CPF inválido
            
            # Adicionar linha na tabela
            associados_data.append([
                str(i),
                associado.nome,
                cpf_criptografado,
                "_" * 40  # Linha para assinatura reduzida
            ])
        
        # Criar tabela
        associados_table = Table(associados_data, colWidths=[30, 200, 100, 180])
        
        # Estilo da tabela
        associados_table.setStyle(TableStyle([
            # Cabeçalho
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            
            # Dados
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),  # Nome alinhado à esquerda
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Número centralizado
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # CPF centralizado
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Assinatura centralizada
            
            # Valign
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(associados_table)
        story.append(Spacer(1, 20))
    
    # Função para criar rodapé
    def create_footer(canvas, doc):
        canvas.saveState()
        
        # Texto do rodapé
        footer_text = """
        Reconhecimento de Utilidade Pública Estadual Lei nº 5.614 28/11/06 |
        Reconhecimento de Utilidade Pública Municipal Lei nº 3.634 14/05/07 |
        Fone: 86 3085-1722 | E-mail: abmepi@gmail.com |
        Endereço: Rua Coelho Rodrigues, 2242, Centro Sul, CEP: 64.000-080, Teresina – PI
        """
        
        # Posicionar rodapé na parte inferior da página
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.black)
        
        # Desenhar linha separadora
        canvas.setStrokeColor(colors.grey)
        canvas.setLineWidth(0.5)
        canvas.line(0, 70, 612, 70)
        
        # Adicionar logo da ABMEPI
        try:
            import os
            from django.conf import settings
            logo_path = get_logo_path('Logo_abmepi.png')
            if logo_path:
                canvas.drawImage(logo_path, 20, 20, width=40, height=40, preserveAspectRatio=True)
                
                # Adicionar dados de geração do documento
                canvas.setFont('Helvetica', 6)
                canvas.setFillColor(colors.black)
                # Usar fuso horário do Brasil para o horário de geração
                import pytz
                agora_brasil = timezone.now().astimezone(pytz.timezone('America/Sao_Paulo'))
                canvas.drawString(20, 10, f"Documento gerado em {agora_brasil.strftime('%d/%m/%Y às %H:%M')}")
                canvas.drawString(20, 4, "ABMEPI - Sistema de Gestão")
        except:
            pass
        
        # Dividir o texto em linhas
        lines = footer_text.strip().split('|')
        y_position = 50
        
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.black)
        
        for line in lines:
            line = line.strip()
            if line:
                canvas.drawRightString(580, y_position, line)
                y_position -= 10
        
        canvas.restoreState()
    
    # Construir PDF
    doc.build(story, onFirstPage=create_footer, onLaterPages=create_footer)
    
    return response
