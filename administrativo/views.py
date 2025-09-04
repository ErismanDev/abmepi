from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from .models import Evento, Comunicado, ParticipanteEvento, ListaPresenca, Presenca
from .forms import EventoForm, ComunicadoForm, ParticipanteEventoForm, ListaPresencaForm, PresencaForm


def criar_notificacoes_comunicado(comunicado):
    """
    Cria notificações para os destinatários de um comunicado
    """
    from core.models import Notificacao
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    usuarios_destino = []
    
    # Determinar usuários destino baseado no tipo de destinatários
    if comunicado.tipo_destinatarios == 'todos':
        # Todos os usuários ativos
        usuarios_destino = User.objects.filter(is_active=True)
    elif comunicado.tipo_destinatarios == 'associados':
        # Apenas associados
        usuarios_destino = User.objects.filter(tipo_usuario='associado', is_active=True)
    elif comunicado.tipo_destinatarios == 'advogados':
        # Apenas advogados
        usuarios_destino = User.objects.filter(tipo_usuario='advogado', is_active=True)
    elif comunicado.tipo_destinatarios == 'psicologos':
        # Apenas psicólogos
        usuarios_destino = User.objects.filter(tipo_usuario='psicologo', is_active=True)
    elif comunicado.tipo_destinatarios == 'especificos':
        # Usuários específicos baseados nas seleções
        usuarios_destino = []
        
        # Adicionar usuários dos associados específicos
        for associado in comunicado.associados_especificos.all():
            try:
                usuario = User.objects.get(associado=associado)
                usuarios_destino.append(usuario)
            except User.DoesNotExist:
                pass
        
        # Adicionar usuários dos advogados específicos
        for advogado in comunicado.advogados_especificos.all():
            try:
                usuario = User.objects.get(advogado=advogado)
                usuarios_destino.append(usuario)
            except User.DoesNotExist:
                pass
        
        # Adicionar usuários dos psicólogos específicos
        for psicologo in comunicado.psicologos_especificos.all():
            try:
                usuario = User.objects.get(psicologo=psicologo)
                usuarios_destino.append(usuario)
            except User.DoesNotExist:
                pass
    
    # Criar notificações para cada usuário destino
    notificacoes_criadas = 0
    for usuario in usuarios_destino:
        try:
            Notificacao.objects.create(
                titulo=f"Novo Comunicado: {comunicado.titulo}",
                mensagem=comunicado.conteudo[:200] + "..." if len(comunicado.conteudo) > 200 else comunicado.conteudo,
                tipo='sistema',
                usuario_destino=usuario,
                usuario_origem=comunicado.autor,
                objeto_tipo='Comunicado',
                objeto_id=comunicado.id,
                url_acao=f"/administrativo/comunicados/{comunicado.id}/",
                prioridade=1 if comunicado.prioridade == 'urgente' else 2
            )
            notificacoes_criadas += 1
        except Exception as e:
            print(f"Erro ao criar notificação para usuário {usuario.id}: {e}")
    
    return notificacoes_criadas


# Views para Eventos
@login_required
def evento_list(request):
    """Lista de eventos"""
    search = request.GET.get('search', '')
    tipo = request.GET.get('tipo', '')
    status = request.GET.get('status', '')
    
    eventos = Evento.objects.all()
    
    if search:
        eventos = eventos.filter(
            Q(titulo__icontains=search) |
            Q(descricao__icontains=search) |
            Q(local__icontains=search)
        )
    
    if tipo:
        eventos = eventos.filter(tipo=tipo)
    
    if status:
        eventos = eventos.filter(status=status)
    
    eventos = eventos.order_by('-data_inicio')
    
    # Paginação
    paginator = Paginator(eventos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'tipo': tipo,
        'status': status,
    }
    
    return render(request, 'administrativo/evento_list.html', context)


@login_required
def evento_create(request):
    """Criar novo evento"""
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.usuario_responsavel = request.user
            evento.save()
            messages.success(request, 'Evento criado com sucesso!')
            return redirect('administrativo:evento_detail', pk=evento.pk)
    else:
        form = EventoForm()
    
    context = {
        'form': form,
        'title': 'Novo Evento',
        'action': 'Criar',
    }
    
    return render(request, 'administrativo/evento_form.html', context)


