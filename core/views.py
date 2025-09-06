from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
<<<<<<< HEAD
from django.db.models import Count, Sum, Q, Prefetch, Max
=======
from django.db.models import Count, Sum, Q
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.models import Group
import logging

logger = logging.getLogger(__name__)

<<<<<<< HEAD
from .models import Usuario, LogAtividade, ConfiguracaoSistema, InstitucionalConfig, FeedPost, Like, Comentario, AssejurNews, AssejurInformativo, AssejurNewsComentario, Notificacao, ExPresidente, HistoriaAssociacao, HistoriaImagem
from .forms import LoginForm, UsuarioCreationForm, UsuarioChangeForm, InstitucionalConfigForm, FeedPostForm, AssejurNewsForm, AssejurInformativoForm, ExPresidenteForm, HistoriaAssociacaoForm
=======
from .models import Usuario, LogAtividade, ConfiguracaoSistema, InstitucionalConfig, FeedPost, Like, Comentario, AssejurNews, AssejurInformativo, AssejurNewsComentario, Notificacao
from .forms import LoginForm, UsuarioCreationForm, UsuarioChangeForm, InstitucionalConfigForm, FeedPostForm, AssejurNewsForm, AssejurInformativoForm
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
from .permissions import PermissionRequiredMixin
from associados.models import Associado
from financeiro.models import Mensalidade
from assejus.models import AtendimentoJuridico
from .forms import UsuarioProfileForm
from django.contrib.auth import update_session_auth_hash


class InstitucionalView(TemplateView):
    """
    View para a página institucional do sistema
    """
    template_name = 'core/institucional.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Obter configurações personalizadas
        config = InstitucionalConfig.get_config()
        context.update({
            'config': config,
            'titulo_principal': config.titulo_principal,
            'subtitulo_hero': config.subtitulo_hero,
            'titulo_sobre': config.titulo_sobre,
            'texto_sobre_1': config.texto_sobre_1,
            'texto_sobre_2': config.texto_sobre_2,
            'texto_sobre_3': config.texto_sobre_3,
            'titulo_cta': config.titulo_cta,
            'texto_cta': config.texto_cta,
            'telefone': config.telefone,
            'email': config.email,
            'endereco': config.endereco,
            'facebook_url': config.facebook_url,
            'instagram_url': config.instagram_url,
            'linkedin_url': config.linkedin_url,
            'youtube_url': config.youtube_url,
            'mostrar_estatisticas': config.mostrar_estatisticas,
            'mostrar_servicos': config.mostrar_servicos,
            'mostrar_sobre': config.mostrar_sobre,
            'mostrar_cta': config.mostrar_cta,
            'meta_description': config.meta_description,
            'meta_keywords': config.meta_keywords,
<<<<<<< HEAD
            # Serviços prestados aos associados
            'servicos_juridicos': config.servicos_juridicos,
            'servicos_psicologicos': config.servicos_psicologicos,
            'servicos_medicos': config.servicos_medicos,
            'servicos_odontologicos': config.servicos_odontologicos,
            'servicos_financeiros': config.servicos_financeiros,
            'servicos_educacionais': config.servicos_educacionais,
            'servicos_recreativos': config.servicos_recreativos,
            'servicos_sociais': config.servicos_sociais,
            'servicos_esportivos': config.servicos_esportivos,
            'servicos_culturais': config.servicos_culturais,
            'servicos_hotel_transito': config.servicos_hotel_transito,
=======
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
        })
        
        # Estatísticas para exibir na página institucional (se habilitado)
        if config.mostrar_estatisticas:
            context['total_associados'] = Associado.objects.filter(ativo=True).count()
            context['total_usuarios'] = Usuario.objects.filter(ativo=True).count()
            context['casos_juridicos'] = AtendimentoJuridico.objects.filter(status='em_andamento').count()
        
        # Posts do feed (apenas posts ativos)
        feed_posts = FeedPost.objects.filter(ativo=True).order_by('-destaque', '-ordem_exibicao', '-data_publicacao')[:10]
        
        # Adicionar informações de likes e comentários para todos os usuários
        session_likes = self.request.session.get('post_likes', {})
        
        for post in feed_posts:
            # Sincronizar contadores do post
            post.sync_counters()
            
            # Verificar se usuário curtiu (autenticado) ou usando sessão (anônimo)
            if self.request.user.is_authenticated:
                post.user_has_liked = post.user_liked(self.request.user)
            else:
                post.user_has_liked = str(post.id) in session_likes
            
            # Contar likes incluindo sessão para usuários anônimos
            post.likes_count = post.get_likes_count()
            
            # Contar comentários ativos
            post.comments_count = post.get_comentarios_count()
            
            # Obter comentários ativos do post (melhorados)
            post.comments_list = post.comentario_set.filter(ativo=True).select_related('usuario').order_by('data_criacao')[:5]
            
            # Debug: Log informações do post
            print(f"DEBUG - Post {post.id}: likes={post.likes_count}, comments={post.comments_count}, comments_list_count={len(post.comments_list)}")
        
        context['feed_posts'] = feed_posts
        
        # Notícias da Assessoria Jurídica para o carrossel (10 mais recentes)
        assejur_news = AssejurNews.objects.filter(
            ativo=True
        ).order_by('-destaque', '-ordem_exibicao', '-data_publicacao')[:10]
        
        context['assejur_news'] = assejur_news
        
        # Notícias anteriores (excluindo as 10 do carrossel)
        noticias_anteriores = AssejurNews.objects.filter(
            ativo=True
        ).order_by('-destaque', '-ordem_exibicao', '-data_publicacao')[10:22]  # Próximas 12 notícias
        
        context['noticias_anteriores'] = noticias_anteriores
        
        # Serializar dados das notícias para o JavaScript
        assejur_news_json = []
        for noticia in assejur_news:
            assejur_news_json.append({
                'id': noticia.id,
                'titulo': noticia.titulo,
                'resumo': noticia.resumo,
                'categoria': noticia.get_categoria_display(),
                'icone': noticia.icone,
                'data_publicacao': noticia.data_publicacao.strftime('%Y-%m-%d') if noticia.data_publicacao else '',
                'prioridade': noticia.prioridade,
                'link_externo': noticia.link_externo or '',
                'conteudo': noticia.conteudo,
                'tags': noticia.tags,
                'ativo': noticia.ativo,
                'destaque': noticia.destaque,
                'ordem_exibicao': noticia.ordem_exibicao or 0,
                'imagem': noticia.imagem.url if noticia.imagem else '',
                'imagem_legenda': noticia.imagem_legenda or '',
            })
        
        import json
        context['assejur_news_json'] = json.dumps(assejur_news_json)
        
<<<<<<< HEAD
        # Buscar presidente atual da diretoria
        from diretoria.models import MembroDiretoria
        presidente_atual = MembroDiretoria.get_presidente_atual()
        context['presidente_atual'] = presidente_atual
        
=======
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
        return context


class DashboardView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    """
    View para o dashboard principal do sistema
    Apenas administradores do sistema podem acessar
    """
    template_name = 'core/dashboard.html'
    user_types_allowed = ['administrador_sistema']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estatísticas gerais
        context['total_associados'] = Associado.objects.filter(ativo=True).count()
        context['total_usuarios'] = Usuario.objects.filter(ativo=True).count()
        context['mensalidades_pendentes'] = Mensalidade.objects.filter(status='pendente').count()
        context['casos_juridicos'] = AtendimentoJuridico.objects.filter(status='em_andamento').count()
        
        # Receitas do mês atual
        mes_atual = timezone.now().month
        ano_atual = timezone.now().year
        context['receita_mes'] = Mensalidade.objects.filter(
            status='pago',
            data_vencimento__month=mes_atual,
            data_vencimento__year=ano_atual
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        # Atividades recentes
        context['atividades_recentes'] = LogAtividade.objects.select_related('usuario')[:10]
        
        # Notificações pendentes
        context['notificacoes_pendentes'] = Notificacao.objects.filter(
            usuario_destino=self.request.user,
            status='pendente'
        ).order_by('-prioridade', '-data_criacao')[:10]
        
        # Contador de notificações pendentes
        context['total_notificacoes_pendentes'] = Notificacao.objects.filter(
            usuario_destino=self.request.user,
            status='pendente'
        ).count()
        
        # Gráfico de associados por situação
        context['associados_por_situacao'] = Associado.objects.values('situacao').annotate(total=Count('id'))
        
        # Estatísticas adicionais
        context['associados_por_estado'] = Associado.objects.values('estado').annotate(total=Count('id'))[:10]
        context['associados_recentes'] = Associado.objects.order_by('-data_cadastro')[:5]
        context['mensalidades_vencidas'] = Mensalidade.objects.filter(status='pendente', data_vencimento__lt=timezone.now()).count()
        
        return context


def login_view(request):
    """
    View personalizada para login
    """
    if request.user.is_authenticated:
        # Redirecionar baseado no tipo de usuário
        if request.user.tipo_usuario == 'administrador_sistema':
            return redirect('dashboard')
        elif request.user.tipo_usuario in ['advogado', 'atendente_advogado']:
            return redirect('assejus:dashboard')
        elif request.user.tipo_usuario == 'psicologo':
            return redirect('psicologia:psicologo_dashboard')
        elif request.user.tipo_usuario == 'atendente_psicologo':
            return redirect('psicologia:dashboard')
        elif request.user.tipo_usuario == 'atendente_geral':
            return redirect('associados:associado_list')
        elif request.user.tipo_usuario == 'associado':
            # Associados podem ver apenas suas próprias informações
            if hasattr(request.user, 'associado') and request.user.associado:
                return redirect('associados:minha_ficha')
            else:
                return redirect('core:usuario_dashboard')
        else:
            # Fallback para página institucional
            return redirect('institucional')
    
    # Inicializar formulário
    form = LoginForm()
    
    if request.method == 'POST':
        try:
            form = LoginForm(request, data=request.POST)
            
            if form.is_valid():
                username = form.cleaned_data.get('username')
                password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                
                if user is not None and user.is_active:
                    login(request, user)
                    
                    # Registrar log de atividade
                    LogAtividade.objects.create(
                        usuario=user,
                        acao='Login realizado',
                        modulo='Sistema',
                        ip_address=request.META.get('REMOTE_ADDR')
                    )
                    
                    # Atualizar último acesso
                    user.ultimo_acesso = timezone.now()
                    user.save(update_fields=['ultimo_acesso'])
                    
                    messages.success(request, f'Bem-vindo, {user.get_full_name()}!')
                    
                    # Redirecionar baseado no tipo de usuário usando a função auxiliar
                    return redirect_to_user_dashboard(user)
                else:
                    messages.error(request, 'CPF ou senha inválidos.')
            else:
                # Formulário inválido - mostrar erros de validação
                if form.errors:
                    for field, errors in form.errors.items():
                        for error in errors:
                            if field in form.fields:
                                messages.error(request, f'{form.fields[field].label}: {error}')
                            else:
                                messages.error(request, f'{error}')
                else:
                    messages.error(request, 'CPF ou senha inválidos.')
                    
        except Exception as e:
            print(f"❌ Erro na view de login: {e}")
            messages.error(request, 'Erro interno. Tente novamente.')
    
    return render(request, 'core/login.html', {'form': form})


@login_required
def primeiro_acesso_view(request):
    """
    View para primeiro acesso - força alteração de senha
    """
    if not request.user.primeiro_acesso:
        # Se não é primeiro acesso, redireciona para dashboard
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = UsuarioProfileForm(request.POST)
        if form.is_valid():
            # Alterar senha do usuário
            nova_senha = form.cleaned_data['nova_senha']
            request.user.set_password(nova_senha)
            request.user.primeiro_acesso = False
            request.user.save()
            
            # Atualizar sessão
            update_session_auth_hash(request, request.user)
            
            # Log da atividade
            LogAtividade.objects.create(
                usuario=request.user,
                acao='Alteração de senha no primeiro acesso',
                modulo='Autenticação',
                detalhes='Usuário alterou a senha padrão no primeiro acesso',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, 'Senha alterada com sucesso! Agora você pode acessar o sistema normalmente.')
            return redirect('dashboard')
    else:
        form = UsuarioProfileForm()
    
    # Adicionar senha padrão ao contexto
    from django.conf import settings
    senha_padrao = getattr(settings, 'SENHA_PADRAO_USUARIO', '12345678')
    
    context = {
        'form': form,
        'senha_padrao': senha_padrao,
        'username': request.user.username
    }
    
    return render(request, 'core/primeiro_acesso.html', context)


class UsuarioListView(LoginRequiredMixin, ListView):
    """
    Lista de usuários do sistema
    """
    model = Usuario
    template_name = 'core/usuario_list.html'
    context_object_name = 'usuarios'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Usuario.objects.all().order_by('username')
        
        # Filtro por tipo de usuário
        tipo_usuario = self.request.GET.get('tipo_usuario')
        if tipo_usuario:
            queryset = queryset.filter(tipo_usuario=tipo_usuario)
        
        # Filtro por status
        ativo = self.request.GET.get('ativo')
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo == 'true')
        
        # Filtro de busca por nome ou CPF
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(username__icontains=search) |
                Q(email__icontains=search)
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_usuario'] = Usuario.TIPO_USUARIO_CHOICES
        
        # Estatísticas para o dashboard
        queryset = self.get_queryset()
        context['total_usuarios'] = Usuario.objects.count()
        context['usuarios_ativos'] = Usuario.objects.filter(ativo=True).count()
        context['usuarios_inativos'] = Usuario.objects.filter(ativo=False).count()
        context['administradores'] = Usuario.objects.filter(tipo_usuario='administrador_sistema').count()
        
        return context


