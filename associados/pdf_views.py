
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.utils import timezone
from .models import Associado, PreCadastroAssociado
import os


def get_logo_path(filename):
    """
    Retorna o caminho correto para a logo, tentando primeiro em static (desenvolvimento)
    e depois em staticfiles (produção)
    """
    from django.conf import settings
    
    # Tentar primeiro no diretório static (desenvolvimento)
    logo_path = os.path.join(settings.BASE_DIR, 'static', filename)
    if os.path.exists(logo_path):
        return logo_path
    
    # Se não existir, tentar no staticfiles (produção)
    logo_path = os.path.join(settings.STATIC_ROOT, filename)
    if os.path.exists(logo_path):
        return logo_path
    
    return None


def criptografar_cpf(cpf):
    """
    Criptografa o CPF mantendo apenas os primeiros 3 e últimos 2 dígitos
    """
    if not cpf or len(cpf) < 11:
        return cpf
    
    # Remove pontos, traços e espaços
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    
    if len(cpf_limpo) == 11:
        # Formato: XXX.XXX.XXX-XX
        cpf_criptografado = f"{cpf_limpo[:3]}.XXX.XXX-{cpf_limpo[-2:]}"
    else:
        cpf_criptografado = cpf
    
    return cpf_criptografado

    

@login_required
def gerar_declaracao_associados_pdf(request):
    """
    Gerar PDF de declaração de associados ou ficha de cadastro de pré-cadastro
    """
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, SimpleDocTemplate, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.graphics.shapes import Drawing, Rect, Line
    from reportlab.graphics import renderPDF
    
    # Verificar se é para um pré-cadastro específico
    pre_cadastro_id = request.GET.get('pre_cadastro_id')
    
    if pre_cadastro_id:
        # Gerar ficha de cadastro para um pré-cadastro específico
        try:
            pre_cadastro = PreCadastroAssociado.objects.get(pk=pre_cadastro_id)
            return gerar_ficha_cadastro_pdf(request, pre_cadastro)
        except PreCadastroAssociado.DoesNotExist:
            from django.http import Http404
            raise Http404("Pré-cadastro não encontrado.")
    
    # Verificar se é para um associado específico ou lista geral
    associado_id = request.GET.get('associado_id')
    
    if associado_id:
        # Gerar declaração para um associado específico
        try:
            associado = Associado.objects.get(pk=associado_id)
            associados = [associado]
        except Associado.DoesNotExist:
            from django.http import Http404
            raise Http404("Associado não encontrado.")
    else:
        # Lista geral de associados
        associados = Associado.objects.filter(ativo=True).order_by('nome')
    
    # Criar PDF
    response = HttpResponse(content_type='application/pdf')
    
    # Nome do arquivo
    if associado_id:
        nome_arquivo = associado.nome.replace(' ', '_').replace('/', '_')
        filename = f"declaracao_{nome_arquivo}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    else:
        filename = f"declaracao_associados_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    # Verificar se é para download ou visualização
    if request.GET.get('download') == '1':
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    else:
        response['Content-Disposition'] = f'inline; filename="{filename}"'
    
    # Criar documento PDF
    doc = SimpleDocTemplate(response, pagesize=A4, 
                           rightMargin=72, leftMargin=72, 
                           topMargin=18, bottomMargin=100)
    story = []
    
    # Estilos personalizados
    styles = getSampleStyleSheet()
    
    # Estilo do título
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.black,
        spaceAfter=20,
        spaceBefore=56.7,  # 2 cm = 56.7 pontos
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo do texto normal
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.black,
        spaceAfter=6,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    
    # Adicionar cabeçalho com logo da ASEJUR
    try:
        import os
        from django.conf import settings
        from reportlab.platypus import Image
        
        # Usar logo2assejur.png como primeira opção no cabeçalho
        logo_asejur2_path = get_logo_path('logo2assejur.png')
        logo_asejur_path = get_logo_path('Logo-assejur.png')
        logo_abmepi_path = get_logo_path('Logo_abmepi.png')
        
        if logo_asejur2_path:
            logo = Image(logo_asejur2_path, width=245.51, height=68.32)
        elif logo_asejur_path:
            logo = Image(logo_asejur_path, width=245.51, height=68.32)
        elif logo_abmepi_path:
            logo = Image(logo_abmepi_path, width=245.51, height=68.32)
        else:
            logo = None
            
        if logo:
            # Centralizar o logo
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 10))
        else:
            story.append(Spacer(1, 30))
    except Exception as e:
        # Em caso de erro, pula o cabeçalho
        story.append(Spacer(1, 30))
    

    

    
    # Conteúdo da declaração
    if associados:
        for associado in associados:
            # Título da declaração
            story.append(Paragraph("DECLARAÇÃO DE CADASTRO ASSOCIATIVO", title_style))
            story.append(Spacer(1, 30))
            
            # Texto da declaração com dados destacados e CPF criptografado
            cpf_criptografado = criptografar_cpf(associado.cpf)
            declaracao_texto = f"""
            O presidente da Associação dos Bombeiros Militares do Estado do Piauí - ABMEPI, DECLARA para os devidos fins que o <b>{associado.get_posto_graduacao_display()}</b> <b>{associado.nome}</b>, identificado pela matrícula funcional nº {associado.matricula_militar or 'N/A'}, CPF nº {cpf_criptografado} apresenta-se atualmente cadastrado e filiado no quadro de <b>{associado.get_tipo_socio_display()}</b> desta entidade, assim como, apresenta-se adimplente com suas obrigações prestacionais, portanto em gozo pleno dos benefícios associativos.
            """
            
            # Estilo para o texto da declaração
            declaracao_style = ParagraphStyle(
                'DeclaracaoStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.black,  # Fonte preta
                spaceAfter=20,
                spaceBefore=20,
                alignment=TA_JUSTIFY,
                fontName='Helvetica',
                leading=17.4,  # 12 * 1.45 = 17.4 (espaçamento 1,45 - aumentado mais 1,0mm)
                leftIndent=0,
                rightIndent=0,
                firstLineIndent=0
            )
            
            story.append(Paragraph(declaracao_texto, declaracao_style))
            
            # Dependentes (se houver)
            dependentes = associado.dependentes.all()
            if dependentes.exists():
                # Estilo para título dos dependentes
                dependentes_title_style = ParagraphStyle(
                    'DependentesTitleStyle',
                    parent=styles['Heading3'],
                    fontSize=14,
                    textColor=colors.black,
                    spaceAfter=10,
                    spaceBefore=20,
                    alignment=TA_LEFT,
                    fontName='Helvetica-Bold'
                )
                
                story.append(Paragraph("DEPENDENTES:", dependentes_title_style))
                
                # Lista de dependentes
                for dependente in dependentes:
                    dependente_texto = f"• {dependente.nome} - {dependente.get_parentesco_display()}"
                    story.append(Paragraph(dependente_texto, normal_style))
                
                story.append(Spacer(1, 20))
            
            # Data e local
            data_local = f"""
            Teresina - PI, {timezone.now().strftime('%d de %B de %Y')}
            """
            
            data_style = ParagraphStyle(
                'DataStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.black,
                spaceAfter=20,
                spaceBefore=20,
                alignment=TA_CENTER,
                fontName='Helvetica'
            )
            
            story.append(Paragraph(data_local, data_style))
            
            # Assinatura
            assinatura_texto = """
            <br/><br/><br/>
            _________________________________<br/>
            Presidente da ABMEPI
            """
            
            assinatura_style = ParagraphStyle(
                'AssinaturaStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.black,
                spaceAfter=20,
                spaceBefore=20,
                alignment=TA_CENTER,
                fontName='Helvetica'
            )
            
            story.append(Paragraph(assinatura_texto, assinatura_style))
            
            # Quebra de página se não for o último associado
            if associado != associados[-1]:
                story.append(PageBreak())
    
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
                canvas.drawString(20, 10, f"Documento gerado em {timezone.now().strftime('%d/%m/%Y às %H:%M')}")
                canvas.drawString(20, 4, "ABMEPI")
        except:
            pass
        
        # Dividir o texto em linhas
        lines = footer_text.strip().split('|')
        y_position = 50  # Subiu de 30 para 50
        
        # Garantir que o texto das informações institucionais seja preto
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.black)  # Texto preto
        
        for line in lines:
            line = line.strip()
            if line:
                # Todas as linhas alinhadas à direita
                canvas.drawRightString(580, y_position, line)
                y_position -= 10
        
        canvas.restoreState()
    
    # Construir PDF com rodapé em todas as páginas
    doc.build(story, onFirstPage=create_footer, onLaterPages=create_footer)
    
    return response


