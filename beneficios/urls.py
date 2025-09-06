from django.urls import path
from . import views

app_name = 'beneficios'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Página de teste
    path('teste/', views.teste, name='teste'),
    
    # Empresas Parceiras
    path('empresas/', views.empresa_list, name='empresa_list'),
    path('empresas/novo/', views.empresa_create, name='empresa_create'),
    path('empresas/<int:pk>/', views.empresa_detail, name='empresa_detail'),
    path('empresas/<int:pk>/editar/', views.empresa_update, name='empresa_update'),
    path('empresas/<int:pk>/excluir/', views.empresa_delete, name='empresa_delete'),
    
    # Convênios
    path('convenios/', views.convenio_list, name='convenio_list'),
    path('convenios/novo/', views.convenio_create, name='convenio_create'),
    path('convenios/<int:pk>/', views.convenio_detail, name='convenio_detail'),
    path('convenios/<int:pk>/editar/', views.convenio_update, name='convenio_update'),
    path('convenios/<int:pk>/excluir/', views.convenio_delete, name='convenio_delete'),
    
    # Benefícios
    path('beneficios/', views.beneficio_list, name='beneficio_list'),
    path('beneficios/novo/', views.beneficio_create, name='beneficio_create'),
    path('beneficios/<int:pk>/', views.beneficio_detail, name='beneficio_detail'),
    path('beneficios/<int:pk>/editar/', views.beneficio_update, name='beneficio_update'),
    path('beneficios/<int:pk>/excluir/', views.beneficio_delete, name='beneficio_delete'),
    
    # Categorias
    path('categorias/', views.categoria_list, name='categoria_list'),
    path('categorias/novo/', views.categoria_create, name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.categoria_update, name='categoria_update'),
    path('categorias/<int:pk>/excluir/', views.categoria_delete, name='categoria_delete'),
    
    # Solicitação de Benefícios
    path('solicitar/', views.solicitar_beneficio, name='solicitar_beneficio'),
    path('meus-beneficios/', views.meus_beneficios, name='meus_beneficios'),
    
    # Busca de Convênios
    path('buscar-convenios/', views.buscar_convenios, name='buscar_convenios'),
    
    # Aprovação de Benefícios
    path('beneficios/<int:pk>/aprovar/', views.aprovar_beneficio, name='aprovar_beneficio'),
    path('beneficios/<int:pk>/rejeitar/', views.rejeitar_beneficio, name='rejeitar_beneficio'),
    
    # APIs
    path('api/convenios-por-categoria/', views.api_convenios_por_categoria, name='api_convenios_por_categoria'),
    path('api/beneficios-por-status/', views.api_beneficios_por_status, name='api_beneficios_por_status'),
    path('api/categorias-ordem/', views.api_categorias_ordem, name='api_categorias_ordem'),
]
