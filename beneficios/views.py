from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import EmpresaParceira, Convenio, Beneficio, CategoriaBeneficio
from .forms import (
    EmpresaParceiraForm, ConvenioForm, BeneficioForm, CategoriaBeneficioForm,
    BeneficioSolicitacaoForm, ConvenioBuscaForm
)


@login_required
def teste(request):
    """Página de teste para verificar se o módulo está funcionando"""
    return render(request, 'beneficios/teste.html')

@login_required
def dashboard(request):
    """Dashboard principal do módulo de benefícios"""
    # Estatísticas gerais
    total_empresas = EmpresaParceira.objects.filter(ativo=True).count()
    total_convenios = Convenio.objects.filter(ativo=True).count()
    total_beneficios = Beneficio.objects.count()
    beneficios_pendentes = Beneficio.objects.filter(status='pendente').count()
    
    # Convênios por categoria
    convenios_por_categoria = Convenio.objects.filter(ativo=True).values('categoria').annotate(
        total=Count('id')
    ).order_by('-total')[:5]
    
    # Benefícios recentes
    beneficios_recentes = Beneficio.objects.select_related('associado', 'convenio').order_by('-data_solicitacao')[:10]
    
    # Convênios expirando em breve
    from datetime import date, timedelta
    data_limite = date.today() + timedelta(days=30)
    convenios_expirando = Convenio.objects.filter(
        ativo=True,
        data_fim__lte=data_limite,
        data_fim__gte=date.today()
    ).order_by('data_fim')[:5]
    
    context = {
        'total_empresas': total_empresas,
        'total_convenios': total_convenios,
        'total_beneficios': total_beneficios,
        'beneficios_pendentes': beneficios_pendentes,
        'convenios_por_categoria': convenios_por_categoria,
        'beneficios_recentes': beneficios_recentes,
        'convenios_expirando': convenios_expirando,
    }
    
    return render(request, 'beneficios/dashboard.html', context)


# Views para Empresas Parceiras
@login_required
def empresa_list(request):
    """Lista de empresas parceiras"""
    empresas = EmpresaParceira.objects.all()
    
    # Filtros
    estado = request.GET.get('estado')
    ativo = request.GET.get('ativo')
    search = request.GET.get('search')
    
    if estado:
        empresas = empresas.filter(estado=estado)
    if ativo is not None:
        empresas = empresas.filter(ativo=ativo == 'true')
    if search:
        empresas = empresas.filter(
            Q(nome__icontains=search) |
            Q(cidade__icontains=search) |
            Q(razao_social__icontains=search)
        )
    
    empresas = empresas.order_by('nome')
    
    # Paginação
    paginator = Paginator(empresas, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'estados': EmpresaParceira.objects.values_list('estado', flat=True).distinct().order_by('estado'),
    }
    
    return render(request, 'beneficios/empresa_list.html', context)


@login_required
def empresa_detail(request, pk):
    """Detalhes de uma empresa parceira"""
    empresa = get_object_or_404(EmpresaParceira, pk=pk)
    convenios = empresa.convenios.filter(ativo=True).order_by('-data_inicio')
    
    context = {
        'empresa': empresa,
        'convenios': convenios,
    }
    
    return render(request, 'beneficios/empresa_detail.html', context)


@login_required
def empresa_create(request):
    """Criar nova empresa parceira"""
    if request.method == 'POST':
        form = EmpresaParceiraForm(request.POST)
        if form.is_valid():
            empresa = form.save()
            messages.success(request, 'Empresa parceira criada com sucesso!')
            return redirect('beneficios:empresa_detail', pk=empresa.pk)
    else:
        form = EmpresaParceiraForm()
    
    context = {
        'form': form,
        'title': 'Nova Empresa Parceira',
        'action': 'Criar',
    }
    
    return render(request, 'beneficios/empresa_form.html', context)