class UsuarioCreateView(LoginRequiredMixin, CreateView):
    """
    Criação de novos usuários
    """
    model = Usuario
    form_class = UsuarioCreationForm
    template_name = 'core/usuario_form.html'
    success_url = reverse_lazy('core:usuario_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Carregar dados dos cadastros existentes para facilitar criação de usuários
        try:
            # Advogados sem usuário associado
            advogados_sem_usuario = []
            try:
                from assejus.models import Advogado
                advogados_sem_usuario = list(Advogado.objects.filter(
                    user__isnull=True
                ).values('cpf', 'nome', 'email', 'oab', 'uf_oab')[:20])
                print(f"🔍 Advogados sem usuário: {len(advogados_sem_usuario)}")
                
                # Debug: mostrar alguns advogados
                for advogado in advogados_sem_usuario[:3]:
                    print(f"   - {advogado['cpf']} - {advogado['nome']}")
                    
            except Exception as e:
                print(f"⚠️ Erro ao carregar advogados: {e}")
                import traceback
                traceback.print_exc()
            
            # Psicólogos sem usuário associado
            psicologos_sem_usuario = []
            try:
                from psicologia.models import Psicologo
                psicologos_sem_usuario = list(Psicologo.objects.filter(
                    user__isnull=True
                ).values('cpf', 'nome_completo', 'email', 'crp', 'uf_crp')[:20])
                print(f"🔍 Psicólogos sem usuário: {len(psicologos_sem_usuario)}")
                
                # Debug: mostrar alguns psicólogos
                for psicologo in psicologos_sem_usuario[:3]:
                    print(f"   - {psicologo['cpf']} - {psicologo['nome_completo']}")
                    
            except Exception as e:
                print(f"⚠️ Erro ao carregar psicólogos: {e}")
                import traceback
                traceback.print_exc()
            
            # Associados sem usuário associado
            associados_sem_usuario = []
            try:
                from associados.models import Associado
                associados_sem_usuario = list(Associado.objects.filter(
                    usuario__isnull=True
                ).values('cpf', 'nome', 'email')[:20])
                print(f"🔍 Associados sem usuário: {len(associados_sem_usuario)}")
                
                # Debug: mostrar alguns associados
                for associado in associados_sem_usuario[:3]:
                    print(f"   - {associado['cpf']} - {associado['nome']}")
                    
            except Exception as e:
                print(f"⚠️ Erro ao carregar associados: {e}")
                import traceback
                traceback.print_exc()
            
            context.update({
                'advogados_disponiveis': advogados_sem_usuario,
                'psicologos_disponiveis': psicologos_sem_usuario,
                'associados_disponiveis': associados_sem_usuario,
                'total_cadastros_disponiveis': len(advogados_sem_usuario) + len(psicologos_sem_usuario) + len(associados_sem_usuario)
            })
            
        except Exception as e:
            print(f"❌ Erro geral ao carregar dados: {e}")
            context.update({
                'advogados_disponiveis': [],
                'psicologos_disponiveis': [],
                'associados_disponiveis': [],
                'total_cadastros_disponiveis': 0
            })
        
        return context
    
    def form_valid(self, form):
        print(f"🔍 DEBUG: form_valid chamado")
        print(f"🔍 DEBUG: Dados do formulário: {form.cleaned_data}")
        
        response = super().form_valid(form)
        
        # Mostrar a senha padrão para o usuário
        senha_padrao = 'abmepi2025'
        
        messages.success(
            self.request, 
            f'Usuário {form.instance.username} criado com sucesso! '
            f'Senha padrão: <strong>{senha_padrao}</strong> - '
            f'O usuário deve alterar esta senha no primeiro acesso.'
        )
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Usuário criado',
            modulo='Core',
            detalhes=f'Usuário {form.instance.username} criado'
        )
        
        return response
    
    def form_invalid(self, form):
        print(f"❌ DEBUG: form_invalid chamado")
        print(f"❌ DEBUG: Erros do formulário: {form.errors}")
        print(f"❌ DEBUG: Erros não relacionados a campos: {form.non_field_errors()}")
        return super().form_invalid(form)


class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
    """
    Atualização de usuários existentes
    """
    model = Usuario
    form_class = UsuarioChangeForm
    template_name = 'core/usuario_form.html'
    success_url = reverse_lazy('core:usuario_list')
    
    def form_valid(self, form):
        # Verificar se há alteração de senha
        password1 = form.cleaned_data.get('password1')
        password2 = form.cleaned_data.get('password2')
        gerar_nova_senha = form.cleaned_data.get('gerar_nova_senha')
        
        # Salvar o usuário primeiro
        response = super().form_valid(form)
        
        # Se foi fornecida uma nova senha ou marcou para gerar, alterá-la
        if password1 and password2 and password1 == password2:
            self.object.set_password(password1)
            
            # Armazenar senha temporária para visualização de administradores
            from django.utils import timezone
            from datetime import timedelta
            
            self.object.senha_temporaria = password1
            self.object.senha_temporaria_expira = timezone.now() + timedelta(hours=24)  # Expira em 24 horas
            self.object.save()
            
            # Mostrar mensagem com a nova senha se foi gerada automaticamente
            if gerar_nova_senha:
                messages.success(
                    self.request, 
                    f'Usuário atualizado e nova senha definida com sucesso! '
                    f'Nova senha: <strong>{password1}</strong> - '
                    f'Guarde esta senha, ela será necessária para o próximo acesso.'
                )
            else:
                messages.success(self.request, 'Usuário atualizado e senha alterada com sucesso!')
            
            # Se o usuário editado é o próprio usuário logado, redirecionar para dashboard apropriado
            if self.object == self.request.user:
                return redirect_to_user_dashboard(self.object)
        else:
            messages.success(self.request, 'Usuário atualizado com sucesso!')
            
            # Se o usuário editado é o próprio usuário logado, redirecionar para dashboard apropriado
            if self.object == self.request.user:
                return redirect_to_user_dashboard(self.object)
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Usuário atualizado',
            modulo='Core',
            detalhes=f'Usuário {form.instance.username} atualizado'
        )
        
        return response