@login_required
def evento_detail(request, pk):
    """Detalhes do evento"""
    evento = get_object_or_404(Evento, pk=pk)
    participantes = evento.participantes.all()
    
    context = {
        'evento': evento,
        'participantes': participantes,
    }
    
    return render(request, 'administrativo/evento_detail.html', context)


@login_required
def evento_update(request, pk):
    """Editar evento"""
    evento = get_object_or_404(Evento, pk=pk)
    
    if request.method == 'POST':
        form = EventoForm(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Evento atualizado com sucesso!')
            return redirect('administrativo:evento_detail', pk=evento.pk)
    else:
        form = EventoForm(instance=evento)
    
    context = {
        'form': form,
        'evento': evento,
        'title': 'Editar Evento',
        'action': 'Atualizar',
    }
    
    return render(request, 'administrativo/evento_form.html', context)


@login_required
def evento_delete(request, pk):
    """Excluir evento"""
    evento = get_object_or_404(Evento, pk=pk)
    
    if request.method == 'POST':
        evento.delete()
        messages.success(request, 'Evento excluído com sucesso!')
        return redirect('administrativo:evento_list')
    
    context = {
        'evento': evento,
    }
    
    return render(request, 'administrativo/evento_confirm_delete.html', context)


# Views para Comunicados
@login_required
def comunicado_list(request):
    """Lista de comunicados"""
    search = request.GET.get('search', '')
    tipo = request.GET.get('tipo', '')
    prioridade = request.GET.get('prioridade', '')
    
    comunicados = Comunicado.objects.all()
    
    if search:
        comunicados = comunicados.filter(
            Q(titulo__icontains=search) |
            Q(conteudo__icontains=search)
        )
    
    if tipo:
        comunicados = comunicados.filter(tipo=tipo)
    
    if prioridade:
        comunicados = comunicados.filter(prioridade=prioridade)
    
    comunicados = comunicados.order_by('-data_publicacao')
    
    # Paginação
    paginator = Paginator(comunicados, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'tipo': tipo,
        'prioridade': prioridade,
    }
    
    return render(request, 'administrativo/comunicado_list.html', context)


@login_required
def comunicado_create(request):
    """Criar novo comunicado - apenas administradores do sistema"""
    # Verificar se o usuário é administrador do sistema
    if request.user.tipo_usuario != 'administrador_sistema':
        messages.error(request, 'Você não tem permissão para criar comunicados.')
        return redirect('administrativo:comunicado_list')
    if request.method == 'POST':
        form = ComunicadoForm(request.POST, request.FILES)
        if form.is_valid():
            comunicado = form.save(commit=False)
            comunicado.autor = request.user
            comunicado.save()
            
            # Salva os campos ManyToMany
            form.save_m2m()
            
            # Criar notificações se solicitado
            if comunicado.enviar_notificacao:
                notificacoes_criadas = criar_notificacoes_comunicado(comunicado)
                if notificacoes_criadas > 0:
                    messages.success(request, f'Comunicado criado com sucesso! {notificacoes_criadas} notificações enviadas.')
                else:
                    messages.warning(request, 'Comunicado criado, mas nenhuma notificação foi enviada.')
            else:
                messages.success(request, 'Comunicado criado com sucesso!')
            return redirect('administrativo:comunicado_detail', pk=comunicado.pk)
    else:
        form = ComunicadoForm()
    
    context = {
        'form': form,
        'title': 'Novo Comunicado',
        'action': 'Criar',
    }
    
    return render(request, 'administrativo/comunicado_form.html', context)


@login_required
def comunicado_detail(request, pk):
    """Detalhes do comunicado"""
    # Verificar se o comunicado existe antes de tentar acessá-lo
    from core.models import Notificacao
    from django.contrib import messages
    
    # Verificar se existe notificação pendente para este comunicado
    notificacao_pendente = Notificacao.objects.filter(
        usuario_destino=request.user,
        objeto_tipo='Comunicado',
        objeto_id=pk,
        status='pendente'
    ).first()
    
    try:
        comunicado = get_object_or_404(Comunicado, pk=pk)
    except:
        # Se o comunicado não existir e houver notificação pendente, marcar como lida
        if notificacao_pendente:
            notificacao_pendente.marcar_como_lida()
            messages.warning(request, 'O comunicado referenciado nesta notificação não existe mais ou foi removido.')
        else:
            messages.error(request, 'Comunicado não encontrado.')
        
        return redirect('administrativo:comunicado_list')
    
    # Marcar notificação como lida se o usuário acessou via notificação
    try:
        if notificacao_pendente:
            notificacao_pendente.marcar_como_lida()
    except Exception as e:
        # Se houver erro ao marcar como lida, não interromper a visualização
        print(f"Erro ao marcar notificação como lida: {e}")
    
    context = {
        'comunicado': comunicado,
    }
    
    return render(request, 'administrativo/comunicado_detail.html', context)


@login_required
def comunicado_update(request, pk):
    """Editar comunicado - apenas administradores do sistema"""
    # Verificar se o usuário é administrador do sistema
    if request.user.tipo_usuario != 'administrador_sistema':
        messages.error(request, 'Você não tem permissão para editar comunicados.')
        return redirect('administrativo:comunicado_detail', pk=pk)
    
    comunicado = get_object_or_404(Comunicado, pk=pk)
    
    if request.method == 'POST':
        form = ComunicadoForm(request.POST, request.FILES, instance=comunicado)
        if form.is_valid():
            comunicado = form.save(commit=False)
            comunicado.save()
            
            # Salva os campos ManyToMany
            form.save_m2m()
            
            # Criar notificações se solicitado
            if comunicado.enviar_notificacao:
                notificacoes_criadas = criar_notificacoes_comunicado(comunicado)
                if notificacoes_criadas > 0:
                    messages.success(request, f'Comunicado atualizado com sucesso! {notificacoes_criadas} notificações enviadas.')
                else:
                    messages.warning(request, 'Comunicado atualizado, mas nenhuma notificação foi enviada.')
            else:
                messages.success(request, 'Comunicado atualizado com sucesso!')
            
            return redirect('administrativo:comunicado_detail', pk=comunicado.pk)
    else:
        form = ComunicadoForm(instance=comunicado)
    
    context = {
        'form': form,
        'comunicado': comunicado,
        'title': 'Editar Comunicado',
        'action': 'Atualizar',
    }
    
    return render(request, 'administrativo/comunicado_form.html', context)


@login_required
def comunicado_delete(request, pk):
    """Excluir comunicado - apenas administradores do sistema"""
    # Verificar se o usuário é administrador do sistema
    if request.user.tipo_usuario != 'administrador_sistema':
        messages.error(request, 'Você não tem permissão para excluir comunicados.')
        return redirect('administrativo:comunicado_detail', pk=pk)
    
    comunicado = get_object_or_404(Comunicado, pk=pk)
    
    if request.method == 'POST':
        comunicado.delete()
        messages.success(request, 'Comunicado excluído com sucesso!')
        return redirect('administrativo:comunicado_list')
    
    context = {
        'comunicado': comunicado,
    }
    
    return render(request, 'administrativo/comunicado_confirm_delete.html', context)


# Views para Listas de Presença
@login_required
def lista_presenca_list(request):
    """Lista de listas de presença"""
    search = request.GET.get('search', '')
    evento_id = request.GET.get('evento', '')
    
    listas = ListaPresenca.objects.all()
    
    if search:
        listas = listas.filter(
            Q(evento__titulo__icontains=search) |
            Q(observacoes__icontains=search)
        )
    
    if evento_id:
        listas = listas.filter(evento_id=evento_id)
    
    listas = listas.order_by('-data_registro')
    
    # Paginação
    paginator = Paginator(listas, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'evento_id': evento_id,
        'eventos': Evento.objects.filter(ativo=True).order_by('titulo'),
    }
    
    return render(request, 'administrativo/lista_presenca_list.html', context)


@login_required
def lista_presenca_create(request):
    """Criar nova lista de presença"""
    if request.method == 'POST':
        form = ListaPresencaForm(request.POST)
        if form.is_valid():
            lista = form.save(commit=False)
            lista.usuario_registro = request.user
            lista.save()
            messages.success(request, 'Lista de presença criada com sucesso!')
            return redirect('administrativo:lista_presenca_detail', pk=lista.pk)
    else:
        form = ListaPresencaForm()
    
    context = {
        'form': form,
        'title': 'Nova Lista de Presença',
        'action': 'Criar',
    }
    
    return render(request, 'administrativo/lista_presenca_form.html', context)


@login_required
def lista_presenca_detail(request, pk):
    """Exibir detalhes da lista de presença"""
    lista = get_object_or_404(ListaPresenca, pk=pk)
    presencas = lista.presencas.all()
    
    # Conta presentes e ausentes
    from .models import Presenca
    total_presentes = Presenca.contar_presentes(presencas)
    total_ausentes = Presenca.contar_ausentes(presencas)
    
    context = {
        'lista': lista,
        'presencas': presencas,
        'total_presentes': total_presentes,
        'total_ausentes': total_ausentes,
    }
    
    return render(request, 'administrativo/lista_presenca_detail.html', context)


@login_required
def lista_presenca_update(request, pk):
    """Editar lista de presença"""
    lista = get_object_or_404(ListaPresenca, pk=pk)
    
    if request.method == 'POST':
        form = ListaPresencaForm(request.POST, instance=lista)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lista de presença atualizada com sucesso!')
            return redirect('administrativo:lista_presenca_detail', pk=lista.pk)
    else:
        form = ListaPresencaForm(instance=lista)
    
    context = {
        'form': form,
        'lista': lista,
        'title': 'Editar Lista de Presença',
        'action': 'Atualizar',
    }
    
    return render(request, 'administrativo/lista_presenca_form.html', context)


@login_required
def lista_presenca_delete(request, pk):
    """Excluir lista de presença"""
    lista = get_object_or_404(ListaPresenca, pk=pk)
    
    if request.method == 'POST':
        lista.delete()
        messages.success(request, 'Lista de presença excluída com sucesso!')
        return redirect('administrativo:lista_presenca_list')
    
    context = {
        'lista': lista,
    }
    
    return render(request, 'administrativo/lista_presenca_confirm_delete.html', context)


@login_required
def presenca_create(request, lista_pk):
    """Adicionar presença à lista"""
    lista = get_object_or_404(ListaPresenca, pk=lista_pk)
    
    if request.method == 'POST':
        form = PresencaForm(request.POST)
        if form.is_valid():
            presenca = form.save(commit=False)
            presenca.lista_presenca = lista
            presenca.save()
            messages.success(request, 'Presença registrada com sucesso!')
            return redirect('administrativo:lista_presenca_detail', pk=lista.pk)
    else:
        form = PresencaForm()
    
    context = {
        'form': form,
        'lista': lista,
        'title': 'Registrar Presença',
        'action': 'Registrar',
    }
    
    return render(request, 'administrativo/presenca_form.html', context)


@login_required
def presenca_update(request, pk):
    """Editar presença"""
    presenca = get_object_or_404(Presenca, pk=pk)
    
    if request.method == 'POST':
        form = PresencaForm(request.POST, instance=presenca)
        if form.is_valid():
            form.save()
            messages.success(request, 'Presença atualizada com sucesso!')
            return redirect('administrativo:lista_presenca_detail', pk=presenca.lista_presenca.pk)
    else:
        form = PresencaForm(instance=presenca)
    
    context = {
        'form': form,
        'presenca': presenca,
        'lista': presenca.lista_presenca,
        'title': 'Editar Presença',
        'action': 'Atualizar',
    }
    
    return render(request, 'administrativo/presenca_form.html', context)


@login_required
def presenca_delete(request, pk):
    """Excluir presença"""
    presenca = get_object_or_404(Presenca, pk=pk)
    lista_pk = presenca.lista_presenca.pk
    
    if request.method == 'POST':
        presenca.delete()
        messages.success(request, 'Presença removida com sucesso!')
        return redirect('administrativo:lista_presenca_detail', pk=lista_pk)
    
    context = {
        'presenca': presenca,
    }
    
    return render(request, 'administrativo/presenca_confirm_delete.html', context)


# Views para Participantes de Eventos
@login_required
def participante_create(request, evento_pk):
    """Adicionar participante ao evento"""
    evento = get_object_or_404(Evento, pk=evento_pk)
    
    if request.method == 'POST':
        form = ParticipanteEventoForm(request.POST)
        if form.is_valid():
            participante = form.save(commit=False)
            participante.evento = evento
            participante.save()
            messages.success(request, 'Participante adicionado com sucesso!')
            return redirect('administrativo:evento_detail', pk=evento.pk)
    else:
        form = ParticipanteEventoForm()
    
    context = {
        'form': form,
        'evento': evento,
        'title': 'Adicionar Participante',
        'action': 'Adicionar',
    }
    
    return render(request, 'administrativo/participante_form.html', context)


@login_required
def participante_update(request, pk):
    """Editar participante"""
    participante = get_object_or_404(ParticipanteEvento, pk=pk)
    
    if request.method == 'POST':
        form = ParticipanteEventoForm(request.POST, instance=participante)
        if form.is_valid():
            form.save()
            messages.success(request, 'Participante atualizado com sucesso!')
            return redirect('administrativo:evento_detail', pk=participante.evento.pk)
    else:
        form = ParticipanteEventoForm(instance=participante)
    
    context = {
        'form': form,
        'participante': participante,
        'evento': participante.evento,  # Adiciona o evento ao context
        'title': 'Editar Participante',
        'action': 'Atualizar',
    }
    
    return render(request, 'administrativo/participante_form.html', context)


@login_required
def participante_delete(request, pk):
    """Excluir participante"""
    participante = get_object_or_404(ParticipanteEvento, pk=pk)
    evento_pk = participante.evento.pk
    
    if request.method == 'POST':
        participante.delete()
        messages.success(request, 'Participante removido com sucesso!')
        return redirect('administrativo:evento_detail', pk=evento_pk)
    
    context = {
        'participante': participante,
    }
    
    return render(request, 'administrativo/participante_confirm_delete.html', context)


# Dashboard administrativo
@login_required
def dashboard(request):
    """Dashboard administrativo"""
    # Estatísticas básicas
    total_eventos = Evento.objects.count()
    eventos_ativos = Evento.objects.filter(ativo=True).count()
    eventos_hoje = Evento.objects.filter(
        data_inicio__date=timezone.now().date()
    ).count()
    
    total_comunicados = Comunicado.objects.count()
    comunicados_ativos = Comunicado.objects.filter(ativo=True).count()
    
    total_listas = ListaPresenca.objects.count()
    
    # Próximos eventos
    proximos_eventos = Evento.objects.filter(
        data_inicio__gte=timezone.now(),
        ativo=True
    ).order_by('data_inicio')[:5]
    
    # Comunicados recentes
    comunicados_recentes = Comunicado.objects.filter(
        ativo=True
    ).order_by('-data_publicacao')[:5]
    
    context = {
        'total_eventos': total_eventos,
        'eventos_ativos': eventos_ativos,
        'eventos_hoje': eventos_hoje,
        'total_comunicados': total_comunicados,
        'comunicados_ativos': comunicados_ativos,
        'total_listas': total_listas,
        'proximos_eventos': proximos_eventos,
        'comunicados_recentes': comunicados_recentes,
    }
    
    return render(request, 'administrativo/dashboard.html', context)


@login_required
def teste_menu(request):
    """Página de teste para verificar o funcionamento do menu"""
    return render(request, 'administrativo/teste_menu.html')


@login_required
def debug_menu(request):
    """Página de debug para verificar o funcionamento do menu"""
    return render(request, 'administrativo/menu_debug.html')



@login_required

def lista_presenca_create(request):

    """Criar nova lista de presença"""

    if request.method == 'POST':

        form = ListaPresencaForm(request.POST)

        if form.is_valid():

            lista = form.save(commit=False)

            lista.usuario_registro = request.user

            lista.save()

            messages.success(request, 'Lista de presença criada com sucesso!')

            return redirect('administrativo:lista_presenca_detail', pk=lista.pk)

    else:

        form = ListaPresencaForm()

    

    context = {

        'form': form,

        'title': 'Nova Lista de Presença',

        'action': 'Criar',

    }

    

    return render(request, 'administrativo/lista_presenca_form.html', context)





@login_required

def lista_presenca_detail(request, pk):

    """Exibir detalhes da lista de presença"""

    lista = get_object_or_404(ListaPresenca, pk=pk)

    presencas = lista.presencas.all()

    

    # Conta presentes e ausentes

    from .models import Presenca

    total_presentes = Presenca.contar_presentes(presencas)

    total_ausentes = Presenca.contar_ausentes(presencas)

    

    context = {

        'lista': lista,

        'presencas': presencas,

        'total_presentes': total_presentes,

        'total_ausentes': total_ausentes,

    }

    

    return render(request, 'administrativo/lista_presenca_detail.html', context)





@login_required

def lista_presenca_update(request, pk):

    """Editar lista de presença"""

    lista = get_object_or_404(ListaPresenca, pk=pk)

    

    if request.method == 'POST':

        form = ListaPresencaForm(request.POST, instance=lista)

        if form.is_valid():

            form.save()

            messages.success(request, 'Lista de presença atualizada com sucesso!')

            return redirect('administrativo:lista_presenca_detail', pk=lista.pk)

    else:

        form = ListaPresencaForm(instance=lista)

    

    context = {

        'form': form,

        'lista': lista,

        'title': 'Editar Lista de Presença',

        'action': 'Atualizar',

    }

    

    return render(request, 'administrativo/lista_presenca_form.html', context)





@login_required

def lista_presenca_delete(request, pk):

    """Excluir lista de presença"""

    lista = get_object_or_404(ListaPresenca, pk=pk)

    

    if request.method == 'POST':

        lista.delete()

        messages.success(request, 'Lista de presença excluída com sucesso!')

        return redirect('administrativo:lista_presenca_list')

    

    context = {

        'lista': lista,

    }

    

    return render(request, 'administrativo/lista_presenca_confirm_delete.html', context)





@login_required

def presenca_create(request, lista_pk):

    """Adicionar presença à lista"""

    lista = get_object_or_404(ListaPresenca, pk=lista_pk)

    

    if request.method == 'POST':

        form = PresencaForm(request.POST)

        if form.is_valid():

            presenca = form.save(commit=False)

            presenca.lista_presenca = lista

            presenca.save()

            messages.success(request, 'Presença registrada com sucesso!')

            return redirect('administrativo:lista_presenca_detail', pk=lista.pk)

    else:

        form = PresencaForm()

    

    context = {

        'form': form,

        'lista': lista,

        'title': 'Registrar Presença',

        'action': 'Registrar',

    }

    

    return render(request, 'administrativo/presenca_form.html', context)





@login_required

def presenca_update(request, pk):

    """Editar presença"""

    presenca = get_object_or_404(Presenca, pk=pk)

    

    if request.method == 'POST':

        form = PresencaForm(request.POST, instance=presenca)

        if form.is_valid():

            form.save()

            messages.success(request, 'Presença atualizada com sucesso!')

            return redirect('administrativo:lista_presenca_detail', pk=presenca.lista_presenca.pk)

    else:

        form = PresencaForm(instance=presenca)

    

    context = {

        'form': form,

        'presenca': presenca,

        'lista': presenca.lista_presenca,

        'title': 'Editar Presença',

        'action': 'Atualizar',

    }

    

    return render(request, 'administrativo/presenca_form.html', context)





@login_required

def presenca_delete(request, pk):

    """Excluir presença"""

    presenca = get_object_or_404(Presenca, pk=pk)

    lista_pk = presenca.lista_presenca.pk

    

    if request.method == 'POST':

        presenca.delete()

        messages.success(request, 'Presença removida com sucesso!')

        return redirect('administrativo:lista_presenca_detail', pk=lista_pk)

    

    context = {

        'presenca': presenca,

    }

    

    return render(request, 'administrativo/presenca_confirm_delete.html', context)





# Views para Participantes de Eventos

@login_required

def participante_create(request, evento_pk):

    """Adicionar participante ao evento"""

    evento = get_object_or_404(Evento, pk=evento_pk)

    

    if request.method == 'POST':

        form = ParticipanteEventoForm(request.POST)

        if form.is_valid():

            participante = form.save(commit=False)

            participante.evento = evento

            participante.save()

            messages.success(request, 'Participante adicionado com sucesso!')

            return redirect('administrativo:evento_detail', pk=evento.pk)

    else:

        form = ParticipanteEventoForm()

    

    context = {

        'form': form,

        'evento': evento,

        'title': 'Adicionar Participante',

        'action': 'Adicionar',

    }

    

    return render(request, 'administrativo/participante_form.html', context)





@login_required

def participante_update(request, pk):

    """Editar participante"""

    participante = get_object_or_404(ParticipanteEvento, pk=pk)

    

    if request.method == 'POST':

        form = ParticipanteEventoForm(request.POST, instance=participante)

        if form.is_valid():

            form.save()

            messages.success(request, 'Participante atualizado com sucesso!')

            return redirect('administrativo:evento_detail', pk=participante.evento.pk)

    else:

        form = ParticipanteEventoForm(instance=participante)

    

    context = {

        'form': form,

        'participante': participante,

        'evento': participante.evento,  # Adiciona o evento ao context

        'title': 'Editar Participante',

        'action': 'Atualizar',

    }

    

    return render(request, 'administrativo/participante_form.html', context)





@login_required

def participante_delete(request, pk):

    """Excluir participante"""

    participante = get_object_or_404(ParticipanteEvento, pk=pk)

    evento_pk = participante.evento.pk

    

    if request.method == 'POST':

        participante.delete()

        messages.success(request, 'Participante removido com sucesso!')

        return redirect('administrativo:evento_detail', pk=evento_pk)

    

    context = {

        'participante': participante,

    }

    

    return render(request, 'administrativo/participante_confirm_delete.html', context)





# Dashboard administrativo

@login_required

def dashboard(request):

    """Dashboard administrativo"""

    # Estatísticas básicas

    total_eventos = Evento.objects.count()

    eventos_ativos = Evento.objects.filter(ativo=True).count()

    eventos_hoje = Evento.objects.filter(

        data_inicio__date=timezone.now().date()

    ).count()

    

    total_comunicados = Comunicado.objects.count()

    comunicados_ativos = Comunicado.objects.filter(ativo=True).count()

    

    total_listas = ListaPresenca.objects.count()

    

    # Próximos eventos

    proximos_eventos = Evento.objects.filter(

        data_inicio__gte=timezone.now(),

        ativo=True

    ).order_by('data_inicio')[:5]

    

    # Comunicados recentes

    comunicados_recentes = Comunicado.objects.filter(

        ativo=True

    ).order_by('-data_publicacao')[:5]

    

    context = {

        'total_eventos': total_eventos,

        'eventos_ativos': eventos_ativos,

        'eventos_hoje': eventos_hoje,

        'total_comunicados': total_comunicados,

        'comunicados_ativos': comunicados_ativos,

        'total_listas': total_listas,

        'proximos_eventos': proximos_eventos,

        'comunicados_recentes': comunicados_recentes,

    }

    

    return render(request, 'administrativo/dashboard.html', context)





@login_required

def teste_menu(request):

    """Página de teste para verificar o funcionamento do menu"""

    return render(request, 'administrativo/teste_menu.html')





@login_required

def debug_menu(request):

    """Página de debug para verificar o funcionamento do menu"""

    return render(request, 'administrativo/menu_debug.html')


