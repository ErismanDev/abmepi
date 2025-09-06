from django.urls import path
from . import views

app_name = 'assejus'

urlpatterns = [
    # Página principal
    path('', views.index, name='index'),
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Advogados
    path('advogados/', views.advogado_list, name='advogado_list'),
    path('advogados/novo/', views.advogado_create, name='advogado_create'),
    path('advogados/<int:pk>/', views.advogado_detail, name='advogado_detail'),
    path('advogados/<int:pk>/editar/', views.advogado_update, name='advogado_update'),
    path('advogados/<int:pk>/excluir/', views.advogado_delete, name='advogado_delete'),
    path('advogados/<int:pk>/debug/', views.advogado_debug, name='advogado_debug'),
    
    # Atendimentos Jurídicos
    path('atendimentos/', views.atendimento_list, name='atendimento_list'),
    path('atendimentos/novo/', views.atendimento_create, name='atendimento_create'),
    path('atendimentos/<int:pk>/', views.atendimento_detail, name='atendimento_detail'),
    path('atendimentos/<int:pk>/editar/', views.atendimento_update, name='atendimento_update'),
    path('atendimentos/<int:pk>/excluir/', views.atendimento_delete, name='atendimento_delete'),
    path('atendimentos/<int:pk>/finalizar/', views.atendimento_finalizar, name='atendimento_finalizar'),
    

    
    # Processos Jurídicos
    path('processos/', views.processos_list, name='processos_list'),
    path('processos/novo/', views.processo_create, name='processo_create'),
    path('processos/<int:pk>/', views.processo_detail, name='processo_detail'),
    path('processos/<int:pk>/editar/', views.processo_edit, name='processo_edit'),
    path('processos/<int:pk>/andamentos-pdf/', views.processo_andamentos_pdf, name='processo_andamentos_pdf'),
    
<<<<<<< HEAD
    # AJAX para autocomplete
    path('ajax/buscar-associados/', views.buscar_associados_ajax, name='buscar_associados_ajax'),
    path('ajax/buscar-processos/', views.buscar_processos_ajax, name='buscar_processos_ajax'),
    
=======
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
    # Andamentos (acessíveis apenas através dos processos)
    path('andamentos/novo/', views.andamento_create, name='andamento_create'),
    path('andamentos/<int:pk>/', views.andamento_detail, name='andamento_detail'),
    path('andamentos/<int:pk>/editar/', views.andamento_update, name='andamento_update'),
    path('andamentos/<int:pk>/excluir/', views.andamento_delete, name='andamento_delete'),
    path('andamentos/<int:pk>/delete-ajax/', views.andamento_delete_ajax, name='andamento_delete_ajax'),
    path('andamentos/<int:pk>/pdf/', views.andamento_pdf, name='andamento_pdf'),
    
    # Consultas
    path('consultas/', views.consulta_list, name='consulta_list'),
    path('consultas/novo/', views.consulta_create, name='consulta_create'),
    path('consultas/<int:pk>/', views.consulta_detail, name='consulta_detail'),
    path('consultas/<int:pk>/editar/', views.consulta_update, name='consulta_update'),
    path('consultas/<int:pk>/excluir/', views.consulta_delete, name='consulta_delete'),
    path('consultas/<int:pk>/enviar-advogado/', views.consulta_enviar_advogado, name='consulta_enviar_advogado'),
    
    # Relatórios
    path('relatorios/', views.relatorio_list, name='relatorio_list'),
    path('relatorios/novo/', views.relatorio_create, name='relatorio_create'),
    path('relatorios/<int:pk>/', views.relatorio_detail, name='relatorio_detail'),
    path('relatorios/<int:pk>/editar/', views.relatorio_update, name='relatorio_update'),
    path('relatorios/<int:pk>/excluir/', views.relatorio_delete, name='relatorio_delete'),
    path('relatorios/<int:pk>/pdf/', views.relatorio_pdf, name='relatorio_pdf'),
    
    # Procurações Ad Judicia
    path('procuracaoes/', views.procuracao_list, name='procuracao_list'),
    path('procuracaoes/novo/', views.procuracao_create, name='procuracao_create'),
    path('procuracaoes/<int:pk>/', views.procuracao_detail, name='procuracao_detail'),
    path('procuracaoes/<int:pk>/editar/', views.procuracao_edit, name='procuracao_edit'),
    path('procuracaoes/<int:pk>/excluir/', views.procuracao_delete, name='procuracao_delete'),
    path('procuracaoes/<int:pk>/imprimir/', views.procuracao_print, name='procuracao_print'),
    path('procuracaoes/<int:pk>/pdf/', views.procuracao_pdf, name='procuracao_pdf'),
    path('ajax/associado/<int:associado_id>/dados/', views.get_associado_data, name='get_associado_data'),
    path('ajax/advogado/<int:advogado_id>/dados/', views.get_advogado_data, name='get_advogado_data'),
    
    # API para estatísticas
    path('stats/', views.stats, name='stats'),
    
    # ============================================================================
    # URLs PARA MODAIS
    # ============================================================================
    
    # Advogados modais
    path('advogados/modal/novo/', views.advogado_modal_create, name='advogado_modal_create'),
    path('advogados/modal/<int:pk>/editar/', views.advogado_modal_update, name='advogado_modal_update'),
    
    # URLs de teste removidas - não são mais necessárias
    # path('advogados/modal/novo/teste/', views.advogado_modal_create_test, name='advogado_modal_create_test'),
    # path('advogados/modal/novo/teste-simples/', views.advogado_modal_create_test_simple, name='advogado_modal_create_test_simple'),
    # path('advogados/modal/novo/teste-direto/', views.advogado_modal_create_test_direct, name='advogado_modal_create_test_direct'),
    # path('advogados/modal/novo/teste-ultra-simples/', views.advogado_modal_create_test_ultra_simple, name='advogado_modal_create_test_ultra_simple'),
    # path('advogados/modal/novo/teste-json/', views.advogado_modal_create_test_json, name='advogado_modal_create_test_json'),
    # path('advogados/modal/novo/teste-no-auth/', views.advogado_modal_create_test_no_auth, name='advogado_modal_create_test_no_auth'),
    
    # Atendimentos modais
    path('atendimentos/modal/novo/', views.atendimento_modal_create, name='atendimento_modal_create'),
    path('atendimentos/modal/<int:pk>/editar/', views.atendimento_modal_update, name='atendimento_modal_update'),
    
    # Atendimentos AJAX
    path('atendimentos/<int:pk>/delete/', views.atendimento_delete_ajax, name='atendimento_delete_ajax'),
    
    # Documentos
    path('documentos/', views.documento_list, name='documento_list'),
    path('documentos/novo/', views.documento_create, name='documento_create'),
    path('documentos/<int:pk>/', views.documento_detail, name='documento_detail'),
    path('documentos/<int:pk>/visualizar/', views.documento_view, name='documento_view'),
    path('documentos/<int:pk>/editar/', views.documento_update, name='documento_update'),
    path('documentos/<int:pk>/excluir/', views.documento_delete, name='documento_delete'),
    path('documentos/<int:pk>/download/', views.documento_download, name='documento_download'),
    path('documentos/upload-ajax/', views.documento_upload_ajax, name='documento_upload_ajax'),
    path('documentos/list-ajax/', views.documento_list_ajax, name='documento_list_ajax'),
    path('documentos/<int:pk>/delete-ajax/', views.documento_delete_ajax, name='documento_delete_ajax'),
    

    

    

    
    # Andamentos modais
    path('andamentos/modal/novo/', views.andamento_modal_create, name='andamento_modal_create'),
    path('andamentos/modal/<int:pk>/editar/', views.andamento_modal_update, name='andamento_modal_update'),
    
    # Consultas modais
    path('consultas/modal/nova/', views.consulta_modal_create, name='consulta_modal_create'),
    path('consultas/modal/<int:pk>/editar/', views.consulta_modal_update, name='consulta_modal_update'),
    
    # Relatórios modais
    path('relatorios/modal/novo/', views.relatorio_modal_create, name='relatorio_modal_create'),
    path('relatorios/modal/<int:pk>/editar/', views.relatorio_modal_update, name='relatorio_modal_update'),
    
    # Views AJAX
    # path('ajax/advogado-form/', views.get_advogado_form_modal, name='get_advogado_form_modal'),
    
    # Modal de detalhes
    # path('advogados/<int:pk>/detalhes-modal/', views.advogado_detail_modal, name='advogado_detail_modal'),
    # path('advogados/<int:pk>/detalhes-modal/teste/', views.advogado_detail_modal_test, name='advogado_detail_modal_test'),

    # URLs para modais
    path('modal-base/', views.modal_base, name='modal_base'),
<<<<<<< HEAD
    
    # URLs para modelos de poderes
    path('modelos-poderes/<str:tipo>/', views.listar_modelos_poderes, name='modelos_poderes_list'),
    path('api/salvar-modelo-poderes/', views.salvar_modelo_poderes, name='api_salvar_modelo_poderes'),
    path('api/obter-modelo-poderes/<int:modelo_id>/', views.obter_modelo_poderes, name='api_obter_modelo_poderes'),
    path('api/excluir-modelo-poderes/<int:modelo_id>/', views.excluir_modelo_poderes, name='excluir_modelo_poderes'),
=======
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
]
