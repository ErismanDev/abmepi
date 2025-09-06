from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_financeiro, name='dashboard'),
    
    # Tipos de Recebimentos
    path('tipos-recebimentos/', views.TipoMensalidadeListView.as_view(), name='tipo_mensalidade_list'),
    path('tipos-recebimentos/novo/', views.TipoMensalidadeCreateView.as_view(), name='tipo_mensalidade_create'),
    path('tipos-recebimentos/<int:pk>/editar/', views.TipoMensalidadeUpdateView.as_view(), name='tipo_mensalidade_update'),
    path('tipos-recebimentos/<int:pk>/excluir/', views.TipoMensalidadeDeleteView.as_view(), name='tipo_mensalidade_delete'),
    
    # Mensalidades
    path('mensalidades/', views.MensalidadeListView.as_view(), name='mensalidade_list'),
    path('mensalidades/nova/', views.MensalidadeCreateView.as_view(), name='mensalidade_create'),
    path('mensalidades/<int:pk>/', views.MensalidadeDetailView.as_view(), name='mensalidade_detail'),
    path('mensalidades/<int:pk>/editar/', views.MensalidadeUpdateView.as_view(), name='mensalidade_update'),
    path('mensalidades/<int:pk>/excluir/', views.MensalidadeDeleteView.as_view(), name='mensalidade_delete'),
    
    # Mensalidades de um associado específico
    path('associado/<int:associado_id>/mensalidades/', views.MensalidadeAssociadoListView.as_view(), name='mensalidade_associado_list'),
    path('associado/<int:associado_id>/carne/', views.gerar_carne_associado, name='gerar_carne_associado'),
    path('associado/<int:associado_id>/parcela-unica/', views.gerar_parcela_unica, name='gerar_parcela_unica'),
    
    # Mensalidades de Associados (Recorrentes)
    path('mensalidades-associados/', views.MensalidadeAssociadosListView.as_view(), name='mensalidade_associados_list'),
    
    # Pagamentos
    path('pagamentos/novo/', views.PagamentoCreateView.as_view(), name='pagamento_create'),
    
    # Despesas
    path('despesas/', views.DespesaListView.as_view(), name='despesa_list'),
    path('despesas/nova/', views.DespesaCreateView.as_view(), name='despesa_create'),
    path('despesas/<int:pk>/', views.DespesaDetailView.as_view(), name='despesa_detail'),
    path('despesas/<int:pk>/editar/', views.DespesaUpdateView.as_view(), name='despesa_update'),
    path('despesas/<int:pk>/excluir/', views.DespesaDeleteView.as_view(), name='despesa_delete'),
    path('despesas/<int:pk>/dar-baixa/', views.dar_baixa_despesa, name='dar_baixa_despesa'),
    
    # Exportação
    path('exportar/mensalidades/', views.export_mensalidades_csv, name='export_mensalidades_csv'),
    path('exportar/despesas/', views.export_despesas_csv, name='export_despesas_csv'),
    
    # Geração automática
    path('gerar-mensalidades/', views.gerar_mensalidades_mensais, name='gerar_mensalidades_mensais'),
    
    # Gerenciamento em lote
    path('gerar-mensalidades-lote/', views.gerar_mensalidades_lote, name='gerar_mensalidades_lote'),
    path('gerar-mensalidades-associado-lote/', views.gerar_mensalidades_associado_lote, name='gerar_mensalidades_associado_lote'),
    path('excluir-mensalidades-associado-lote/', views.excluir_mensalidades_associado_lote, name='excluir_mensalidades_associado_lote'),
    path('excluir-mensalidades-lote/', views.excluir_mensalidades_lote, name='excluir_mensalidades_lote'),
    path('dar-baixa-recebiveis-lote/', views.dar_baixa_recebiveis_lote, name='dar_baixa_recebiveis_lote'),
    path('gerar-carne-lote/', views.gerar_carne_lote, name='gerar_carne_lote'),

    # Configuração de Cobrança
    path('configuracao-cobranca/', views.configuracao_cobranca_edit, name='configuracao_cobranca_edit'),
    path('configuracao-cobranca/dados/', views.configuracao_cobranca_dados, name='configuracao_cobranca_dados'),
]