class UsuarioDeleteView(LoginRequiredMixin, DeleteView):
    """
    Exclusão de usuários
    """
    model = Usuario
    template_name = 'core/usuario_confirm_delete.html'
    success_url = reverse_lazy('core:usuario_list')
    
    def delete(self, request, *args, **kwargs):
        usuario = self.get_object()
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Usuário excluído',
            modulo='Core',
            detalhes=f'Usuário {usuario.username} excluído'
        )
        
        messages.success(request, 'Usuário excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
def perfil_usuario(request):
    """
    View para o usuário visualizar e editar seu próprio perfil
    """
    # Associados só podem visualizar, não editar
    if request.user.tipo_usuario == 'associado':
        context = {'user': request.user}
        
        # Adicionar informações do associado se existir
        try:
            from associados.models import Associado
            associado = Associado.objects.get(usuario=request.user)
            context['associado'] = associado
        except Associado.DoesNotExist:
            pass
        
        return render(request, 'core/perfil_visualizacao.html', context)
    
    if request.method == 'POST':
        form = UsuarioChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            # Verificar se houve alteração de senha
            password1 = form.cleaned_data.get('password1')
            password2 = form.cleaned_data.get('password2')
            gerar_nova_senha = form.cleaned_data.get('gerar_nova_senha')
            
            # Salvar o usuário primeiro
            form.save()
            
            # Se foi fornecida uma nova senha ou marcou para gerar, alterá-la
            if password1 and password2 and password1 == password2:
                request.user.set_password(password1)
                
                # Armazenar senha temporária para visualização de administradores
                from django.utils import timezone
                from datetime import timedelta
                
                request.user.senha_temporaria = password1
                request.user.senha_temporaria_expira = timezone.now() + timedelta(hours=24)  # Expira em 24 horas
                request.user.save()
                
                # Mostrar mensagem com a nova senha se foi gerada automaticamente
                if gerar_nova_senha:
                    messages.success(
                        request, 
                        f'Perfil atualizado e nova senha definida com sucesso! '
                        f'Nova senha: <strong>{password1}</strong> - '
                        f'Guarde esta senha, ela será necessária para o próximo acesso.'
                    )
                else:
                    messages.success(request, 'Perfil atualizado e senha alterada com sucesso!')
                
                # Registrar log de atividade
                LogAtividade.objects.create(
                    usuario=request.user,
                    acao='Perfil atualizado e senha alterada',
                    modulo='Core',
                    detalhes='Usuário alterou próprio perfil e senha'
                )
                
                # Redirecionar para o dashboard apropriado baseado no tipo de usuário
                return redirect_to_user_dashboard(request.user)
            else:
                messages.success(request, 'Perfil atualizado com sucesso!')
                
                # Registrar log de atividade
                LogAtividade.objects.create(
                    usuario=request.user,
                    acao='Perfil atualizado',
                    modulo='Core',
                    detalhes='Usuário alterou próprio perfil'
                )
                
                # Redirecionar para o dashboard apropriado baseado no tipo de usuário
                return redirect_to_user_dashboard(request.user)
    else:
        form = UsuarioChangeForm(instance=request.user)
    
    return render(request, 'core/perfil.html', {'form': form})


def redirect_to_user_dashboard(user):
    """
    Função para redirecionar usuário para o dashboard apropriado baseado no tipo
    """
    if user.tipo_usuario == 'administrador_sistema':
        return redirect('core:dashboard')
    elif user.tipo_usuario in ['advogado', 'atendente_advogado']:
        return redirect('assejus:dashboard')
    elif user.tipo_usuario == 'psicologo':
        return redirect('psicologia:psicologo_dashboard')
    elif user.tipo_usuario == 'atendente_psicologo':
        return redirect('psicologia:dashboard')
    elif user.tipo_usuario == 'atendente_geral':
        return redirect('associados:associado_list')
    elif user.tipo_usuario == 'associado':
        # Associados podem ver apenas suas próprias informações
        if hasattr(user, 'associado') and user.associado:
            return redirect('associados:minha_ficha')
        else:
            return redirect('core:usuario_dashboard')
    else:
        # Fallback para dashboard de usuário comum
        return redirect('core:usuario_dashboard')


@login_required
def usuario_dashboard(request):
    """
    Dashboard para usuários comuns (não administradores)
    """
    context = {
        'user': request.user,
        'title': 'Meu Dashboard',
        'subtitle': 'Bem-vindo ao seu painel pessoal',
        'associado': None,
        'advogado': None,
        'psicologo': None,
        'mensalidades': [],
        'casos_recentes': [],
        'atendimentos_recentes': []
    }
    
    # Adicionar informações específicas baseadas no tipo de usuário
    if request.user.tipo_usuario == 'associado':
        try:
            from associados.models import Associado
            # Primeiro, tentar buscar pelo relacionamento direto
            associado = Associado.objects.get(usuario=request.user)
            context['associado'] = associado
            context['mensalidades'] = associado.mensalidades.all()[:5]  # Últimas 5 mensalidades
        except Associado.DoesNotExist:
            # Se não existe pelo relacionamento, tentar buscar pelo CPF
            try:
                associado = Associado.objects.get(cpf=request.user.username)
                # Vincular automaticamente o usuário ao associado
                associado.usuario = request.user
                associado.save()
                context['associado'] = associado
                context['mensalidades'] = associado.mensalidades.all()[:5]
                
                # Registrar log de atividade
                from core.models import LogAtividade
                LogAtividade.objects.create(
                    usuario=request.user,
                    acao='Associado vinculado automaticamente',
                    modulo='Core',
                    detalhes=f'Usuário {request.user.username} vinculado ao associado {associado.nome}'
                )
                
            except Associado.DoesNotExist:
                # Se não existe associado, manter como None
                pass
    elif request.user.tipo_usuario == 'advogado':
        try:
            from assejus.models import Advogado
            advogado = Advogado.objects.get(user=request.user)
            context['advogado'] = advogado
            context['casos_recentes'] = advogado.casos_responsavel.all()[:5]  # Últimos 5 casos
        except Advogado.DoesNotExist:
            # Se não existe advogado, manter como None
            pass
    elif request.user.tipo_usuario == 'psicologo':
        try:
            from psicologia.models import Psicologo
            psicologo = Psicologo.objects.get(user=request.user)
            context['psicologo'] = psicologo
            context['atendimentos_recentes'] = psicologo.sessao_set.all()[:5]  # Últimas 5 sessões
        except Psicologo.DoesNotExist:
            # Se não existe psicologo, manter como None
            pass
    
    # Adicionar atividades recentes do usuário
    context['atividades_recentes'] = LogAtividade.objects.filter(usuario=request.user)[:10]
    
    return render(request, 'core/usuario_dashboard.html', context)


@login_required
def dashboard_stats(request):
    """
    API para estatísticas do dashboard (AJAX)
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # Estatísticas em tempo real
        mes_atual = timezone.now().month
        ano_atual = timezone.now().year
        
        stats = {
            'total_associados': Associado.objects.filter(ativo=True).count(),
            'receita_mes': Mensalidade.objects.filter(
                status='pago',
                data_vencimento__month=mes_atual,
                data_vencimento__year=ano_atual
            ).aggregate(total=Sum('valor'))['total'] or 0,
            'mensalidades_pendentes': Mensalidade.objects.filter(status='pendente').count(),
            'casos_juridicos': AtendimentoJuridico.objects.filter(status='em_andamento').count(),
        }
        return JsonResponse(stats)
    
    return JsonResponse({'error': 'Requisição inválida'}, status=400)


class InstitucionalConfigEditView(LoginRequiredMixin, UpdateView):
    """
    View para editar configurações da página institucional
    """
    model = InstitucionalConfig
    form_class = InstitucionalConfigForm
    template_name = 'core/institucional_config_form.html'
    success_url = reverse_lazy('institucional')
    
    def get_object(self, queryset=None):
        """Retorna a configuração atual ou cria uma nova"""
        return InstitucionalConfig.get_config()
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Configuração institucional atualizada',
            modulo='Core',
            detalhes='Página institucional personalizada'
        )
        
        messages.success(self.request, 'Configurações da página institucional atualizadas com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Página Institucional'
        context['subtitle'] = 'Personalize o conteúdo da página institucional'
        
        # Adicionar estatísticas da assessoria jurídica
        context['total_noticias'] = AssejurNews.objects.count()
        context['total_informativos'] = AssejurInformativo.objects.count()
        context['noticias_ativas'] = AssejurNews.objects.filter(ativo=True).count()
        
<<<<<<< HEAD
        # Adicionar estatísticas de ex-presidentes e história
        try:
            context['total_ex_presidentes'] = ExPresidente.objects.count()
            context['ex_presidentes_ativos'] = ExPresidente.objects.filter(ativo=True).count()
        except Exception as e:
            context['total_ex_presidentes'] = 0
            context['ex_presidentes_ativos'] = 0
        
        try:
            context['total_marcos_historicos'] = HistoriaAssociacao.objects.count()
            context['marcos_historicos_ativos'] = HistoriaAssociacao.objects.filter(ativo=True).count()
            context['marcos_destaque'] = HistoriaAssociacao.objects.filter(ativo=True, destaque=True).count()
        except Exception as e:
            context['total_marcos_historicos'] = 0
            context['marcos_historicos_ativos'] = 0
            context['marcos_destaque'] = 0
        
        return context


def test_accordions(request):
    """View para testar os acordeons"""
    return render(request, 'test_accordions.html')


=======
        return context


>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
class FeedPostCreateView(LoginRequiredMixin, CreateView):
    """
    View para criar novos posts do feed
    """
    model = FeedPost
    form_class = FeedPostForm
    template_name = 'core/feedpost_form.html'
    success_url = reverse_lazy('core:institucional_edit')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Post do feed criado',
            modulo='Core',
            detalhes=f'Post "{form.instance.titulo}" criado'
        )
        
        messages.success(self.request, 'Post do feed criado com sucesso!')
        return response


class FeedPostUpdateView(LoginRequiredMixin, UpdateView):
    """
    View para editar posts do feed
    """
    model = FeedPost
    form_class = FeedPostForm
    template_name = 'core/feedpost_form.html'
    success_url = reverse_lazy('core:institucional_edit')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Post do feed atualizado',
            modulo='Core',
            detalhes=f'Post "{form.instance.titulo}" atualizado'
        )
        
        messages.success(self.request, 'Post do feed atualizado com sucesso!')
        return response


class FeedPostDeleteView(LoginRequiredMixin, DeleteView):
    """
    View para excluir posts do feed
    """
    model = FeedPost
    template_name = 'core/feedpost_confirm_delete.html'
    success_url = reverse_lazy('core:institucional_edit')
    
    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Post do feed excluído',
            modulo='Core',
            detalhes=f'Post "{post.titulo}" excluído'
        )
        
        messages.success(request, 'Post do feed excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


@login_required
def feed_post_create_ajax(request):
    """
    View AJAX para criar posts do feed
    """
    print(f"DEBUG: ===== FEED POST CREATE AJAX =====")
    print(f"DEBUG: Request method: {request.method}")
    print(f"DEBUG: User: {request.user}")
    print(f"DEBUG: User authenticated: {request.user.is_authenticated}")
    
    if request.method == 'POST':
        print(f"DEBUG: Request POST recebido")
        print(f"DEBUG: FILES: {request.FILES}")
        print(f"DEBUG: POST: {request.POST}")
        print(f"DEBUG: Content-Type: {request.content_type}")
        print(f"DEBUG: Headers: {dict(request.headers)}")
        
        try:
            print(f"DEBUG: Criando formulário com POST: {request.POST}")
            print(f"DEBUG: Criando formulário com FILES: {request.FILES}")
            
            form = FeedPostForm(request.POST, request.FILES)
            print(f"DEBUG: Formulário criado")
            print(f"DEBUG: Form fields: {list(form.fields.keys())}")
            print(f"DEBUG: Form is_valid: {form.is_valid()}")
            print(f"DEBUG: Form errors: {form.errors}")
            
            if form.is_valid():
                print(f"DEBUG: Form cleaned_data: {form.cleaned_data}")
            else:
                print(f"DEBUG: Form inválido - erros detalhados:")
                for field, errors in form.errors.items():
                    print(f"  {field}: {errors}")
            
            if form.is_valid():
                post = form.save()
                print(f"DEBUG: Post salvo com sucesso: {post.id}")
                print(f"DEBUG: Post imagem: {post.imagem}")
                print(f"DEBUG: Post imagem URL: {post.imagem.url if post.imagem else 'Sem imagem'}")
                
                # Registrar log de atividade
                try:
                    LogAtividade.objects.create(
                        usuario=request.user,
                        acao='Post do feed criado via AJAX',
                        modulo='Core',
                        detalhes=f'Post "{post.titulo}" criado'
                    )
                except Exception as e:
                    print(f"DEBUG: Erro ao criar log de atividade: {e}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Post criado com sucesso!',
                    'post': {
                        'id': post.id,
                        'titulo': post.titulo,
                        'tipo_post': post.get_tipo_post_display(),
                        'autor': post.autor,
                        'ativo': post.ativo,
                        'destaque': post.destaque,
                        'ordem_exibicao': post.ordem_exibicao,
                        'data_publicacao': post.data_publicacao.strftime('%d/%m/%Y'),
                        'imagem_url': post.imagem.url if post.imagem else None,
                    }
                })
            else:
                print(f"DEBUG: Erros do formulário: {form.errors}")
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': 'Por favor, corrija os erros no formulário.'
                })
        except Exception as e:
            print(f"DEBUG: Erro ao processar formulário: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Erro interno: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def feed_post_update_ajax(request, pk):
    """
    View AJAX para atualizar posts do feed
    """
    print(f"DEBUG: ===== FEED POST UPDATE AJAX =====")
    print(f"DEBUG: View update chamada para pk: {pk}")
    print(f"DEBUG: Tipo do pk: {type(pk)}")
    print(f"DEBUG: Request method: {request.method}")
    print(f"DEBUG: User: {request.user}")
    
    try:
        post = FeedPost.objects.get(pk=pk)
        print(f"DEBUG: Post encontrado: {post.titulo}")
        print(f"DEBUG: Post ID: {post.id}")
        print(f"DEBUG: Post ativo: {post.ativo}")
        print(f"DEBUG: Post destaque: {post.destaque}")
    except FeedPost.DoesNotExist:
        print(f"DEBUG: Post não encontrado com pk: {pk}")
        return JsonResponse({'success': False, 'message': 'Post não encontrado'})
    
    if request.method == 'POST':
        print(f"DEBUG: Request POST recebido para update")
        print(f"DEBUG: FILES: {request.FILES}")
        print(f"DEBUG: POST: {request.POST}")
        print(f"DEBUG: Content-Type: {request.content_type}")
        
        try:
            print(f"DEBUG: Criando formulário para edição com instance: {post}")
            print(f"DEBUG: POST data: {request.POST}")
            print(f"DEBUG: FILES data: {request.FILES}")
            
            form = FeedPostForm(request.POST, request.FILES, instance=post)
            print(f"DEBUG: Formulário criado para edição")
            print(f"DEBUG: Form fields: {list(form.fields.keys())}")
            print(f"DEBUG: Form is_valid: {form.is_valid()}")
            print(f"DEBUG: Form errors: {form.errors}")
            
            if form.is_valid():
                print(f"DEBUG: Form cleaned_data para edição: {form.cleaned_data}")
            else:
                print(f"DEBUG: Form inválido para edição - erros detalhados:")
                for field, errors in form.errors.items():
                    print(f"  {field}: {errors}")
            
            if form.is_valid():
                post = form.save()
                print(f"DEBUG: Post atualizado com sucesso: {post.id}")
                print(f"DEBUG: Post imagem: {post.imagem}")
                print(f"DEBUG: Post imagem URL: {post.imagem.url if post.imagem else 'Sem imagem'}")
                
                # Registrar log de atividade
                try:
                    LogAtividade.objects.create(
                        usuario=request.user,
                        acao='Post do feed atualizado via AJAX',
                        modulo='Core',
                        detalhes=f'Post "{post.titulo}" atualizado'
                    )
                except Exception as e:
                    print(f"DEBUG: Erro ao criar log de atividade: {e}")
                
                return JsonResponse({
                    'success': True,
                    'message': 'Post atualizado com sucesso!',
                    'post': {
                        'id': post.id,
                        'titulo': post.titulo,
                        'tipo_post': post.get_tipo_post_display(),
                        'autor': post.autor,
                        'ativo': post.ativo,
                        'destaque': post.destaque,
                        'ordem_exibicao': post.ordem_exibicao,
                        'data_publicacao': post.data_publicacao.strftime('%d/%m/%Y'),
                        'imagem_url': post.imagem.url if post.imagem else None,
                    }
                })
            else:
                print(f"DEBUG: Erros do formulário: {form.errors}")
                return JsonResponse({
                    'success': False,
                    'errors': form.errors,
                    'message': 'Por favor, corrija os erros no formulário.'
                })
        except Exception as e:
            print(f"DEBUG: Erro ao processar formulário: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'success': False,
                'message': f'Erro interno: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def feed_post_delete_ajax(request, pk):
    """
    View AJAX para excluir posts do feed
    """
    try:
        post = FeedPost.objects.get(pk=pk)
    except FeedPost.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Post não encontrado'})
    
    if request.method == 'POST':
        titulo = post.titulo
        post.delete()
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Post do feed excluído via AJAX',
            modulo='Core',
            detalhes=f'Post "{titulo}" excluído'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Post excluído com sucesso!'
        })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def feed_posts_list_ajax(request):
    """
    View AJAX para listar posts do feed
    """
    print(f"DEBUG: Listando posts do feed")
    posts = FeedPost.objects.filter(ativo=True).order_by('-destaque', '-ordem_exibicao', '-data_publicacao')[:10]
    print(f"DEBUG: Posts encontrados: {posts.count()}")
    
    posts_data = []
    for post in posts:
        post_data = {
            'id': post.id,
            'titulo': post.titulo,
            'conteudo': post.conteudo,
            'tipo_post': post.tipo_post,
            'tipo_post_display': post.get_tipo_post_display(),
            'autor': post.autor,
            'ativo': post.ativo,
            'destaque': post.destaque,
            'ordem_exibicao': post.ordem_exibicao,
            'data_publicacao': post.data_publicacao.strftime('%d/%m/%Y'),
            'tempo_relativo': post.get_tempo_relativo(),
            'likes': post.likes,
            'comentarios': post.comentarios,
            'compartilhamentos': post.compartilhamentos,
            'imagem_url': post.imagem.url if post.imagem else None,
        }
        posts_data.append(post_data)
        print(f"DEBUG: Post {post.id}: {post.titulo}")
    
    print(f"DEBUG: Total de posts retornados: {len(posts_data)}")
    return JsonResponse({'posts': posts_data})


<<<<<<< HEAD
@login_required
def feed_posts_list(request):
    """
    View para listar posts do feed (HTML)
    """
    posts = FeedPost.objects.all().order_by('-destaque', '-ordem_exibicao', '-data_publicacao')
    context = {
        'posts': posts,
        'title': 'Gerenciar Feed Social',
        'subtitle': 'Gerencie os posts do feed social da ABMEPI'
    }
    return render(request, 'core/feed_posts_list.html', context)


@login_required
def feed_post_create(request):
    """
    View para criar posts do feed (HTML)
    """
    if request.method == 'POST':
        form = FeedPostForm(request.POST, request.FILES)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user.get_full_name() or request.user.username
            post.save()
            
            # Registrar log de atividade
            LogAtividade.objects.create(
                usuario=request.user,
                acao='Post do feed criado',
                modulo='Core',
                detalhes=f'Post "{post.titulo}" criado'
            )
            
            messages.success(request, 'Post criado com sucesso!')
            return redirect('core:feed_posts_list')
        else:
            # Exibir erros específicos do formulário
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = FeedPostForm(initial={'autor': request.user.get_full_name() or request.user.username})
    
    context = {
        'form': form,
        'title': 'Criar Post do Feed',
        'subtitle': 'Crie um novo post para o feed social da ABMEPI'
    }
    return render(request, 'core/feed_post_form.html', context)


=======
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
def post_like_ajax(request, post_id):
    """
    View AJAX para curtir/descurtir posts (aberto para todos)
    """
    
    if request.method == 'POST':
        try:
            post = get_object_or_404(FeedPost, id=post_id)
            
            # Para usuários autenticados, usar o modelo Like normal
            if request.user.is_authenticated:
                like_exists = Like.objects.filter(post=post, usuario=request.user).first()
                
                if like_exists:
                    # Descurtir - remover like
                    like_exists.delete()
                    liked = False
                    action = 'descurtiu'
                else:
                    # Curtir - adicionar like
                    Like.objects.create(post=post, usuario=request.user)
                    liked = True
                    action = 'curtiu'
                
                # Registrar log de atividade
                LogAtividade.objects.create(
                    usuario=request.user,
                    acao=f'Post {action}',
                    modulo='Core',
                    detalhes=f'Post "{post.titulo}" {action} pelo usuário'
                )
            else:
                # Para usuários anônimos, usar sessão e persistir no banco
                session_likes = request.session.get('post_likes', {})
                post_id_str = str(post_id)
                
                # Garantir que a sessão tenha uma chave
                if not request.session.session_key:
                    request.session.create()
                
                if post_id_str in session_likes:
                    # Descurtir - remover da sessão e do banco
                    del session_likes[post_id_str]
                    liked = False
                    action = 'descurtiu'
                    
                    # Remover like anônimo do banco
                    from core.models import LikeAnonimo
                    LikeAnonimo.objects.filter(
                        post=post,
                        session_key=request.session.session_key
                    ).delete()
                else:
                    # Curtir - adicionar na sessão e no banco
                    session_likes[post_id_str] = True
                    liked = True
                    action = 'curtiu'
                    
                    # Criar like anônimo no banco
                    from core.models import LikeAnonimo
                    LikeAnonimo.objects.create(
                        post=post,
                        session_key=request.session.session_key,
                        nome_anonimo=request.session.get('nome_anonimo', 'Visitante')
                    )
                
                request.session['post_likes'] = session_likes
                request.session.modified = True
            
            # Sincronizar contadores do post
            post.sync_counters()
            
            # Contar likes atuais incluindo sessão
            likes_count = post.get_likes_count()
            
            return JsonResponse({
                'success': True,
                'liked': liked,
                'likes_count': likes_count,
                'message': f'Post {action} com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao processar like: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


def post_comment_ajax(request, post_id):
    """
    View AJAX para adicionar comentários (aberto para todos)
    """
    
    if request.method == 'POST':
        try:
            post = get_object_or_404(FeedPost, id=post_id)
            conteudo = request.POST.get('conteudo', '').strip()
            nome_usuario = request.POST.get('nome_usuario', '').strip()
            
            if not conteudo:
                return JsonResponse({
                    'success': False,
                    'message': 'Comentário não pode estar vazio'
                })
            
            if len(conteudo) < 3:
                return JsonResponse({
                    'success': False,
                    'message': 'Comentário deve ter pelo menos 3 caracteres'
                })
            
            # Para usuários anônimos, validar nome
            if not request.user.is_authenticated:
                if not nome_usuario:
                    return JsonResponse({
                        'success': False,
                        'message': 'Nome é obrigatório'
                    })
                if len(nome_usuario) < 2:
                    return JsonResponse({
                        'success': False,
                        'message': 'Nome deve ter pelo menos 2 caracteres'
                    })
            
            # Criar novo comentário
            # Para usuários autenticados, usar o usuário atual
            # Para usuários anônimos, usar None e salvar o nome
            if request.user.is_authenticated:
                comentario = Comentario.objects.create(
                    post=post,
                    usuario=request.user,
                    conteudo=conteudo
                )
            else:
                comentario = Comentario.objects.create(
                    post=post,
                    usuario=None,
                    nome_anonimo=nome_usuario,
                    conteudo=conteudo
                )
            
            # Sincronizar contadores do post
            counters = post.sync_counters()
            comments_count = counters['comentarios']
            
            # Registrar log de atividade (apenas para usuários autenticados)
            if request.user.is_authenticated:
                LogAtividade.objects.create(
                    usuario=request.user,
                    acao='Comentário adicionado',
                    modulo='Core',
                    detalhes=f'Comentário adicionado no post "{post.titulo}"'
                )
            
            return JsonResponse({
                'success': True,
                'comments_count': comments_count,
                'comment': {
                    'id': comentario.id,
                    'conteudo': comentario.conteudo,
                    'usuario_nome': comentario.get_author_name(),
                    'tempo_relativo': comentario.get_tempo_relativo(),
                    'data_criacao': comentario.data_criacao.strftime('%d/%m/%Y %H:%M')
                },
                'message': 'Comentário adicionado com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao adicionar comentário: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


def post_comments_list_ajax(request, post_id):
    """
    View AJAX para listar comentários de um post
    """
    try:
        post = get_object_or_404(FeedPost, id=post_id)
        comentarios = post.comentario_set.filter(ativo=True).select_related('usuario').order_by('data_criacao')
        
        comments_data = []
        for comentario in comentarios:
            comment_data = {
                'id': comentario.id,
                'conteudo': comentario.conteudo,
                'usuario_nome': comentario.get_author_name(),
                'tempo_relativo': comentario.get_tempo_relativo(),
                'data_criacao': comentario.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'can_edit': comentario.usuario == request.user if comentario.usuario else False  # Usuário pode editar apenas seus comentários
            }
            comments_data.append(comment_data)
        
        return JsonResponse({
            'success': True,
            'comments': comments_data,
            'comments_count': len(comments_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao carregar comentários: {str(e)}'
        })


# ============================================================================
# VIEWS PARA ASSESSORIA JURÍDICA (ASSEJUR)
# ============================================================================

class AssejurNewsListView(LoginRequiredMixin, ListView):
    """
    View para listar notícias da assessoria jurídica
    """
    model = AssejurNews
    template_name = 'core/assejur_news_list.html'
    context_object_name = 'noticias'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AssejurNews.objects.all().order_by('-destaque', '-ordem_exibicao', '-data_publicacao')
        
        # Filtros
        categoria = self.request.GET.get('categoria')
        if categoria:
            queryset = queryset.filter(categoria=categoria)
        
        prioridade = self.request.GET.get('prioridade')
        if prioridade:
            queryset = queryset.filter(prioridade=prioridade)
        
        ativo = self.request.GET.get('ativo')
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo == 'true')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Notícias da Assessoria Jurídica'
        context['subtitle'] = 'Gerencie as notícias jurídicas do sistema'
        context['categorias'] = AssejurNews.CATEGORIA_CHOICES
        context['prioridades'] = AssejurNews.PRIORIDADE_CHOICES
        return context


class AssejurNewsCreateView(LoginRequiredMixin, CreateView):
    """
    View para criar novas notícias da assessoria jurídica
    """
    model = AssejurNews
    form_class = AssejurNewsForm
    template_name = 'core/assejur_news_form.html'
    success_url = reverse_lazy('core:assejur_news_list')
    
    def form_valid(self, form):
        form.instance.autor = self.request.user
        response = super().form_valid(form)
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Notícia ASSEJUR criada',
            modulo='Core',
            detalhes=f'Notícia "{form.instance.titulo}" criada'
        )
        
        messages.success(self.request, 'Notícia da assessoria jurídica criada com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nova Notícia Jurídica'
        context['subtitle'] = 'Crie uma nova notícia para a assessoria jurídica'
        context['action'] = 'create'
        return context


class AssejurNewsUpdateView(LoginRequiredMixin, UpdateView):
    """
    View para editar notícias da assessoria jurídica
    """
    model = AssejurNews
    form_class = AssejurNewsForm
    template_name = 'core/assejur_news_form.html'
    success_url = reverse_lazy('core:assejur_news_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Notícia ASSEJUR atualizada',
            modulo='Core',
            detalhes=f'Notícia "{form.instance.titulo}" atualizada'
        )
        
        messages.success(self.request, 'Notícia da assessoria jurídica atualizada com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Notícia Jurídica'
        context['subtitle'] = 'Edite os dados da notícia'
        context['action'] = 'update'
        return context


class AssejurNewsDeleteView(LoginRequiredMixin, DeleteView):
    """
    View para excluir notícias da assessoria jurídica
    """
    model = AssejurNews
    template_name = 'core/assejur_news_confirm_delete.html'
    success_url = reverse_lazy('core:assejur_news_list')
    
    def delete(self, request, *args, **kwargs):
        noticia = self.get_object()
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Notícia ASSEJUR excluída',
            modulo='Core',
            detalhes=f'Notícia "{noticia.titulo}" excluída'
        )
        
        messages.success(request, 'Notícia da assessoria jurídica excluída com sucesso!')
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Excluir Notícia Jurídica'
        context['subtitle'] = 'Confirme a exclusão da notícia'
        return context


class AssejurInformativoListView(LoginRequiredMixin, ListView):
    """
    View para listar informativos da assessoria jurídica
    """
    model = AssejurInformativo
    template_name = 'core/assejur_informativo_list.html'
    context_object_name = 'informativos'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = AssejurInformativo.objects.all().order_by('-ordem_exibicao', '-data_criacao')
        
        # Filtros
        prioridade = self.request.GET.get('prioridade')
        if prioridade:
            queryset = queryset.filter(prioridade=prioridade)
        
        ativo = self.request.GET.get('ativo')
        if ativo is not None:
            queryset = queryset.filter(ativo=ativo == 'true')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Informativos da Assessoria Jurídica'
        context['subtitle'] = 'Gerencie os informativos jurídicos do sistema'
        context['prioridades'] = AssejurInformativo.PRIORIDADE_CHOICES
        return context


class AssejurInformativoCreateView(LoginRequiredMixin, CreateView):
    """
    View para criar novos informativos da assessoria jurídica
    """
    model = AssejurInformativo
    form_class = AssejurInformativoForm
    template_name = 'core/assejur_informativo_form.html'
    success_url = reverse_lazy('core:assejur_informativo_list')
    
    def form_valid(self, form):
        form.instance.autor = self.request.user
        response = super().form_valid(form)
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Informativo ASSEJUR criado',
            modulo='Core',
            detalhes=f'Informativo "{form.instance.titulo}" criado'
        )
        
        messages.success(self.request, 'Informativo da assessoria jurídica criado com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Novo Informativo Jurídico'
        context['subtitle'] = 'Crie um novo informativo para a assessoria jurídica'
        context['action'] = 'create'
        return context


class AssejurInformativoUpdateView(LoginRequiredMixin, UpdateView):
    """
    View para editar informativos da assessoria jurídica
    """
    model = AssejurInformativo
    form_class = AssejurInformativoForm
    template_name = 'core/assejur_informativo_form.html'
    success_url = reverse_lazy('core:assejur_informativo_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Informativo ASSEJUR atualizado',
            modulo='Core',
            detalhes=f'Informativo "{form.instance.titulo}" atualizado'
        )
        
        messages.success(self.request, 'Informativo da assessoria jurídica atualizado com sucesso!')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Editar Informativo Jurídico'
        context['subtitle'] = 'Edite os dados do informativo'
        context['action'] = 'update'
        return context


class AssejurInformativoDeleteView(LoginRequiredMixin, DeleteView):
    """
    View para excluir informativos da assessoria jurídica
    """
    model = AssejurInformativo
    template_name = 'core/assejur_informativo_confirm_delete.html'
    success_url = reverse_lazy('core:assejur_informativo_list')
    
    def delete(self, request, *args, **kwargs):
        informativo = self.get_object()
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Informativo ASSEJUR excluído',
            modulo='Core',
            detalhes=f'Informativo "{informativo.titulo}" excluído'
        )
        
        messages.success(request, 'Informativo da assessoria jurídica excluído com sucesso!')
        return super().delete(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Excluir Informativo Jurídico'
        context['subtitle'] = 'Confirme a exclusão do informativo'
        return context


# Views AJAX para operações rápidas
def assejur_news_toggle_status_ajax(request, pk):
    """
    View AJAX para alternar status ativo/inativo de notícias
    """
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            noticia = get_object_or_404(AssejurNews, pk=pk)
            noticia.ativo = not noticia.ativo
            noticia.save()
            
            # Registrar log de atividade
            LogAtividade.objects.create(
                usuario=request.user,
                acao='Status da notícia ASSEJUR alterado',
                modulo='Core',
                detalhes=f'Notícia "{noticia.titulo}" - Status: {"Ativo" if noticia.ativo else "Inativo"}'
            )
            
            return JsonResponse({
                'success': True,
                'ativo': noticia.ativo,
                'message': f'Notícia {"ativada" if noticia.ativo else "desativada"} com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao alterar status: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Requisição inválida'})


def assejur_informativo_toggle_status_ajax(request, pk):
    """
    View AJAX para alternar status ativo/inativo de informativos
    """
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            informativo = get_object_or_404(AssejurInformativo, pk=pk)
            informativo.ativo = not informativo.ativo
            informativo.save()
            
            # Registrar log de atividade
            LogAtividade.objects.create(
                usuario=request.user,
                acao='Status do informativo ASSEJUR alterado',
                modulo='Core',
                detalhes=f'Informativo "{informativo.titulo}" - Status: {"Ativo" if informativo.ativo else "Inativo"}'
            )
            
            return JsonResponse({
                'success': True,
                'ativo': informativo.ativo,
                'message': f'Informativo {"ativado" if informativo.ativo else "desativado"} com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao alterar status: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Requisição inválida'})


def assejur_news_detail(request, pk):
    """
    View para exibir notícia completa da assessoria jurídica
    """
    noticia = get_object_or_404(AssejurNews, pk=pk, ativo=True)
    
    # Incrementar visualizações
    noticia.incrementar_visualizacoes()
    
    # Obter comentários ativos da notícia
    comentarios = noticia.get_comentarios_ativos()
    
    # Registrar log de atividade se usuário autenticado
    if request.user.is_authenticated:
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Notícia ASSEJUR visualizada',
            modulo='Core',
            detalhes=f'Notícia "{noticia.titulo}" visualizada'
        )
    
    context = {
        'noticia': noticia,
        'comentarios': comentarios,
        'total_comentarios': len(comentarios),
        'title': noticia.titulo,
        'subtitle': f'Categoria: {noticia.get_categoria_display()} - {noticia.get_tempo_relativo()}',
    }
    
    return render(request, 'core/assejur_news_detail.html', context)


def assejur_news_public_list(request):
    """
    View pública para listar notícias jurídicas (sem login)
    """
    # Obter notícias ativas ordenadas por destaque e data
    noticias = AssejurNews.objects.filter(
        ativo=True
    ).order_by('-destaque', '-ordem_exibicao', '-data_publicacao')
    
    # Filtros opcionais
    categoria = request.GET.get('categoria')
    if categoria:
        noticias = noticias.filter(categoria=categoria)
    
    # Paginação
    from django.core.paginator import Paginator
    paginator = Paginator(noticias, 12)  # 12 notícias por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'noticias': page_obj,
        'page_obj': page_obj,
        'categorias': AssejurNews.CATEGORIA_CHOICES,
        'title': 'Portal de Notícias Jurídicas',
        'subtitle': 'Assessoria Jurídica ABMEPI - Informações e Atualizações',
        'config': InstitucionalConfig.get_config(),
    }
    
    return render(request, 'core/assejur_news_public_list.html', context)


<<<<<<< HEAD
def assejur_news_content_ajax(request, noticia_id):
    """
    View AJAX para retornar o conteúdo completo de uma notícia
    """
    try:
        noticia = get_object_or_404(AssejurNews, id=noticia_id, ativo=True)
        
        return JsonResponse({
            'success': True,
            'conteudo': noticia.conteudo or noticia.resumo,
            'titulo': noticia.titulo,
            'categoria': noticia.get_categoria_display(),
            'prioridade': noticia.get_prioridade_display(),
            'data_publicacao': noticia.data_publicacao.strftime('%d/%m/%Y') if noticia.data_publicacao else '',
            'imagem': noticia.imagem.url if noticia.imagem else None,
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


=======
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
def post_share_ajax(request, post_id):
    """
    View AJAX para compartilhar posts (aberto para todos)
    """
    
    if request.method == 'POST':
        try:
            post = get_object_or_404(FeedPost, id=post_id)
            
            # Incrementar contador de compartilhamentos
            post.compartilhamentos += 1
            post.save(update_fields=['compartilhamentos'])
            
            # Registrar log de atividade (apenas para usuários autenticados)
            if request.user.is_authenticated:
                LogAtividade.objects.create(
                    usuario=request.user,
                    acao='Post compartilhado',
                    modulo='Core',
                    detalhes=f'Post "{post.titulo}" compartilhado pelo usuário'
                )
            
            return JsonResponse({
                'success': True,
                'shares_count': post.compartilhamentos,
                'message': 'Post compartilhado com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao compartilhar post: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


def assejur_news_comment_ajax(request, news_id):
    """
    View AJAX para adicionar comentários às notícias ASSEJUR
    """
    if request.method == 'POST':
        try:
            noticia = get_object_or_404(AssejurNews, id=news_id, ativo=True)
            
            # Obter dados do formulário
            conteudo = request.POST.get('conteudo', '').strip()
            nome_anonimo = request.POST.get('nome_anonimo', '').strip()
            
            if not conteudo:
                return JsonResponse({
                    'success': False,
                    'message': 'O comentário não pode estar vazio.'
                })
            
            # Criar comentário
            comentario = AssejurNewsComentario.objects.create(
                noticia=noticia,
                usuario=request.user if request.user.is_authenticated else None,
                nome_anonimo=nome_anonimo if not request.user.is_authenticated else None,
                conteudo=conteudo
            )
            
            # Retornar dados do comentário criado
            comentario_data = {
                'id': comentario.id,
                'conteudo': comentario.conteudo,
                'data_criacao': comentario.data_criacao.strftime('%d/%m/%Y %H:%M'),
                'author_name': comentario.get_author_name(),
                'time_ago': comentario.get_tempo_relativo(),
                'content': comentario.conteudo,
                'is_authenticated': comentario.usuario is not None
            }
            
            return JsonResponse({
                'success': True,
                'message': 'Comentário adicionado com sucesso!',
                'comentario': comentario_data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao adicionar comentário: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


def assejur_news_view_increment_ajax(request, news_id):
    """
    View AJAX para incrementar visualizações de notícias ASSEJUR
    """
    if request.method == 'POST':
        try:
            noticia = get_object_or_404(AssejurNews, id=news_id, ativo=True)
            
            # Incrementar visualizações
            noticia.incrementar_visualizacoes()
            
            # Registrar log de atividade se usuário autenticado
            if request.user.is_authenticated:
                LogAtividade.objects.create(
                    usuario=request.user,
                    acao='Notícia ASSEJUR visualizada (modal)',
                    modulo='Core',
                    detalhes=f'Notícia "{noticia.titulo}" visualizada via modal'
                )
            
            return JsonResponse({
                'success': True,
                'visualizacoes': noticia.visualizacoes,
                'message': 'Visualização registrada com sucesso!'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao registrar visualização: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


def assejur_news_comments_list_ajax(request, news_id):
    """
    View AJAX para listar comentários de uma notícia ASSEJUR
    """
    try:
        noticia = get_object_or_404(AssejurNews, id=news_id, ativo=True)
        comentarios = noticia.get_comentarios_ativos()
        
        comments_data = []
        for comentario in comentarios:
            comments_data.append({
                'id': comentario.id,
                'author_name': comentario.get_author_name(),
                'content': comentario.conteudo,
                'time_ago': comentario.get_tempo_relativo(),
                'is_authenticated': comentario.usuario is not None
            })
        
        return JsonResponse({
            'success': True,
            'comments': comments_data,
            'total_comments': len(comments_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erro ao carregar comentários: {str(e)}'
        })


@login_required
def marcar_notificacoes_como_lidas_ajax(request):
    """
    View AJAX para marcar todas as notificações pendentes do usuário como lidas
    """
    if request.method == 'POST':
        try:
            from django.utils import timezone
            
            # Marcar todas as notificações pendentes do usuário como lidas
            notificacoes_atualizadas = Notificacao.objects.filter(
                usuario_destino=request.user,
                status='pendente'
            ).update(
                status='lida',
                data_leitura=timezone.now()
            )
            
            return JsonResponse({
                'success': True,
                'message': f'{notificacoes_atualizadas} notificações marcadas como lidas',
                'notificacoes_atualizadas': notificacoes_atualizadas
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao marcar notificações como lidas: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def marcar_notificacao_como_lida_ajax(request, notificacao_id):
    """
    View AJAX para marcar uma notificação específica como lida
    """
    if request.method == 'POST':
        try:
            # Buscar a notificação específica do usuário
            notificacao = get_object_or_404(
                Notificacao, 
                id=notificacao_id, 
                usuario_destino=request.user
            )
            
            # Marcar como lida se ainda estiver pendente
            if notificacao.status == 'pendente':
                notificacao.marcar_como_lida()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Notificação marcada como lida',
                    'notificacao_id': notificacao.id
                })
            else:
                return JsonResponse({
                    'success': True,
                    'message': 'Notificação já estava marcada como lida',
                    'notificacao_id': notificacao.id
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erro ao marcar notificação como lida: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Método não permitido'})


@login_required
def notificacao_invalida(request, notificacao_id):
    """
    View para tratar notificações que referenciam objetos que não existem mais
    """
    from django.contrib import messages
    
    try:
        # Buscar a notificação
        notificacao = get_object_or_404(
            Notificacao, 
            id=notificacao_id, 
            usuario_destino=request.user
        )
        
        # Marcar como lida
        if notificacao.status == 'pendente':
            notificacao.marcar_como_lida()
        
        # Mostrar mensagem apropriada baseada no tipo de objeto
        if notificacao.objeto_tipo == 'Comunicado':
            messages.warning(request, 'O comunicado referenciado nesta notificação não existe mais ou foi removido.')
            return redirect('administrativo:comunicado_list')
        else:
            messages.warning(request, 'O conteúdo referenciado nesta notificação não existe mais ou foi removido.')
            return redirect('core:dashboard')
            
    except Exception as e:
        messages.error(request, 'Erro ao processar notificação.')
        return redirect('core:dashboard')


class LegislacaoView(TemplateView):
    """
    View para a página de legislação com arquivos para download
    """
    template_name = 'core/legislacao.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dados de exemplo para legislação (pode ser expandido com um modelo real)
        context['legislacoes'] = {
            'leis_estaduais': [
                {
                    'titulo': 'Lei Estadual nº 123/2020',
                    'descricao': 'Dispõe sobre direitos e deveres dos bombeiros militares',
                    'categoria': 'Lei Estadual',
                    'data_publicacao': '15/03/2020',
                    'arquivo': 'lei_123_2020.pdf',
                    'tamanho': '2.5 MB'
                },
                {
                    'titulo': 'Lei Estadual nº 456/2019',
                    'descricao': 'Estabelece normas para policiais militares',
                    'categoria': 'Lei Estadual',
                    'data_publicacao': '22/08/2019',
                    'arquivo': 'lei_456_2019.pdf',
                    'tamanho': '1.8 MB'
                }
            ],
            'decretos': [
                {
                    'titulo': 'Decreto nº 789/2021',
                    'descricao': 'Regulamenta benefícios para militares',
                    'categoria': 'Decreto',
                    'data_publicacao': '10/05/2021',
                    'arquivo': 'decreto_789_2021.pdf',
                    'tamanho': '3.2 MB'
                }
            ],
            'regulamentos': [
                {
                    'titulo': 'Regulamento de Uniformes',
                    'descricao': 'Normas para uso de uniformes militares',
                    'categoria': 'Regulamento',
                    'data_publicacao': '05/12/2020',
                    'arquivo': 'regulamento_uniformes.pdf',
                    'tamanho': '1.5 MB'
                }
            ],
            'portarias': [
                {
                    'titulo': 'Portaria nº 001/2022',
                    'descricao': 'Instruções para procedimentos administrativos',
                    'categoria': 'Portaria',
                    'data_publicacao': '20/01/2022',
                    'arquivo': 'portaria_001_2022.pdf',
                    'tamanho': '0.8 MB'
                }
            ]
        }
        
        return context


def logout_view(request):
    """
    View para fazer logout do usuário
    """
    from django.contrib.auth import logout
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('login')


@login_required
def usuario_search_cpf(request):
    """Buscar usuários por CPF para autocompletar"""
    query = request.GET.get('q', '').strip()
    
    if not query or len(query) < 3:
        return JsonResponse({'results': []})
    
    # Buscar usuários que contenham o CPF digitado
    usuarios = Usuario.objects.filter(
        username__icontains=query
    ).values('username', 'first_name', 'last_name', 'email')[:10]
    
    results = []
    for usuario in usuarios:
        results.append({
            'cpf': usuario['username'],
            'nome': f"{usuario['first_name']} {usuario['last_name']}".strip(),
            'email': usuario['email']
        })
    
    return JsonResponse({'results': results})


@login_required
def redefinir_senha_usuario(request, pk):
    """
    View para administradores redefinirem a senha de um usuário
    """
    # Verificar se o usuário é administrador do sistema
    if request.user.tipo_usuario != 'administrador_sistema':
        messages.error(request, 'Acesso negado. Apenas administradores do sistema podem redefinir senhas.')
        return redirect('core:usuario_list')
    
    try:
        usuario = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        messages.error(request, 'Usuário não encontrado.')
        return redirect('core:usuario_list')
    
    if request.method == 'POST':
        # Gerar nova senha única
        senha_nova = gerar_senha_unica()
        
        # Alterar a senha do usuário
        usuario.set_password(senha_nova)
        
        # Armazenar senha temporária para visualização de administradores
        from django.utils import timezone
        from datetime import timedelta
        
        usuario.senha_temporaria = senha_nova
        usuario.senha_temporaria_expira = timezone.now() + timedelta(hours=24)  # Expira em 24 horas
        usuario.save()
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Senha redefinida',
            modulo='Core',
            detalhes=f'Senha do usuário {usuario.username} redefinida pelo administrador'
        )
        
        messages.success(
            request, 
            f'Senha do usuário <strong>{usuario.get_full_name()}</strong> redefinida com sucesso! '
            f'Nova senha: <strong>{senha_nova}</strong> - '
            f'Informe esta senha ao usuário para o próximo acesso.'
        )
        
        return redirect('core:usuario_update', pk=pk)
    
    # GET request - mostrar confirmação
    context = {
        'usuario': usuario,
        'title': 'Redefinir Senha',
        'subtitle': f'Confirmar redefinição de senha para {usuario.get_full_name()}'
    }
    
    return render(request, 'core/redefinir_senha_confirm.html', context)


def gerar_senha_unica():
    """Gera uma senha única e segura"""
    import secrets
    import string
    
    # Padrão: 2 letras maiúsculas + 2 letras minúsculas + 2 números + 2 caracteres especiais
    letras_maiusculas = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(2))
    letras_minusculas = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(2))
    numeros = ''.join(secrets.choice(string.digits) for _ in range(2))
    caracteres_especiais = ''.join(secrets.choice('!@#$%^&*') for _ in range(2))
    
    # Combinar e embaralhar
    senha = letras_maiusculas + letras_minusculas + numeros + caracteres_especiais
    senha_lista = list(senha)
    secrets.SystemRandom().shuffle(senha_lista)
    
    return ''.join(senha_lista)


# ==================== VIEWS PARA GERENCIAMENTO DE EMAILS EM LOTE ====================

@login_required
def email_batch_dashboard(request):
    """
    Dashboard para gerenciamento de emails em lote
    """
    from .services.email_service import email_batch_service
    from associados.models import Associado
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Estatísticas
    total_associados = Associado.objects.filter(email__isnull=False).exclude(email='').count()
    associados_ativos = Associado.objects.filter(
        email__isnull=False, 
        email__gt='', 
        situacao='ativo'
    ).count()
    total_usuarios = User.objects.filter(email__isnull=False).exclude(email='').count()
    usuarios_ativos = User.objects.filter(
        email__isnull=False, 
        email__gt='', 
        is_active=True
    ).count()
    
    # Lista de usuários para seleção
    usuarios_disponiveis = User.objects.filter(
        email__isnull=False
    ).exclude(email='').order_by('first_name', 'last_name', 'username')
    
    context = {
        'title': 'Envio de Emails em Lote',
        'subtitle': 'Gerenciar envio de emails para associados e usuários',
        'total_associados': total_associados,
        'associados_ativos': associados_ativos,
        'total_usuarios': total_usuarios,
        'usuarios_ativos': usuarios_ativos,
        'usuarios_disponiveis': usuarios_disponiveis,
    }
    
    return render(request, 'core/email_batch_dashboard.html', context)


@login_required
def email_batch_send(request):
    """
    View para envio de emails em lote
    """
    from .services.email_service import email_batch_service
    
    if request.method == 'POST':
        recipient_type = request.POST.get('recipient_type')
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        html_message = request.POST.get('html_message', '').strip()
        selected_users = request.POST.getlist('selected_users')
        
        # Processar anexos
        attachments = []
        for file in request.FILES.getlist('attachments'):
            if file:
                attachments.append({
                    'filename': file.name,
                    'content': file.read(),
                    'mimetype': file.content_type
                })
        
        # Validações
        if not subject:
            messages.error(request, 'O assunto é obrigatório.')
            return redirect('core:email_batch_dashboard')
        
        if not message and not html_message:
            messages.error(request, 'A mensagem é obrigatória.')
            return redirect('core:email_batch_dashboard')
        
        try:
            
            # Envio em lote
            result = None
            
            if recipient_type == 'associados_ativos':
                result = email_batch_service.send_to_all_associados(
                    subject=subject,
                    message=message,
                    html_message=html_message if html_message else None,
                    filter_active=True,
                    attachments=attachments if attachments else None
                )
            elif recipient_type == 'associados_todos':
                result = email_batch_service.send_to_all_associados(
                    subject=subject,
                    message=message,
                    html_message=html_message if html_message else None,
                    filter_active=False,
                    attachments=attachments if attachments else None
                )
            elif recipient_type == 'usuarios_ativos':
                result = email_batch_service.send_to_all_users(
                    subject=subject,
                    message=message,
                    html_message=html_message if html_message else None,
                    filter_active=True,
                    attachments=attachments if attachments else None
                )
            elif recipient_type == 'usuarios_todos':
                result = email_batch_service.send_to_all_users(
                    subject=subject,
                    message=message,
                    html_message=html_message if html_message else None,
                    filter_active=False,
                    attachments=attachments if attachments else None
                )
            elif recipient_type == 'usuarios_especificos':
                if not selected_users:
                    messages.error(request, 'Selecione pelo menos um usuário para envio específico.')
                    return redirect('core:email_batch_dashboard')
                
                user_ids = [int(user_id) for user_id in selected_users]
                result = email_batch_service.send_to_specific_users(
                    user_ids=user_ids,
                    subject=subject,
                    message=message,
                    html_message=html_message if html_message else None,
                    attachments=attachments if attachments else None
                )
            elif recipient_type == 'custom':
                email_list = request.POST.get('email_list', '').strip()
                if not email_list:
                    messages.error(request, 'Lista de emails é obrigatória para envio customizado.')
                    return redirect('core:email_batch_dashboard')
                
                # Converter string de emails em lista
                emails = [email.strip() for email in email_list.split('\n') if email.strip()]
                result = email_batch_service.send_to_custom_list(
                    email_list=emails,
                    subject=subject,
                    message=message,
                    html_message=html_message if html_message else None,
                    attachments=attachments if attachments else None
                )
            
            if result:
                # Registrar log de atividade
                LogAtividade.objects.create(
                    usuario=request.user,
                    acao='Envio de emails em lote',
                    modulo='Core',
                    detalhes=f'Enviados {result["successful_sends"]}/{result["total_recipients"]} emails. Assunto: {subject}'
                )
                
                messages.success(
                    request, 
                    f'Envio concluído! {result["successful_sends"]}/{result["total_recipients"]} emails enviados com sucesso. '
                    f'Taxa de sucesso: {result["success_rate"]:.1f}%'
                )
                
                if result['failed_emails']:
                    messages.warning(
                        request, 
                        f'{result["failed_sends"]} emails falharam. Verifique os logs para mais detalhes.'
                    )
            
        except Exception as e:
            messages.error(request, f'Erro ao enviar emails: {str(e)}')
            logger.error(f"Erro no envio de emails em lote: {str(e)}")
        
        return redirect('core:email_batch_dashboard')
    
    return redirect('core:email_batch_dashboard')


@login_required
def email_batch_preview(request):
    """
    Preview do email antes do envio
    """
    if request.method == 'POST':
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        html_message = request.POST.get('html_message', '').strip()
        
        context = {
            'title': 'Preview do Email',
            'subtitle': 'Visualização do email antes do envio',
            'subject': subject,
            'message': message,
            'html_message': html_message,
        }
        
        return render(request, 'core/email_batch_preview.html', context)
    
    return redirect('core:email_batch_dashboard')


@login_required
def email_batch_history(request):
    """
    Histórico de envios de email
    """
    from django.core.paginator import Paginator
    
    # Buscar logs de envio de emails
    logs = LogAtividade.objects.filter(
        acao__icontains='email',
        modulo='Core'
    ).order_by('-data_hora')
    
    paginator = Paginator(logs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Histórico de Emails',
        'subtitle': 'Log de envios de emails em lote',
        'page_obj': page_obj,
    }
    
    return render(request, 'core/email_batch_history.html', context)
<<<<<<< HEAD


class ExPresidentesView(TemplateView):
    """
    View para exibir a galeria de ex-presidentes
    """
    template_name = 'core/ex_presidentes.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Buscar ex-presidentes ativos ordenados por data mais recente primeiro
        ex_presidentes = ExPresidente.objects.filter(ativo=True).order_by('-periodo_inicio', 'ordem_exibicao')
        
        # Buscar presidente atual da diretoria
        from diretoria.models import MembroDiretoria
        presidente_atual = MembroDiretoria.get_presidente_atual()
        
        context.update({
            'ex_presidentes': ex_presidentes,
            'presidente_atual': presidente_atual,
            'title': 'Galeria de Ex-Presidentes',
            'subtitle': 'Conheça a história de liderança da ABMEPI',
        })
        
        return context


class HistoriaAssociacaoView(TemplateView):
    """
    View para exibir a história da associação
    """
    template_name = 'core/historia_associacao.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Buscar marcos históricos ativos ordenados por ordem de exibição
        marcos_historicos = HistoriaAssociacao.objects.filter(ativo=True).order_by('ordem_exibicao', 'data_marcante')
        
        # Buscar imagens da galeria para cada marco histórico usando prefetch_related
        marcos_historicos = marcos_historicos.prefetch_related(
            Prefetch(
                'galeria_imagens',
                queryset=HistoriaImagem.objects.filter(ativo=True).order_by('ordem_exibicao', 'created_at')
            )
        )
        
        # Separar por tipo para melhor organização
        marcos_por_tipo = {}
        for marco in marcos_historicos:
            tipo = marco.get_tipo_display()
            if tipo not in marcos_por_tipo:
                marcos_por_tipo[tipo] = []
            marcos_por_tipo[tipo].append(marco)
        
        # Buscar marcos em destaque
        marcos_destaque = HistoriaAssociacao.objects.filter(ativo=True, destaque=True).order_by('ordem_exibicao', 'data_marcante')
        
        # Buscar imagens da galeria para marcos em destaque usando prefetch_related
        marcos_destaque = marcos_destaque.prefetch_related(
            Prefetch(
                'galeria_imagens',
                queryset=HistoriaImagem.objects.filter(ativo=True).order_by('ordem_exibicao', 'created_at')
            )
        )
        
        # Buscar presidente atual da diretoria
        from diretoria.models import MembroDiretoria
        presidente_atual = MembroDiretoria.get_presidente_atual()
        
        context.update({
            'marcos_historicos': marcos_historicos,
            'marcos_por_tipo': marcos_por_tipo,
            'marcos_destaque': marcos_destaque,
            'presidente_atual': presidente_atual,
            'title': 'História da ABMEPI',
            'subtitle': 'Nossa trajetória de conquistas e realizações',
        })
        
        return context


class ExPresidenteListView(LoginRequiredMixin, ListView):
    """
    View para listar ex-presidentes para gerenciamento
    """
    model = ExPresidente
    template_name = 'core/ex_presidente_list.html'
    context_object_name = 'ex_presidentes'
    paginate_by = 20
    
    def get_queryset(self):
        return ExPresidente.objects.all().order_by('-periodo_fim')


class ExPresidenteCreateView(LoginRequiredMixin, CreateView):
    """
    View para criar ex-presidentes
    """
    model = ExPresidente
    form_class = ExPresidenteForm
    template_name = 'core/ex_presidente_form.html'
    success_url = reverse_lazy('core:ex_presidentes')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Ex-presidente criado',
            modulo='Core',
            detalhes=f'Ex-presidente "{form.instance.nome}" criado'
        )
        
        messages.success(self.request, 'Ex-presidente adicionado com sucesso!')
        return response


class ExPresidenteUpdateView(LoginRequiredMixin, UpdateView):
    """
    View para editar ex-presidentes
    """
    model = ExPresidente
    form_class = ExPresidenteForm
    template_name = 'core/ex_presidente_form.html'
    success_url = reverse_lazy('core:ex_presidentes')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Ex-presidente atualizado',
            modulo='Core',
            detalhes=f'Ex-presidente "{form.instance.nome}" atualizado'
        )
        
        messages.success(self.request, 'Ex-presidente atualizado com sucesso!')
        return response


class ExPresidenteDeleteView(LoginRequiredMixin, DeleteView):
    """
    View para excluir ex-presidentes
    """
    model = ExPresidente
    success_url = reverse_lazy('core:ex_presidentes')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        nome = obj.nome
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Ex-presidente excluído',
            modulo='Core',
            detalhes=f'Ex-presidente "{nome}" excluído'
        )
        
        messages.success(request, f'Ex-presidente "{nome}" excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


class HistoriaAssociacaoCreateView(LoginRequiredMixin, CreateView):
    """
    View para criar marcos históricos
    """
    model = HistoriaAssociacao
    form_class = HistoriaAssociacaoForm
    template_name = 'core/historia_form.html'
    success_url = reverse_lazy('core:historia_associacao')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Processar upload múltiplo de imagens
        imagens_galeria = self.request.FILES.getlist('imagens_galeria')
        if imagens_galeria:
            for i, imagem in enumerate(imagens_galeria):
                HistoriaImagem.objects.create(
                    evento=form.instance,
                    imagem=imagem,
                    legenda=f"Imagem {i + 1}",
                    ordem_exibicao=i
                )
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Marco histórico criado',
            modulo='Core',
            detalhes=f'Marco histórico "{form.instance.titulo}" criado'
        )
        
        messages.success(self.request, 'Marco histórico adicionado com sucesso!')
        return response


class HistoriaAssociacaoUpdateView(LoginRequiredMixin, UpdateView):
    """
    View para editar marcos históricos
    """
    model = HistoriaAssociacao
    form_class = HistoriaAssociacaoForm
    template_name = 'core/historia_form.html'
    success_url = reverse_lazy('core:historia_associacao')
    
    def get_context_data(self, **kwargs):
        """Adicionar as imagens da galeria ao contexto"""
        context = super().get_context_data(**kwargs)
        if self.object:
            # Carregar imagens da galeria ativas para o template
            context['galeria_imagens'] = self.object.galeria_imagens.filter(ativo=True).order_by('ordem_exibicao', 'created_at')
            # Debug: verificar se a data está sendo carregada
            context['debug_data_marcante'] = self.object.data_marcante
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Processar upload múltiplo de imagens
        imagens_galeria = self.request.FILES.getlist('imagens_galeria')
        if imagens_galeria:
            # Obter a próxima ordem de exibição
            ultima_ordem = form.instance.galeria_imagens.aggregate(
                max_ordem=Max('ordem_exibicao')
            )['max_ordem'] or -1
            
            for i, imagem in enumerate(imagens_galeria):
                HistoriaImagem.objects.create(
                    evento=form.instance,
                    imagem=imagem,
                    legenda=f"Imagem {ultima_ordem + i + 2}",
                    ordem_exibicao=ultima_ordem + i + 1
                )
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=self.request.user,
            acao='Marco histórico atualizado',
            modulo='Core',
            detalhes=f'Marco histórico "{form.instance.titulo}" atualizado'
        )
        
        messages.success(self.request, 'Marco histórico atualizado com sucesso!')
        return response


class HistoriaAssociacaoDeleteView(LoginRequiredMixin, DeleteView):
    """
    View para excluir marcos históricos
    """
    model = HistoriaAssociacao
    success_url = reverse_lazy('core:historia_associacao')
    
    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        titulo = obj.titulo
        
        # Registrar log de atividade
        LogAtividade.objects.create(
            usuario=request.user,
            acao='Marco histórico excluído',
            modulo='Core',
            detalhes=f'Marco histórico "{titulo}" excluído'
        )
        
        messages.success(request, f'Marco histórico "{titulo}" excluído com sucesso!')
        return super().delete(request, *args, **kwargs)


class HistoriaAssociacaoListView(LoginRequiredMixin, ListView):
    """
    View para listar marcos históricos para edição
    """
    model = HistoriaAssociacao
    template_name = 'core/historia_list.html'
    context_object_name = 'marcos_historicos'
    paginate_by = 10
    
    def get_queryset(self):
        return HistoriaAssociacao.objects.all().order_by('ordem_exibicao', 'data_marcante')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Gerenciar Marcos Históricos'
        context['subtitle'] = 'Edite, adicione imagens e gerencie os eventos da história da ABMEPI'
        
        # Adicionar estatísticas
        marcos = HistoriaAssociacao.objects.all()
        context['total_marcos'] = marcos.count()
        context['marcos_ativos'] = marcos.filter(ativo=True).count()
        context['marcos_destaque'] = marcos.filter(destaque=True).count()
        context['marcos_com_imagens'] = marcos.filter(galeria_imagens__isnull=False).distinct().count()
        
        return context
=======
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
