from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('logout/', views.logout_view, name='logout'),
    path('primeiro-acesso/', views.primeiro_acesso_view, name='primeiro_acesso'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('dashboard/usuario/', views.usuario_dashboard, name='usuario_dashboard'),
    path('institucional/', views.InstitucionalView.as_view(), name='institucional'),
    path('usuarios/', views.UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/novo/', views.UsuarioCreateView.as_view(), name='usuario_create'),
    path('usuarios/<int:pk>/editar/', views.UsuarioUpdateView.as_view(), name='usuario_update'),
    path('usuarios/<int:pk>/redefinir-senha/', views.redefinir_senha_usuario, name='redefinir_senha_usuario'),
    path('usuarios/<int:pk>/excluir/', views.UsuarioDeleteView.as_view(), name='usuario_delete'),
    path('usuarios/buscar-cpf/', views.usuario_search_cpf, name='usuario_search_cpf'),
    path('perfil/', views.perfil_usuario, name='perfil'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('institucional/editar/', views.InstitucionalConfigEditView.as_view(), name='institucional_edit'),
    path('test-accordions/', views.test_accordions, name='test_accordions'),
    
    # URLs para gerenciamento de posts do feed
    path('feed/posts/', views.feed_posts_list, name='feed_posts_list'),
    path('feed/posts/criar/', views.feed_post_create, name='feed_post_create'),
    path('feed/posts/ajax/', views.feed_posts_list_ajax, name='feed_posts_list_ajax'),
    path('feed/posts/criar/ajax/', views.feed_post_create_ajax, name='feed_post_create_ajax'),
    path('feed/posts/<int:pk>/atualizar/', views.feed_post_update_ajax, name='feed_post_update'),
    path('feed/posts/<int:pk>/excluir/', views.feed_post_delete_ajax, name='feed_post_delete'),
    
    # URLs para interações dos posts (like, comentários, compartilhamento)
    path('posts/<int:post_id>/like/', views.post_like_ajax, name='post_like'),
    path('posts/<int:post_id>/comment/', views.post_comment_ajax, name='post_comment'),
    path('posts/<int:post_id>/comments/', views.post_comments_list_ajax, name='post_comments_list'),
    path('posts/<int:post_id>/share/', views.post_share_ajax, name='post_share'),
    
    # URLs para Assessoria Jurídica (ASSEJUR)
    # Notícias
    path('assejur/noticias/', views.AssejurNewsListView.as_view(), name='assejur_news_list'),
    path('assejur/noticias/nova/', views.AssejurNewsCreateView.as_view(), name='assejur_news_create'),
    path('assejur/noticias/<int:pk>/editar/', views.AssejurNewsUpdateView.as_view(), name='assejur_news_update'),
    path('assejur/noticias/<int:pk>/excluir/', views.AssejurNewsDeleteView.as_view(), name='assejur_news_delete'),
    path('assejur/noticias/<int:pk>/toggle-status/', views.assejur_news_toggle_status_ajax, name='assejur_news_toggle_status'),
    
    # Informativos
    path('assejur/informativos/', views.AssejurInformativoListView.as_view(), name='assejur_informativo_list'),
    path('assejur/informativos/novo/', views.AssejurInformativoCreateView.as_view(), name='assejur_informativo_create'),
    path('assejur/informativos/<int:pk>/editar/', views.AssejurInformativoUpdateView.as_view(), name='assejur_informativo_update'),
    path('assejur/informativos/<int:pk>/excluir/', views.AssejurInformativoDeleteView.as_view(), name='assejur_informativo_delete'),
    path('assejur/informativos/<int:pk>/toggle-status/', views.assejur_informativo_toggle_status_ajax, name='assejur_informativo_toggle_status'),
    path('assejur/noticias/<int:pk>/', views.assejur_news_detail, name='assejur_news_detail'),
    
    # URLs para comentários das notícias ASSEJUR
    path('assejur/noticias/<int:news_id>/comment/', views.assejur_news_comment_ajax, name='assejur_news_comment'),
    path('assejur/noticias/<int:news_id>/comments/', views.assejur_news_comments_list_ajax, name='assejur_news_comments_list'),
    
    # URL para incrementar visualizações de notícias via AJAX
    path('assejur/noticias/<int:news_id>/view/', views.assejur_news_view_increment_ajax, name='assejur_news_view_increment'),
    
    # URLs públicas para visualização das notícias
    path('noticias-juridicas/', views.assejur_news_public_list, name='assejur_news_public_list'),
    path('assejur/noticias/<int:noticia_id>/conteudo/', views.assejur_news_content_ajax, name='assejur_news_content_ajax'),
    
    # URL para página de legislação
    path('legislacao/', views.LegislacaoView.as_view(), name='legislacao'),
    
    # URL para marcar notificações como lidas
    path('notificacoes/marcar-como-lidas/', views.marcar_notificacoes_como_lidas_ajax, name='marcar_notificacoes_como_lidas'),
    path('notificacoes/<int:notificacao_id>/marcar-como-lida/', views.marcar_notificacao_como_lida_ajax, name='marcar_notificacao_como_lida'),
    path('notificacoes/<int:notificacao_id>/invalida/', views.notificacao_invalida, name='notificacao_invalida'),
    
    # URLs para gerenciamento de emails em lote
    path('emails/', views.email_batch_dashboard, name='email_batch_dashboard'),
    path('emails/enviar/', views.email_batch_send, name='email_batch_send'),
    path('emails/preview/', views.email_batch_preview, name='email_batch_preview'),
    path('emails/historico/', views.email_batch_history, name='email_batch_history'),
    
    # URLs para galeria de ex-presidentes e história
    path('ex-presidentes/', views.ExPresidentesView.as_view(), name='ex_presidentes'),
    path('historia/', views.HistoriaAssociacaoView.as_view(), name='historia_associacao'),
    
    # URLs para gerenciar ex-presidentes
    path('ex-presidentes/gerenciar/', views.ExPresidenteListView.as_view(), name='ex_presidente_list'),
    path('ex-presidentes/novo/', views.ExPresidenteCreateView.as_view(), name='ex_presidente_create'),
    path('ex-presidentes/<int:pk>/editar/', views.ExPresidenteUpdateView.as_view(), name='ex_presidente_update'),
    path('ex-presidentes/<int:pk>/excluir/', views.ExPresidenteDeleteView.as_view(), name='ex_presidente_delete'),
    
    # URLs para gerenciar história
    path('historia/gerenciar/', views.HistoriaAssociacaoListView.as_view(), name='historia_list'),
    path('historia/novo/', views.HistoriaAssociacaoCreateView.as_view(), name='historia_create'),
    path('historia/<int:pk>/editar/', views.HistoriaAssociacaoUpdateView.as_view(), name='historia_update'),
    path('historia/<int:pk>/excluir/', views.HistoriaAssociacaoDeleteView.as_view(), name='historia_delete'),
]
