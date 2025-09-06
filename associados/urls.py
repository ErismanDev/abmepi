from django.urls import path
from . import views
from . import views_pre_cadastro

app_name = 'associados'

urlpatterns = [
    # Listagem principal
    path('', views.AssociadoListView.as_view(), name='associado_list'),
    
    # CRUD de associados
    path('novo/', views.AssociadoCreateView.as_view(), name='associado_create'),
    path('<int:pk>/', views.AssociadoDetailView.as_view(), name='associado_detail'),
    path('<int:pk>/editar/', views.AssociadoUpdateView.as_view(), name='associado_update'),
    path('<int:pk>/excluir/', views.AssociadoDeleteView.as_view(), name='associado_delete'),
    
    # URLs para modais
    path('associados/modal/novo/', views.associado_modal_create, name='associado_modal_create'),
    path('associados/modal/<int:pk>/editar/', views.associado_modal_update, name='associado_modal_update'),
    path('dependentes/modal/novo/', views.dependente_modal_create, name='dependente_modal_create'),
    path('dependentes/modal/<int:pk>/editar/', views.dependente_modal_update, name='dependente_modal_update'),
    path('documentos/modal/novo/', views.documento_modal_create, name='documento_modal_create'),
    path('documentos/modal/<int:pk>/editar/', views.documento_modal_update, name='documento_modal_update'),
    path('pre-cadastro/modal/', views.pre_cadastro_modal, name='pre_cadastro_modal'),
    
    # Ações em lote
    path('acoes-em-lote/', views.associado_bulk_action, name='associado_bulk_action'),
    path('exportar/', views.exportar_associados, name='exportar_associados'),
    path('declaracao-pdf/', views.gerar_declaracao_associados_pdf, name='gerar_declaracao_associados_pdf'),
    path('requerimento-inscricao-pdf/', views.gerar_requerimento_inscricao_pdf, name='gerar_requerimento_inscricao_pdf'),
    path('ficha-cadastro/<int:associado_id>/', views.gerar_ficha_cadastro_associado_pdf, name='gerar_ficha_cadastro_associado_pdf'),
    
    # Documentos
    path('<int:associado_id>/documentos/novo/', views.documento_create, name='documento_create'),
    path('documentos/<int:documento_id>/excluir/', views.documento_delete, name='documento_delete'),
    
    # Dependentes
    path('<int:associado_id>/dependentes/novo/', views.dependente_create, name='dependente_create'),
    path('dependentes/<int:pk>/', views.DependenteDetailView.as_view(), name='dependente_detail'),
    path('dependentes/<int:pk>/editar/', views.dependente_update, name='dependente_update'),
    path('dependentes/<int:pk>/excluir/', views.dependente_delete, name='dependente_delete'),
    
    # API para estatísticas
    path('api/stats/', views.associado_stats_api, name='associado_stats_api'),
    
    # API para dados do associado
    path('api/associado/<int:pk>/', views.associado_api, name='associado_api'),
    
    # Pré-cadastro
    path('pre-cadastro/', views.PreCadastroAssociadoView.as_view(), name='pre_cadastro_form'),
    path('pre-cadastro/sucesso/', views.pre_cadastro_sucesso, name='pre_cadastro_sucesso'),
    path('pre-cadastro/consultar/', views.consultar_pre_cadastro, name='consultar_pre_cadastro'),
    
    # Gerenciamento de pré-cadastros
    path('pre-cadastros/', views_pre_cadastro.PreCadastroListView.as_view(), name='pre_cadastro_list'),
    path('pre-cadastros/<int:pk>/', views_pre_cadastro.pre_cadastro_detail, name='pre_cadastro_detail'),
    path('pre-cadastros/<int:pk>/aprovar/', views_pre_cadastro.aprovar_pre_cadastro, name='aprovar_pre_cadastro'),
    path('pre-cadastros/<int:pk>/rejeitar/', views_pre_cadastro.rejeitar_pre_cadastro, name='rejeitar_pre_cadastro'),
    path('pre-cadastros/historico/', views_pre_cadastro.pre_cadastro_historico, name='pre_cadastro_historico'),
    
    # Views específicas para associados
    path('minha-ficha/', views.minha_ficha, name='minha_ficha'),
    path('meus-atendimentos-juridicos/', views.meus_atendimentos_juridicos_nova, name='meus_atendimentos_juridicos'),
    path('meus-atendimentos-juridicos/<int:atendimento_id>/detalhes/', views.detalhes_atendimento_juridico, name='detalhes_atendimento_juridico'),
    path('meus-atendimentos-psicologicos/', views.meus_atendimentos_psicologicos, name='meus_atendimentos_psicologicos'),
    path('minhas-reservas-hotel/', views.minhas_reservas_hotel_nova, name='minhas_reservas_hotel'),
    path('meu-financeiro/', views.associado_financeiro, name='associado_financeiro'),
]