@login_required
def empresa_update(request, pk):
    """Editar empresa parceira"""
    empresa = get_object_or_404(EmpresaParceira, pk=pk)
    
    if request.method == 'POST':
        form = EmpresaParceiraForm(request.POST, instance=empresa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empresa parceira atualizada com sucesso!')
            return redirect('beneficios:empresa_detail', pk=empresa.pk)
    else:
        form = EmpresaParceiraForm(instance=empresa)
    
    context = {
        'form': form,
        'empresa': empresa,
        'title': 'Editar Empresa Parceira',
        'action': 'Atualizar',
    }
    
    return render(request, 'beneficios/empresa_form.html', context)


@login_required
def empresa_delete(request, pk):
    """Excluir empresa parceira"""
    empresa = get_object_or_404(EmpresaParceira, pk=pk)
    
    if request.method == 'POST':
        empresa.delete()
        messages.success(request, 'Empresa parceira excluída com sucesso!')
        return redirect('beneficios:empresa_list')
    
    context = {
        'empresa': empresa,
    }
    
    return render(request, 'beneficios/empresa_confirm_delete.html', context)


# Views para Convênios
@login_required
def convenio_list(request):
    """Lista de convênios"""
    convenios = Convenio.objects.select_related('empresa').all()
    
    # Filtros
    categoria = request.GET.get('categoria')
    status = request.GET.get('status')
    ativo = request.GET.get('ativo')
    search = request.GET.get('search')
    
    if categoria:
        convenios = convenios.filter(categoria=categoria)
    if status:
        convenios = convenios.filter(status=status)
    if ativo is not None:
        convenios = convenios.filter(ativo=ativo == 'true')
    if search:
        convenios = convenios.filter(
            Q(titulo__icontains=search) |
            Q(empresa__nome__icontains=search) |
            Q(descricao__icontains=search)
        )
    
    convenios = convenios.order_by('-data_inicio')
    
    # Paginação
    paginator = Paginator(convenios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categorias': Convenio.CATEGORIA_CHOICES,
        'status_choices': Convenio.STATUS_CHOICES,
    }
    
    return render(request, 'beneficios/convenio_list.html', context)


@login_required
def convenio_detail(request, pk):
    """Detalhes de um convênio"""
    convenio = get_object_or_404(Convenio, pk=pk)
    beneficios = convenio.beneficios.select_related('associado').order_by('-data_solicitacao')
    
    context = {
        'convenio': convenio,
        'beneficios': beneficios,
    }
    
    return render(request, 'beneficios/convenio_detail.html', context)


@login_required
def convenio_create(request):
    """Criar novo convênio"""
    if request.method == 'POST':
        form = ConvenioForm(request.POST, request.FILES)
        if form.is_valid():
            convenio = form.save(commit=False)
            convenio.usuario_responsavel = request.user
            convenio.save()
            messages.success(request, 'Convênio criado com sucesso!')
            return redirect('beneficios:convenio_detail', pk=convenio.pk)
    else:
        form = ConvenioForm()
    
    context = {
        'form': form,
        'title': 'Novo Convênio',
        'action': 'Criar',
    }
    
    return render(request, 'beneficios/convenio_form.html', context)


@login_required
def convenio_update(request, pk):
    """Editar convênio"""
    convenio = get_object_or_404(Convenio, pk=pk)
    
    if request.method == 'POST':
        form = ConvenioForm(request.POST, request.FILES, instance=convenio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Convênio atualizado com sucesso!')
            return redirect('beneficios:convenio_detail', pk=convenio.pk)
    else:
        form = ConvenioForm(instance=convenio)
    
    context = {
        'form': form,
        'convenio': convenio,
        'title': 'Editar Convênio',
        'action': 'Atualizar',
    }
    
    return render(request, 'beneficios/convenio_form.html', context)


@login_required
def convenio_delete(request, pk):
    """Excluir convênio"""
    convenio = get_object_or_404(Convenio, pk=pk)
    
    if request.method == 'POST':
        convenio.delete()
        messages.success(request, 'Convênio excluído com sucesso!')
        return redirect('beneficios:convenio_list')
    
    context = {
        'convenio': convenio,
    }
    
    return render(request, 'beneficios/convenio_confirm_delete.html', context)


# Views para Benefícios
@login_required
def beneficio_list(request):
    """Lista de benefícios"""
    beneficios = Beneficio.objects.select_related('associado', 'convenio').all()
    
    # Filtros
    status = request.GET.get('status')
    categoria = request.GET.get('categoria')
    search = request.GET.get('search')
    
    if status:
        beneficios = beneficios.filter(status=status)
    if categoria:
        beneficios = beneficios.filter(convenio__categoria=categoria)
    if search:
        beneficios = beneficios.filter(
            Q(associado__nome__icontains=search) |
            Q(convenio__titulo__icontains=search) |
            Q(convenio__empresa__nome__icontains=search)
        )
    
    beneficios = beneficios.order_by('-data_solicitacao')
    
    # Paginação
    paginator = Paginator(beneficios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': Beneficio.STATUS_CHOICES,
        'categorias': Convenio.CATEGORIA_CHOICES,
    }
    
    return render(request, 'beneficios/beneficio_list.html', context)


@login_required
def beneficio_detail(request, pk):
    """Detalhes de um benefício"""
    beneficio = get_object_or_404(Beneficio, pk=pk)
    
    context = {
        'beneficio': beneficio,
    }
    
    return render(request, 'beneficios/beneficio_detail.html', context)


@login_required
def beneficio_create(request):
    """Criar novo benefício"""
    if request.method == 'POST':
        form = BeneficioForm(request.POST, request.FILES)
        if form.is_valid():
            beneficio = form.save()
            messages.success(request, 'Benefício criado com sucesso!')
            return redirect('beneficios:beneficio_detail', pk=beneficio.pk)
    else:
        form = BeneficioForm()
    
    context = {
        'form': form,
        'title': 'Novo Benefício',
        'action': 'Criar',
    }
    
    return render(request, 'beneficios/beneficio_form.html', context)


@login_required
def beneficio_update(request, pk):
    """Editar benefício"""
    beneficio = get_object_or_404(Beneficio, pk=pk)
    
    if request.method == 'POST':
        form = BeneficioForm(request.POST, request.FILES, instance=beneficio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Benefício atualizado com sucesso!')
            return redirect('beneficios:beneficio_detail', pk=beneficio.pk)
    else:
        form = BeneficioForm(instance=beneficio)
    
    context = {
        'form': form,
        'beneficio': beneficio,
        'title': 'Editar Benefício',
        'action': 'Atualizar',
    }
    
    return render(request, 'beneficios/beneficio_form.html', context)


@login_required
def beneficio_delete(request, pk):
    """Excluir benefício"""
    beneficio = get_object_or_404(Beneficio, pk=pk)
    
    if request.method == 'POST':
        beneficio.delete()
        messages.success(request, 'Benefício excluído com sucesso!')
        return redirect('beneficios:beneficio_list')
    
    context = {
        'beneficio': beneficio,
    }
    
    return render(request, 'beneficios/beneficio_confirm_delete.html', context)


# Views para Categorias de Benefícios
@login_required
def categoria_list(request):
    """Lista de categorias de benefícios"""
    categorias = CategoriaBeneficio.objects.all().order_by('ordem', 'nome')
    
    context = {
        'categorias': categorias,
    }
    
    return render(request, 'beneficios/categoria_list.html', context)


@login_required
def categoria_create(request):
    """Criar nova categoria"""
    if request.method == 'POST':
        form = CategoriaBeneficioForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, 'Categoria criada com sucesso!')
            return redirect('beneficios:categoria_list')
    else:
        form = CategoriaBeneficioForm()
    
    context = {
        'form': form,
        'title': 'Nova Categoria',
        'action': 'Criar',
    }
    
    return render(request, 'beneficios/categoria_form.html', context)


@login_required
def categoria_update(request, pk):
    """Editar categoria"""
    categoria = get_object_or_404(CategoriaBeneficio, pk=pk)
    
    if request.method == 'POST':
        form = CategoriaBeneficioForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('beneficios:categoria_list')
    else:
        form = CategoriaBeneficioForm(instance=categoria)
    
    context = {
        'form': form,
        'categoria': categoria,
        'title': 'Editar Categoria',
        'action': 'Atualizar',
    }
    
    return render(request, 'beneficios/categoria_form.html', context)


@login_required
def categoria_delete(request, pk):
    """Excluir categoria"""
    categoria = get_object_or_404(CategoriaBeneficio, pk=pk)
    
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria excluída com sucesso!')
        return redirect('beneficios:categoria_list')
    
    context = {
        'categoria': categoria,
    }
    
    return render(request, 'beneficios/categoria_confirm_delete.html', context)


# Views para Solicitação de Benefícios
@login_required
def solicitar_beneficio(request):
    """Solicitar um benefício"""
    if request.method == 'POST':
        form = BeneficioSolicitacaoForm(request.POST)
        if form.is_valid():
            beneficio = form.save(commit=False)
            beneficio.associado = request.user.associado
            beneficio.status = 'pendente'
            beneficio.save()
            messages.success(request, 'Solicitação de benefício enviada com sucesso!')
            return redirect('beneficios:meus_beneficios')
    else:
        form = BeneficioSolicitacaoForm()
    
    context = {
        'form': form,
        'title': 'Solicitar Benefício',
    }
    
    return render(request, 'beneficios/solicitar_beneficio.html', context)


@login_required
def meus_beneficios(request):
    """Lista de benefícios do usuário logado"""
    if hasattr(request.user, 'associado'):
        beneficios = Beneficio.objects.filter(
            associado=request.user.associado
        ).select_related('convenio', 'convenio__empresa').order_by('-data_solicitacao')
    else:
        beneficios = Beneficio.objects.none()
    
    context = {
        'beneficios': beneficios,
    }
    
    return render(request, 'beneficios/meus_beneficios.html', context)


# Views para Busca de Convênios
def buscar_convenios(request):
    """Busca de convênios disponíveis"""
    form = ConvenioBuscaForm(request.GET)
    convenios = Convenio.objects.filter(ativo=True, status='ativo').select_related('empresa')
    
    if form.is_valid():
        categoria = form.cleaned_data.get('categoria')
        cidade = form.cleaned_data.get('cidade')
        estado = form.cleaned_data.get('estado')
        termo_busca = form.cleaned_data.get('termo_busca')
        
        if categoria:
            convenios = convenios.filter(categoria=categoria)
        if cidade:
            convenios = convenios.filter(empresa__cidade__icontains=cidade)
        if estado:
            convenios = convenios.filter(empresa__estado=estado)
        if termo_busca:
            convenios = convenios.filter(
                Q(titulo__icontains=termo_busca) |
                Q(empresa__nome__icontains=termo_busca) |
                Q(descricao__icontains=termo_busca)
            )
    
    # Filtra apenas convênios válidos
    from datetime import date
    convenios = convenios.filter(
        Q(data_fim__isnull=True) | Q(data_fim__gte=date.today())
    ).order_by('empresa__nome', 'titulo')
    
    # Paginação
    paginator = Paginator(convenios, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
    }
    
    return render(request, 'beneficios/buscar_convenios.html', context)


# Views para Aprovação de Benefícios
@login_required
def aprovar_beneficio(request, pk):
    """Aprovar um benefício"""
    beneficio = get_object_or_404(Beneficio, pk=pk)
    
    if request.method == 'POST':
        beneficio.status = 'aprovado'
        beneficio.data_aprovacao = timezone.now()
        beneficio.usuario_aprovacao = request.user
        beneficio.save()
        messages.success(request, 'Benefício aprovado com sucesso!')
        return redirect('beneficios:beneficio_detail', pk=beneficio.pk)
    
    context = {
        'beneficio': beneficio,
    }
    
    return render(request, 'beneficios/aprovar_beneficio.html', context)


@login_required
def rejeitar_beneficio(request, pk):
    """Rejeitar um benefício"""
    beneficio = get_object_or_404(Beneficio, pk=pk)
    
    if request.method == 'POST':
        beneficio.status = 'rejeitado'
        beneficio.save()
        messages.success(request, 'Benefício rejeitado com sucesso!')
        return redirect('beneficios:beneficio_detail', pk=beneficio.pk)
    
    context = {
        'beneficio': beneficio,
    }
    
    return render(request, 'beneficios/rejeitar_beneficio.html', context)


# API Views
@login_required
def api_convenios_por_categoria(request):
    """API para obter convênios por categoria (para gráficos)"""
    convenios_por_categoria = Convenio.objects.filter(ativo=True).values('categoria').annotate(
        total=Count('id')
    ).order_by('-total')
    
    data = {
        'labels': [item['categoria'] for item in convenios_por_categoria],
        'data': [item['total'] for item in convenios_por_categoria],
    }
    
    return JsonResponse(data)


@login_required
def api_beneficios_por_status(request):
    """API para obter benefícios por status (para gráficos)"""
    beneficios_por_status = Beneficio.objects.values('status').annotate(
        total=Count('id')
    ).order_by('-total')
    
    data = {
        'labels': [item['status'] for item in beneficios_por_status],
        'data': [item['total'] for item in beneficios_por_status],
    }
    
    return JsonResponse(data)


@login_required
def api_categorias_ordem(request):
    """API para obter a maior ordem das categorias"""
    from django.db.models import Max
    
    max_ordem = CategoriaBeneficio.objects.aggregate(Max('ordem'))
    
    data = {
        'max_ordem': max_ordem['ordem__max']
    }
    
    return JsonResponse(data)
