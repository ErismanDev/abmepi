from django.urls import path
from . import views

app_name = 'psicologia'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('meu-dashboard/', views.psicologo_dashboard, name='psicologo_dashboard'),
    
    # Psicólogos
    path('psicologos/', views.PsicologoListView.as_view(), name='psicologo_list'),
    path('psicologos/<int:pk>/', views.PsicologoDetailView.as_view(), name='psicologo_detail'),
    path('psicologos/novo/', views.PsicologoCreateView.as_view(), name='psicologo_create'),
    path('psicologos/<int:pk>/editar/', views.PsicologoUpdateView.as_view(), name='psicologo_update'),
    path('psicologos/<int:pk>/excluir/', views.PsicologoDeleteView.as_view(), name='psicologo_delete'),
    
    # Pacientes
    path('pacientes/', views.PacienteListView.as_view(), name='paciente_list'),
    path('pacientes/<int:pk>/', views.PacienteDetailView.as_view(), name='paciente_detail'),
    path('pacientes/novo/', views.PacienteCreateView.as_view(), name='paciente_create'),
    path('pacientes/novo-modal/', views.PacienteCreateModalView.as_view(), name='paciente_create_modal'),
    path('pacientes/<int:pk>/editar/', views.PacienteUpdateView.as_view(), name='paciente_update'),
    path('pacientes/<int:pk>/editar-modal/', views.PacienteUpdateModalView.as_view(), name='paciente_update_modal'),
    path('pacientes/<int:pk>/transferir-modal/', views.PacienteTransferirModalView.as_view(), name='paciente_transferir_modal'),
    path('pacientes/<int:pk>/excluir/', views.PacienteDeleteView.as_view(), name='paciente_delete'),
    
    # Sessões (visualização geral)
    path('sessoes/', views.SessaoListView.as_view(), name='sessao_list'),
    path('sessoes/<int:pk>/', views.SessaoDetailView.as_view(), name='sessao_detail'),
    path('sessoes/<int:pk>/dados-json/', views.sessao_dados_json, name='sessao_dados_json'),
    path('sessoes/nova/', views.SessaoCreateView.as_view(), name='sessao_create'),
    path('sessoes/<int:pk>/editar/', views.SessaoUpdateView.as_view(), name='sessao_update'),
    path('sessoes/<int:pk>/excluir/', views.SessaoDeleteView.as_view(), name='sessao_delete'),
    
    # Sessões a partir da ficha do paciente
    path('pacientes/<int:paciente_id>/sessoes/nova/', views.SessaoFromPacienteCreateView.as_view(), name='sessao_from_paciente_create'),
    path('pacientes/<int:paciente_id>/sessoes/<int:pk>/editar/', views.SessaoFromPacienteUpdateView.as_view(), name='sessao_from_paciente_update'),
    path('pacientes/<int:paciente_id>/sessoes/<int:pk>/excluir/', views.SessaoFromPacienteDeleteView.as_view(), name='sessao_from_paciente_delete'),
    path('pacientes/<int:paciente_id>/sessoes/<int:pk>/finalizar/', views.finalizar_sessao, name='finalizar_sessao'),
    
    # Prontuários a partir da ficha do paciente
    path('pacientes/<int:paciente_id>/prontuarios/novo/', views.ProntuarioFromPacienteCreateView.as_view(), name='prontuario_from_paciente_create'),
    path('pacientes/<int:paciente_id>/prontuarios/<int:pk>/editar/', views.ProntuarioFromPacienteUpdateView.as_view(), name='prontuario_from_paciente_update'),
    path('pacientes/<int:paciente_id>/prontuarios/<int:pk>/excluir/', views.ProntuarioFromPacienteDeleteView.as_view(), name='prontuario_from_paciente_delete'),
    
    # Prontuários (visualização geral)
    path('prontuarios/', views.ProntuarioListView.as_view(), name='prontuario_list'),
    path('prontuarios/<int:pk>/', views.ProntuarioDetailView.as_view(), name='prontuario_detail'),
    path('prontuarios/novo/', views.ProntuarioCreateView.as_view(), name='prontuario_create'),
    path('prontuarios/<int:pk>/editar/', views.ProntuarioUpdateView.as_view(), name='prontuario_update'),
    path('prontuarios/<int:pk>/excluir/', views.ProntuarioDeleteView.as_view(), name='prontuario_delete'),
    
    # Evoluções (visualização geral)
    path('evolucoes/', views.EvolucaoListView.as_view(), name='evolucao_list'),
    path('evolucoes/<int:pk>/', views.EvolucaoDetailView.as_view(), name='evolucao_detail'),
    path('evolucoes/nova/', views.EvolucaoCreateView.as_view(), name='evolucao_create'),
    path('evolucoes/<int:pk>/editar/', views.EvolucaoUpdateView.as_view(), name='evolucao_update'),
    path('evolucoes/<int:pk>/excluir/', views.EvolucaoDeleteView.as_view(), name='evolucao_delete'),
    
    # Evoluções a partir da ficha do paciente
    path('pacientes/<int:paciente_id>/evolucoes/nova/', views.EvolucaoFromPacienteCreateView.as_view(), name='evolucao_from_paciente_create'),
    path('pacientes/<int:paciente_id>/evolucoes/<int:pk>/editar/', views.EvolucaoFromPacienteUpdateView.as_view(), name='evolucao_from_paciente_update'),
    path('pacientes/<int:paciente_id>/evolucoes/<int:pk>/excluir/', views.EvolucaoFromPacienteDeleteView.as_view(), name='evolucao_from_paciente_delete'),
    
    # Documentos (visualização geral)
    path('documentos/', views.DocumentoListView.as_view(), name='documento_list'),
    path('documentos/<int:pk>/', views.DocumentoDetailView.as_view(), name='documento_detail'),
    path('documentos/<int:pk>/dados-json/', views.documento_dados_json, name='documento_dados_json'),
    path('documentos/novo/', views.DocumentoCreateView.as_view(), name='documento_create'),
    path('documentos/<int:pk>/editar/', views.DocumentoUpdateView.as_view(), name='documento_update'),
    path('documentos/<int:pk>/excluir/', views.DocumentoDeleteView.as_view(), name='documento_delete'),
    
    # Documentos a partir da ficha do paciente
    path('pacientes/<int:paciente_id>/documentos/novo/', views.DocumentoFromPacienteCreateView.as_view(), name='documento_from_paciente_create'),
    path('pacientes/<int:paciente_id>/documentos/<int:pk>/editar/', views.DocumentoFromPacienteUpdateView.as_view(), name='documento_from_paciente_update'),
    path('pacientes/<int:paciente_id>/documentos/<int:pk>/excluir/', views.DocumentoFromPacienteDeleteView.as_view(), name='documento_from_paciente_delete'),
    
    # Agenda
    path('agenda/', views.AgendaListView.as_view(), name='agenda_list'),
    path('agenda/<int:pk>/', views.AgendaDetailView.as_view(), name='agenda_detail'),
    path('agenda/<int:pk>/dados-json/', views.agenda_dados_json, name='agenda_dados_json'),
    path('agenda/novo/', views.AgendaCreateView.as_view(), name='agenda_create'),
    path('agenda/<int:pk>/editar/', views.AgendaUpdateView.as_view(), name='agenda_update'),
    path('agenda/<int:pk>/excluir/', views.AgendaDeleteView.as_view(), name='agenda_delete'),
    
    # Views auxiliares
    path('buscar-associados/', views.buscar_associados, name='buscar_associados'),
    path('verificar-disponibilidade/', views.verificar_disponibilidade, name='verificar_disponibilidade'),
    
    # Transferência de pacientes
    path('pacientes/<int:paciente_id>/transferir/', views.transferir_paciente, name='transferir_paciente'),
    path('pacientes/<int:paciente_id>/remover-psicologo/', views.remover_psicologo_paciente, name='remover_psicologo_paciente'),
    
    # ============================================================================
    # URLs PARA MODAIS
    # ============================================================================
    
    # Psicólogos modais
    path('psicologos/modal/novo/', views.psicologo_modal_create, name='psicologo_modal_create'),
    path('psicologos/modal/<int:pk>/editar/', views.psicologo_modal_update, name='psicologo_modal_update'),
    
    # Pacientes modais
    path('pacientes/modal/novo/', views.paciente_modal_create, name='paciente_modal_create'),
    path('pacientes/modal/<int:pk>/editar/', views.paciente_modal_update, name='paciente_modal_update'),
    
    # Sessões modais
    path('sessoes/modal/nova/', views.sessao_modal_create, name='sessao_modal_create'),
    path('sessoes/modal/<int:pk>/editar/', views.sessao_modal_update, name='sessao_modal_update'),
    
    # Prontuários modais
    path('prontuarios/modal/novo/', views.prontuario_modal_create, name='prontuario_modal_create'),
    path('prontuarios/modal/<int:pk>/editar/', views.prontuario_modal_update, name='prontuario_modal_update'),
    
    # Evoluções modais
    path('evolucoes/modal/nova/', views.evolucao_modal_create, name='evolucao_modal_create'),
    path('evolucoes/modal/<int:pk>/editar/', views.evolucao_modal_update, name='evolucao_modal_update'),
    
    # Documentos modais
    path('documentos/modal/novo/', views.documento_modal_create, name='documento_modal_create'),
    path('documentos/modal/<int:pk>/editar/', views.documento_modal_update, name='documento_modal_update'),
    
    # Agenda modais
    path('agenda/modal/nova/', views.agenda_modal_create, name='agenda_modal_create'),
    path('agenda/modal/<int:pk>/editar/', views.agenda_modal_update, name='agenda_modal_update'),
    
    # Views AJAX
    # path('ajax/agenda-form/', views.get_agenda_form_modal, name='get_agenda_form_modal'),
    
    # Modal de detalhes
    path('psicologos/<int:pk>/detalhes-modal/', views.psicologo_detail_modal, name='psicologo_detail_modal'),
]
