from django.urls import path
from . import views

app_name = 'administrativo'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Página de teste
    path('teste-menu/', views.teste_menu, name='teste_menu'),
    
    # Página de debug
    path('debug-menu/', views.debug_menu, name='debug_menu'),
    
    # Eventos
    path('eventos/', views.evento_list, name='evento_list'),
    path('eventos/novo/', views.evento_create, name='evento_create'),
    path('eventos/<int:pk>/', views.evento_detail, name='evento_detail'),
    path('eventos/<int:pk>/editar/', views.evento_update, name='evento_update'),
    path('eventos/<int:pk>/excluir/', views.evento_delete, name='evento_delete'),
    
    # Participantes de Eventos
    path('eventos/<int:evento_pk>/participantes/novo/', views.participante_create, name='participante_create'),
    path('participantes/<int:pk>/editar/', views.participante_update, name='participante_update'),
    path('participantes/<int:pk>/excluir/', views.participante_delete, name='participante_delete'),
    
    # Comunicados
    path('comunicados/', views.comunicado_list, name='comunicado_list'),
    path('comunicados/novo/', views.comunicado_create, name='comunicado_create'),
    path('comunicados/<int:pk>/', views.comunicado_detail, name='comunicado_detail'),
    path('comunicados/<int:pk>/editar/', views.comunicado_update, name='comunicado_update'),
    path('comunicados/<int:pk>/excluir/', views.comunicado_delete, name='comunicado_delete'),
    
    # Listas de Presença
    path('listas-presenca/', views.lista_presenca_list, name='lista_presenca_list'),
    path('listas-presenca/novo/', views.lista_presenca_create, name='lista_presenca_create'),
    path('listas-presenca/<int:pk>/', views.lista_presenca_detail, name='lista_presenca_detail'),
    path('listas-presenca/<int:pk>/editar/', views.lista_presenca_update, name='lista_presenca_update'),
    path('listas-presenca/<int:pk>/excluir/', views.lista_presenca_delete, name='lista_presenca_delete'),
    
    # Presenças
    path('listas-presenca/<int:lista_pk>/presenca/novo/', views.presenca_create, name='presenca_create'),
    path('presenca/<int:pk>/editar/', views.presenca_update, name='presenca_update'),
    path('presenca/<int:pk>/excluir/', views.presenca_delete, name='presenca_delete'),
]