@login_required
def gerar_requerimento_inscricao_pdf(request):
    """
    Gerar PDF do requerimento oficial de inscrição na associação
    """
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, SimpleDocTemplate, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.graphics.shapes import Drawing, Rect, Line
    from reportlab.graphics import renderPDF
    
    # Verificar se é para um pré-cadastro específico
    pre_cadastro_id = request.GET.get('pre_cadastro_id')
    
    if not pre_cadastro_id:
        from django.http import Http404
        raise Http404("ID do pré-cadastro não fornecido.")
    
    try:
        pre_cadastro = PreCadastroAssociado.objects.get(pk=pre_cadastro_id)
    except PreCadastroAssociado.DoesNotExist:
        from django.http import Http404
        raise Http404("Pré-cadastro não encontrado.")
    
    return gerar_requerimento_inscricao_pdf_content(request, pre_cadastro)


def gerar_requerimento_inscricao_pdf_content(request, pre_cadastro):
    """
    Gerar PDF do requerimento oficial de inscrição na associação
    """
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, SimpleDocTemplate, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.graphics.shapes import Drawing, Rect, Line
    from reportlab.graphics import renderPDF
    
    # Criar PDF
    response = HttpResponse(content_type='application/pdf')
    
    # Nome do arquivo
    nome_arquivo = pre_cadastro.nome.replace(' ', '_').replace('/', '_')
    filename = f"requerimento_inscricao_{nome_arquivo}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
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
        fontSize=16,
        textColor=colors.black,
        spaceAfter=20,
        spaceBefore=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo para texto normal
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=3,
        spaceBefore=0,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=14
    )
    
    # Estilo para texto em maiúsculas
    uppercase_style = ParagraphStyle(
        'UppercaseStyle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.black,
        spaceAfter=6,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold'
    )
    
    # Adicionar cabeçalho com logo da ASEJUR
    try:
        import os
        from django.conf import settings
        from reportlab.platypus import Image
        
        # Usar logo2assejur.png como primeira opção no cabeçalho
        logo_asejur2_path = get_logo_path('logo2assejur.png')
        logo_asejur_path = get_logo_path('Logo-assejur.png')
        logo_abmepi_path = get_logo_path('Logo_abmepi.png')
        
        if logo_asejur2_path:
            logo = Image(logo_asejur2_path, width=245.51, height=68.32)
        elif logo_asejur_path:
            logo = Image(logo_asejur_path, width=245.51, height=68.32)
        elif logo_abmepi_path:
            logo = Image(logo_abmepi_path, width=245.51, height=68.32)
        else:
            logo = None
            
        if logo:
            # Centralizar o logo
            logo.hAlign = 'CENTER'
            story.append(logo)
            story.append(Spacer(1, 10))
    except Exception as e:
        pass
    
    # Cabeçalho do documento
    story.append(Paragraph("ASSOCIAÇÃO BENEFICENTE DOS MILITARES ESTADUAIS DO PIAUÍ", title_style))
    story.append(Paragraph("ABMEPI", title_style))
    story.append(Spacer(1, 20))
    
    # Título do documento
    story.append(Paragraph("REQUERIMENTO DE INSCRIÇÃO", title_style))
    story.append(Spacer(1, 20))
    
    # Informações da situação e corporação
    situacao_text = ""
    if pre_cadastro.situacao == 'ativo':
        situacao_text = "[X] Ativa [ ] Reserva Remunerada [ ] Reformado"
    elif pre_cadastro.situacao == 'reserva':
        situacao_text = "[ ] Ativa [X] Reserva Remunerada [ ] Reformado"
    elif pre_cadastro.situacao == 'reformado':
        situacao_text = "[ ] Ativa [ ] Reserva Remunerada [X] Reformado"
    else:
        situacao_text = "[ ] Ativa [ ] Reserva Remunerada [ ] Reformado"
    
    corporacao_text = ""
    if pre_cadastro.tipo_profissao == 'policial':
        corporacao_text = "[X] Polícia Militar [ ] Bombeiro Militar"
    elif pre_cadastro.tipo_profissao == 'bombeiro':
        corporacao_text = "[ ] Polícia Militar [X] Bombeiro Militar"
    else:
        corporacao_text = "[ ] Polícia Militar [ ] Bombeiro Militar"
    
    story.append(Paragraph(f"SITUAÇÃO: {situacao_text}", normal_style))
    story.append(Paragraph(f"Corporação: {corporacao_text}", normal_style))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("PREENCHER COM LETRA DE FORMA", uppercase_style))
    story.append(Spacer(1, 15))
    
    # Processar naturalidade
    if pre_cadastro.naturalidade:
        if ',' in pre_cadastro.naturalidade:
            cidade_natural = pre_cadastro.naturalidade.split(',')[0].strip().upper()
            uf_natural = pre_cadastro.naturalidade.split(',')[1].strip().upper()
        else:
            cidade_natural = pre_cadastro.naturalidade.upper()
            uf_natural = pre_cadastro.estado.upper()
    else:
        cidade_natural = '_____________________________'
        uf_natural = '______'
    
    # Texto do requerimento formatado em linhas separadas
    story.append(Paragraph(f"Requerente: <b>{pre_cadastro.nome.upper()}</b>,", normal_style))
    story.append(Paragraph(f"nacionalidade: brasileiro(a), natural do município de: <b>{cidade_natural}</b>,", normal_style))
    story.append(Paragraph(f"UF: <b>{uf_natural}</b>, estado civil: <b>{pre_cadastro.get_estado_civil_display().upper()}</b>,", normal_style))
    story.append(Paragraph(f"servidor(a) público(a) estadual, matrícula funcional nº. <b>{pre_cadastro.matricula or '_____________________________'}</b>,", normal_style))
    story.append(Paragraph(f"lotado no cargo de: <b>{pre_cadastro.posto_graduacao.upper() if pre_cadastro.posto_graduacao else '_____________________________'}</b>,", normal_style))
    story.append(Paragraph(f"portador do [ ] RGPM [ ] RGBM [ ] GIP: <b>{pre_cadastro.rg}</b> e CPF: <b>{pre_cadastro.cpf}</b>,", normal_style))
    story.append(Paragraph(f"filho de <b>{pre_cadastro.nome_pai.upper() if pre_cadastro.nome_pai else '_____________________________'}</b> e", normal_style))
    story.append(Paragraph(f"<b>{pre_cadastro.nome_mae.upper() if pre_cadastro.nome_mae else '_____________________________'}</b>,", normal_style))
    story.append(Paragraph(f"residente e domiciliado na <b>{pre_cadastro.rua.upper()}, {pre_cadastro.numero}{', ' + pre_cadastro.complemento.upper() if pre_cadastro.complemento else ''}</b>,", normal_style))
    story.append(Paragraph(f"cidade de: <b>{pre_cadastro.cidade.upper()}</b> UF: <b>{pre_cadastro.estado.upper()}</b>,", normal_style))
    story.append(Paragraph(f"tendo o endereço eletrônico (email): <b>{pre_cadastro.email or '_____________________________'}</b>,", normal_style))
    story.append(Paragraph(f"telefone(s): <b>{pre_cadastro.telefone or pre_cadastro.celular or '_____________________________'}</b> e", normal_style))
    story.append(Paragraph("com a seguinte relação de dependentes:", normal_style))
    story.append(Spacer(1, 15))
    
    # Seção de dependentes
    story.append(Paragraph("1. [ ] Não possuo dependentes", normal_style))
    story.append(Spacer(1, 25))
    
    # Texto final do requerimento
    story.append(Paragraph("Venho requerer a MINHA INSCRIÇÃO junto a esta associação com o intuito", normal_style))
    story.append(Paragraph("de fazer parte do corpo associativo, por meio dessa singela colaboração,", normal_style))
    story.append(Paragraph("para ajudar na defesa dos direitos e prerrogativas de toda a nossa", normal_style))
    story.append(Paragraph("Categoria militar, de acordo com os termos abaixo.", normal_style))
    story.append(Spacer(1, 30))
    
    # Assinatura
    story.append(Paragraph("_________________________________", normal_style))
    story.append(Paragraph("Assinatura do Requerente", normal_style))
    story.append(Spacer(1, 20))
    
    # Data e local
    data_atual = timezone.now().strftime('%d/%m/%Y')
    story.append(Paragraph(f"Teresina, {data_atual}", normal_style))
    
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
                canvas.drawString(20, 10, f"Documento gerado em {timezone.now().strftime('%d/%m/%Y às %H:%M')}")
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
    
    # Construir PDF com rodapé
    doc.build(story, onFirstPage=create_footer, onLaterPages=create_footer)
    
    return response


