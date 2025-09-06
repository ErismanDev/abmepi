from django.urls import path
from . import views
from . import pdf_views
from . import api_views
from . import editor_views
from . import editor_personalizado_views
from . import views_ata_simples
from . import modelo_views
from . import modelo_unificado_views

app_name = 'diretoria'

urlpatterns = [
    # Dashboard
    path('', views.DiretoriaDashboardView.as_view(), name='dashboard'),
    
    # Cargos
    path('cargos/', views.CargoDiretoriaListView.as_view(), name='cargo_list'),
    path('cargos/novo/', views.CargoDiretoriaCreateView.as_view(), name='cargo_create'),
    path('cargos/<int:pk>/editar/', views.CargoDiretoriaUpdateView.as_view(), name='cargo_update'),
    path('cargos/<int:pk>/excluir/', views.CargoDiretoriaDeleteView.as_view(), name='cargo_delete'),
    
    # Membros
    path('membros/', views.MembroDiretoriaListView.as_view(), name='membro_list'),
    path('membros/novo/', views.MembroDiretoriaCreateView.as_view(), name='membro_create'),
    path('membros/<int:pk>/editar/', views.MembroDiretoriaUpdateView.as_view(), name='membro_update'),
    path('membros/<int:pk>/excluir/', views.MembroDiretoriaDeleteView.as_view(), name='membro_delete'),
    
    # Atas
    path('atas/', views.AtaReuniaoListView.as_view(), name='ata_list'),
    path('atas/<int:pk>/', views.AtaReuniaoDetailView.as_view(), name='ata_detail'),
    path('atas/nova/', views.AtaReuniaoCreateView.as_view(), name='ata_create'),
    path('atas/<int:pk>/editar/', views.AtaReuniaoUpdateView.as_view(), name='ata_update'),
    path('atas/<int:pk>/excluir/', views.AtaReuniaoDeleteView.as_view(), name='ata_delete'),
    path('atas/<int:pk>/pdf/', pdf_views.gerar_ata_pdf, name='ata_pdf'),
    
    # Editor Avançado de Atas
    path('editor-atas/', editor_views.AtaEditorListView.as_view(), name='ata_editor_list'),
    path('editor-atas/nova/', editor_views.AtaEditorView.as_view(), name='ata_editor_create'),
    path('editor-atas/<int:pk>/editar/', editor_views.AtaEditorEditView.as_view(), name='ata_editor_edit'),
    path('api/editor-atas/salvar/', editor_views.salvar_ata_ajax, name='api_ata_editor_save'),
    path('api/editor-atas/<int:pk>/salvar/', editor_views.salvar_ata_ajax, name='api_ata_editor_update'),
    path('api/editor-atas/template/', editor_views.aplicar_template_ajax, name='api_ata_template'),
    
    # Editor Personalizado de Atas
    path('editor-personalizado/', editor_personalizado_views.AtaEditorPersonalizadoListView.as_view(), name='ata_editor_personalizado_list'),
    path('editor-personalizado/nova/', editor_personalizado_views.AtaEditorPersonalizadoCreateView.as_view(), name='ata_editor_personalizado_create'),
    path('editor-personalizado/<int:pk>/editar/', editor_personalizado_views.AtaEditorPersonalizadoUpdateView.as_view(), name='ata_editor_personalizado_edit'),
    path('editor-personalizado/<int:pk>/visualizar/', editor_personalizado_views.AtaEditorPersonalizadoDetailView.as_view(), name='ata_editor_personalizado_detail'),
    path('api/editor-personalizado/salvar/', editor_personalizado_views.salvar_ata_personalizado_ajax, name='api_ata_editor_personalizado_save'),
    path('api/editor-personalizado/<int:pk>/salvar/', editor_personalizado_views.salvar_ata_personalizado_ajax, name='api_ata_editor_personalizado_update'),
    path('api/editor-personalizado/template/', editor_personalizado_views.aplicar_template_personalizado_ajax, name='api_ata_template_personalizado'),
    
    # APIs
    path('api/templates/', api_views.TemplateListView.as_view(), name='api_templates'),
    path('api/membros/', api_views.MembroDiretoriaListView.as_view(), name='api_membros'),
    path('api/atas/', api_views.salvar_ata_api, name='api_ata_create'),
    path('api/atas/<int:pk>/', api_views.AtaDetailView.as_view(), name='api_ata_detail'),
    path('api/atas/<int:pk>/salvar/', api_views.salvar_ata_api, name='api_ata_update'),
    path('api/atas/<int:pk>/conteudo/', api_views.salvar_conteudo_ata, name='api_ata_conteudo'),
    
    # Resoluções
    path('resolucoes/', views.ResolucaoDiretoriaListView.as_view(), name='resolucao_list'),
    path('resolucoes/<int:pk>/', views.ResolucaoDiretoriaDetailView.as_view(), name='resolucao_detail'),
    path('resolucoes/nova/', views.ResolucaoDiretoriaCreateView.as_view(), name='resolucao_create'),
    path('resolucoes/<int:pk>/editar/', views.ResolucaoDiretoriaUpdateView.as_view(), name='resolucao_update'),
    path('resolucoes/<int:pk>/excluir/', views.ResolucaoDiretoriaDeleteView.as_view(), name='resolucao_delete'),
    
    # AJAX
    path('ajax/buscar-associados/', views.buscar_associados_ajax, name='buscar_associados_ajax'),
    path('ajax/buscar-cargos/', views.buscar_cargos_ajax, name='buscar_cargos_ajax'),
    
    # Modelos de Ata
    path('modelos/', views.listar_modelos_ata, name='modelos_ata_list'),
    path('api/modelos/salvar/', views.salvar_modelo_ata, name='api_salvar_modelo'),
    path('api/modelos/<int:modelo_id>/', views.obter_modelo_ata, name='api_obter_modelo'),
    
    # Modelos de Ata Personalizados
    path('modelos-ata/', modelo_views.ModeloAtaListView.as_view(), name='modelo_ata_list'),
    path('modelos-ata/novo/', modelo_views.ModeloAtaCreateView.as_view(), name='modelo_ata_create'),
    path('modelos-ata/<int:pk>/editar/', modelo_views.ModeloAtaUpdateView.as_view(), name='modelo_ata_update'),
    path('modelos-ata/<int:pk>/excluir/', modelo_views.ModeloAtaDeleteView.as_view(), name='modelo_ata_delete'),
    path('api/modelos-ata/salvar/', modelo_views.salvar_modelo_ajax, name='api_modelo_ata_save'),
    path('api/modelos-ata/aplicar/', modelo_views.aplicar_modelo_ajax, name='api_modelo_ata_apply'),
    path('api/modelos-ata/listar/', modelo_views.listar_modelos_ajax, name='api_modelo_ata_list'),
    
    # Sistema Unificado de Modelos de Ata
    path('modelos-unificados/', modelo_unificado_views.ModeloAtaUnificadoListView.as_view(), name='modelo_unificado_list'),
    path('modelos-unificados/novo/', modelo_unificado_views.ModeloAtaUnificadoCreateView.as_view(), name='modelo_unificado_create'),
    path('modelos-unificados/<int:pk>/editar/', modelo_unificado_views.ModeloAtaUnificadoUpdateView.as_view(), name='modelo_unificado_update'),
    path('modelos-unificados/<int:pk>/excluir/', modelo_unificado_views.ModeloAtaUnificadoDeleteView.as_view(), name='modelo_unificado_delete'),
    path('api/modelos-unificados/usar/<int:pk>/', modelo_unificado_views.usar_modelo_ajax, name='api_modelo_unificado_usar'),
    path('api/modelos-unificados/listar/', modelo_unificado_views.listar_modelos_ajax, name='api_modelo_unificado_list'),
    path('api/modelos-unificados/duplicar/<int:pk>/', modelo_unificado_views.duplicar_modelo, name='api_modelo_unificado_duplicar'),
    
    # Sistema Simplificado de Atas
    path('atas-simples/', views_ata_simples.AtaSimplesListView.as_view(), name='ata_simples_list'),
    path('atas-simples/nova/', views_ata_simples.AtaSimplesCreateView.as_view(), name='ata_simples_create'),
    path('atas-simples/<uuid:pk>/editar/', views_ata_simples.AtaSimplesEditView.as_view(), name='ata_simples_edit'),
    path('atas-simples/<uuid:pk>/visualizar/', views_ata_simples.AtaSimplesDetailView.as_view(), name='ata_simples_view'),
    path('atas-simples/<uuid:pk>/editor/', views_ata_simples.AtaEditorView.as_view(), name='ata_editor'),
    path('atas-simples/<uuid:pk>/editor-avancado/', views_ata_simples.AtaEditorAvancadoView.as_view(), name='ata_editor_avancado'),
    path('atas-simples/<uuid:pk>/html/', views_ata_simples.visualizar_ata_html, name='visualizar_ata_html'),
    path('atas-simples/<uuid:pk>/imprimir/', views_ata_simples.imprimir_ata, name='imprimir_ata'),
    path('atas-simples/<uuid:pk>/baixar/', views_ata_simples.baixar_ata_html, name='baixar_ata_html'),
    path('atas-simples/<uuid:pk>/regenerar/', views_ata_simples.regenerar_html, name='regenerar_html'),
    path('atas-simples/<uuid:pk>/finalizar/', views_ata_simples.finalizar_ata, name='finalizar_ata'),
    path('atas-simples/<uuid:pk>/assinar/', views_ata_simples.assinar_ata, name='assinar_ata'),
]