def gerar_ficha_cadastro_pdf(request, pre_cadastro):
    """
    Gerar PDF da ficha de cadastro associativo para pré-cadastro - VERSÃO MELHORADA
    """
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import Table, TableStyle, Spacer, Paragraph, SimpleDocTemplate, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
    from reportlab.lib.pagesizes import A4
    from reportlab.graphics.shapes import Drawing, Rect, Line
    from reportlab.graphics import renderPDF
    
    # Criar PDF
    response = HttpResponse(content_type='application/pdf')
    
    # Nome do arquivo
    from django.utils import timezone
    nome_arquivo = pre_cadastro.nome.replace(' ', '_').replace('/', '_')
    filename = f"ficha_cadastro_{nome_arquivo}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
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
        spaceBefore=15,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Estilo do texto normal
    normal_style = ParagraphStyle(
        'NormalText',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=8,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=14
    )
    
    # Estilo para campos destacados
    field_style = ParagraphStyle(
        'FieldStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=8,
        alignment=TA_LEFT,
        fontName='Helvetica-Bold',
        leading=14
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
        fontName='Helvetica-Bold',
        borderWidth=1,
        borderColor=colors.black,
        borderPadding=5,
        backColor=colors.lightgrey
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
    
    # Título da ficha (centralizado)
    title_centered_style = ParagraphStyle(
        'TitleCenteredStyle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.black,
        spaceAfter=20,
        spaceBefore=28.35,  # 1 cm = 28.35 pontos (reduzido de 2 cm)
        alignment=TA_CENTER,  # Centralizado
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("FICHA DE CADASTRO ASSOCIATIVO", title_centered_style))
    story.append(Spacer(1, 10))
    
    
    # Situação e Corporação
    situacao_texto = "<b>SITUAÇÃO:</b> "
    if pre_cadastro.situacao == 'ativo':
        situacao_texto += "[X] Ativa [ ] Reserva Remunerada [ ] Reformado"
    elif pre_cadastro.situacao == 'reserva':
        situacao_texto += "[ ] Ativa [X] Reserva Remunerada [ ] Reformado"
    elif pre_cadastro.situacao == 'reformado':
        situacao_texto += "[ ] Ativa [ ] Reserva Remunerada [X] Reformado"
    else:
        situacao_texto += "[ ] Ativa [ ] Reserva Remunerada [ ] Reformado"
    
    story.append(Paragraph(situacao_texto, field_style))
    
    corporacao_texto = "<b>Corporação:</b> "
    if pre_cadastro.tipo_profissao == 'bombeiro':
        corporacao_texto += "[ ] Polícia Militar [X] Bombeiro Militar"
    elif pre_cadastro.tipo_profissao == 'policial':
        corporacao_texto += "[X] Polícia Militar [ ] Bombeiro Militar"
    else:
        corporacao_texto += "[ ] Polícia Militar [ ] Bombeiro Militar"
    
    story.append(Paragraph(corporacao_texto, field_style))
    story.append(Spacer(1, 15))
    
    
    # Estilo para o texto do requerimento (justificado, sem quebras)
    requerimento_style = ParagraphStyle(
        'RequerimentoStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=15,
        spaceBefore=10,
        alignment=TA_JUSTIFY,  # Texto justificado
        fontName='Helvetica',
        leading=13,  # Espaçamento entre linhas
        leftIndent=0,
        rightIndent=0,
        firstLineIndent=0
    )
    
    # Marcar o tipo de documento correto
    tipo_doc_rgpm = "[X]" if pre_cadastro.tipo_documento == 'rgpm' else "[ ]"
    tipo_doc_rgbm = "[X]" if pre_cadastro.tipo_documento == 'rgbm' else "[ ]"
    tipo_doc_gip = "[X]" if pre_cadastro.tipo_documento == 'gip' else "[ ]"
    
    # Formulário de requerimento (texto contínuo sem quebras até dependentes)
    requerimento_texto = f"""<b>Requerente:</b> {pre_cadastro.nome or '_________________________________________'}, nacionalidade: brasileiro (a), natural do município de: {pre_cadastro.naturalidade or '_________________________________'} UF: {pre_cadastro.estado or '______'}, estado civil: {pre_cadastro.get_estado_civil_display() or '________________________'}, servidor (a) público (a) estadual, matrícula funcional nº. {pre_cadastro.matricula or '_____________________________'}, lotado no cargo de: {pre_cadastro.posto_graduacao or '_____________________________________________'}, portador do {tipo_doc_rgpm} RGPM {tipo_doc_rgbm} RGBM {tipo_doc_gip} GIP: {pre_cadastro.rg or '____________________________'} e CPF: {pre_cadastro.cpf or '___________________________________'}, filho de {pre_cadastro.nome_pai or '__________________________________________________________________________________'} e {pre_cadastro.nome_mae or '____________________________________________________________________________'}, residente e domiciliado na {pre_cadastro.rua or '______________________________________________________________________'} cidade de: {pre_cadastro.cidade or '________________________________'} UF: {pre_cadastro.estado or '______'}, tendo o endereço eletrônico (email): {pre_cadastro.email or '_________________________________________________________________'} telefone (s): {pre_cadastro.telefone or '_________________________________________________________'} e com a seguinte relação de dependentes:"""
    
    story.append(Paragraph(requerimento_texto, requerimento_style))
    
    # Listar dependentes cadastrados
    dependentes = pre_cadastro.dependentes.all() if hasattr(pre_cadastro, 'dependentes') else []
    
    if dependentes.exists():
        for i, dependente in enumerate(dependentes, 1):
            dependente_texto = f"{i}. Nome: {dependente.nome or '___________________________________________________'} parentesco: {dependente.get_parentesco_display() if hasattr(dependente, 'get_parentesco_display') else '____________'}"
            story.append(Paragraph(dependente_texto, requerimento_style))
    else:
        # Se não houver dependentes, mostrar linha em branco
        story.append(Paragraph("1. Nome: ___________________________________________________ parentesco: ____________", requerimento_style))
    story.append(Spacer(1, 20))
    
    # Seção: Observações
    if pre_cadastro.observacoes:
        story.append(Paragraph("OBSERVAÇÕES", section_style))
        story.append(Paragraph(pre_cadastro.observacoes, normal_style))
    story.append(Spacer(1, 15))
    
    
    # Texto de declaração
    declaracao_texto = """
    <b>DECLARAÇÃO:</b><br/><br/>
    Declaro que as informações prestadas nesta ficha de cadastro são verdadeiras e estou ciente de que a falsidade das mesmas pode acarretar a exclusão do quadro associativo, conforme previsto no estatuto da ABMEPI.<br/><br/>
    Venho requerer a MINHA INSCRIÇÃO junto a esta associação com o intuito de fazer parte do corpo associativo, por meio dessa singela colaboração, para ajudar na defesa dos direitos e prerrogativas de toda a nossa Categoria militar.
    """
    
    story.append(Paragraph(declaracao_texto, normal_style))
    
    # Quebra de página para os termos ficarem na segunda página
    from reportlab.platypus import PageBreak
    story.append(PageBreak())
    
    # Título do Termo de Compromisso
    termo_title_style = ParagraphStyle(
        'TermoTitleStyle',
        parent=styles['Heading1'],
        fontSize=12,
        textColor=colors.black,
        spaceAfter=3,
        spaceBefore=0,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("TERMO DE COMPROMISSO", termo_title_style))
    story.append(Spacer(1, 5))
    
    # Estilo para o texto do termo
    termo_style = ParagraphStyle(
        'TermoStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=8,
        spaceBefore=2,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=11,
        leftIndent=0,
        rightIndent=0,
        firstLineIndent=0
    )
    
    # Texto do Termo de Compromisso
    termo_texto = """
    <b>1.</b> O associado declara que tem ciência quanto a todas as relações jurídicas referentes à
    presente adesão, a teor das normas regulamentadas no Estatuto da Associação dos Bombeiros e Policiais
    Militares do Estado do Piauí - ABMEPI, de forma que, compromete-se, a partir da assinatura deste termo em
    atender os seguintes dispositivos normativos:<br/><br/>
    
    <b>1.1.</b> O Associado qualificado autoriza a averbação em folha de pagamento ou execução por
    meio de boleto bancário, respectivamente, de desconto direto consignado ou cobrança mensal da importância
    correspondente a 1,2% do subsídio do Soldado PM/Soldado BM referente a taxa de contribuição associativa,
    assim como, qualquer outro desconto referente a qualquer prestação de serviço ou benefício remunerado
    realizados junto a esta entidade, desde que devidamente comprovado através de Contrato, Recibo ou
    Comprovante, específicos.<br/><br/>
    
    <b>1.2.</b> O sócio contribuinte militar ou civil, a partir do ato de sua filiação, sujeitar-se-á a carência de
    60 (sessenta) dias quanto ao benefício da prestação de serviço advocatício pela assessoria jurídica.<br/><br/>
    
    <b>1.2.1.</b> Os casos excepcionais serão deliberados pela Diretoria Executiva.<br/><br/>
    
    <b>1.3.</b> Nos casos de cadastro associativo de "filiação temporária" ou "filiação permanente" em
    que o sócio já ingresse no quadro associativo com demanda judicial requerida, este fica obrigado a pagar taxa
    de "uso de serviços administrativo-jurídicos" que corresponderá ao valor acumulado da atual taxa de
    contribuição associativa correspondente ao período de 24 (vinte e quatro) meses.<br/><br/>
    
    <b>1.3.1.</b> Em casos excepcionais o Diretor Presidente deliberará sobre desconto de até 40% na
    referida taxa.<br/><br/>
    
    <b>1.3.2.</b> Nos casos de filiação temporária e que visem apenas o "uso de serviços administrativo-
    jurídicos" em lapso temporal pré-determinado no cadastro associativo, a partir da expiração do lapso temporal
    previamente estabelecido, a ABMEPI isentar-se-á de qualquer responsabilidade quanto a representação
    postulatória de eventual demanda judicial que prossiga em trâmite após o prazo de vigência da representação
    associativa.<br/><br/>
    
    <b>1.3.3.</b> Nos casos de desfiliação do quadro associativo, a ABMEPI tornar-se-á imediatamente isenta
    de qualquer obrigação quanto a prestação de serviços ou oferta de benefícios eventualmente disponibilizados
    pela entidade no ato de vigência do cadastro associativo.<br/><br/>
    
    <b>1.4.</b> O valor contratado neste termo referente à taxa de contribuição associativa poderá sofrer
    alteração a título de atualização, conforme deliberação em Assembleia Geral de Sócios, conforme previsão
    estatutária.<br/><br/>
    
    <b>Responsabilizo-me pela exatidão das informações prestadas, em vista dos originais dos
    documentes apresentados por este proponente, bem como, pela legitimidade de sua assinatura.</b>
    """
    
    story.append(Paragraph(termo_texto, termo_style))
    story.append(Spacer(1, 15))
    
    # Título do Termo de Autorização
    autorizacao_title_style = ParagraphStyle(
        'AutorizacaoTitleStyle',
        parent=styles['Heading1'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=3,
        spaceBefore=5,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("TERMO DE AUTORIZAÇÃO PARA REPRESENTAÇÃO JUDICIAL E EXTRAJUDICIAL", autorizacao_title_style))
    story.append(Spacer(1, 3))
    
    # Estilo para o texto da autorização
    autorizacao_style = ParagraphStyle(
        'AutorizacaoStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=8,
        spaceBefore=2,
        alignment=TA_JUSTIFY,
        fontName='Helvetica',
        leading=11,
        leftIndent=0,
        rightIndent=0,
        firstLineIndent=0
    )
    
    # Texto do Termo de Autorização
    autorizacao_texto = """
    Este signatário anterior qualificado OUTORGA e AUTORIZA ao Presidente da Associação dos
    Bombeiros e Policiais Militares do Estado do Piauí – ABMEPI, inscrita no CNPJ/MF: 07.642.658/0001-46, por
    meio da Assessoria Jurídica da entidade, PROCEDER representação administrativa, judicial e extrajudicial,
    inclusive substituição no pólo ativo no ajuizamento de ações de conhecimento e mandamentais, visando a
    defesa de direitos individuais relacionados aos interesses pessoais deste signatário, assim como, quanto a
    correspondente defesa de interesses e dos direitos individuais, coletivos e difusos da classe militar no âmbito
    do Estado do Piauí.
    """
    
    story.append(Paragraph(autorizacao_texto, autorizacao_style))
    story.append(Spacer(1, 15))
    
    # Data e assinaturas
    data_assinatura_style = ParagraphStyle(
        'DataAssinaturaStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=15,
        spaceBefore=8,
        alignment=TA_CENTER,
        fontName='Helvetica',
        leading=11
    )
    
    # Obter data atual por extenso
    from datetime import datetime
    from django.utils import timezone
    
    data_atual = timezone.now()
    meses = [
        'janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho',
        'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'
    ]
    
    dia = data_atual.day
    mes = meses[data_atual.month - 1]
    ano = data_atual.year
    
    data_extenso = f"Teresina-PI, {dia} de {mes} de {ano}."
    
    story.append(Paragraph(data_extenso, data_assinatura_style))
    story.append(Spacer(1, 20))
    
    # Assinaturas
    assinaturas_style = ParagraphStyle(
        'AssinaturasStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.black,
        spaceAfter=8,
        spaceBefore=8,
        alignment=TA_CENTER,
        fontName='Helvetica',
        leading=11
    )
    
    # Assinaturas lado a lado
    from reportlab.platypus import Table, TableStyle
    
    assinaturas_data = [
        ["_______________________________________", "___________________________________________"],
        [f"{pre_cadastro.nome}", "Presidente da ABMEPI"]
    ]
    
    assinaturas_table = Table(assinaturas_data, colWidths=[250, 250])
    assinaturas_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    
    story.append(assinaturas_table)
    story.append(Spacer(1, 15))
    
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
                canvas.drawString(20, 10, f"Documento gerado em {timezone.now().strftime('%d/%m/%Y às %H:%M')}")
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
    
    # Construir PDF com rodapé
    doc.build(story, onFirstPage=create_footer, onLaterPages=create_footer)
    
    return response