from django.urls import path
from . import views

app_name = 'hotel_transito'

urlpatterns = [
    # Dashboard
    path('', views.dashboard_hotel_transito, name='dashboard'),
    
    # Quartos
    path('quartos/', views.QuartoListView.as_view(), name='quarto_list'),
    path('quartos/<int:pk>/', views.QuartoDetailView.as_view(), name='quarto_detail'),
    path('quartos/novo/', views.QuartoCreateView.as_view(), name='quarto_create'),
    path('quartos/<int:pk>/editar/', views.QuartoUpdateView.as_view(), name='quarto_update'),
    path('quartos/<int:pk>/excluir/', views.QuartoDeleteView.as_view(), name='quarto_delete'),
    
    # Hóspedes
    path('hospedes/', views.HospedeListView.as_view(), name='hospede_list'),
    path('hospedes/<int:pk>/', views.HospedeDetailView.as_view(), name='hospede_detail'),
    path('hospedes/novo/', views.HospedeCreateView.as_view(), name='hospede_create'),
    path('hospedes/<int:pk>/editar/', views.HospedeUpdateView.as_view(), name='hospede_update'),
    path('hospedes/<int:pk>/excluir/', views.HospedeDeleteView.as_view(), name='hospede_delete'),
    
    # Reservas
    path('reservas/', views.ReservaListView.as_view(), name='reserva_list'),
    path('reservas/<int:pk>/', views.ReservaDetailView.as_view(), name='reserva_detail'),
    path('reservas/novo/', views.ReservaCreateView.as_view(), name='reserva_create'),
    path('reservas/<int:pk>/editar/', views.ReservaUpdateView.as_view(), name='reserva_update'),
    path('reservas/<int:pk>/excluir/', views.ReservaDeleteView.as_view(), name='reserva_delete'),
    path('reservas/<int:pk>/confirmar/', views.confirmar_reserva, name='confirmar_reserva'),
    path('reservas/<int:pk>/cancelar/', views.cancelar_reserva, name='cancelar_reserva'),
    
    # Hospedagens
    path('hospedagens/', views.HospedagemListView.as_view(), name='hospedagem_list'),
    path('hospedagens/<int:pk>/', views.HospedagemDetailView.as_view(), name='hospedagem_detail'),
    path('hospedagens/novo/', views.HospedagemCreateView.as_view(), name='hospedagem_create'),
    path('hospedagens/<int:pk>/editar/', views.HospedagemUpdateView.as_view(), name='hospedagem_update'),
    path('hospedagens/<int:pk>/excluir/', views.HospedagemDeleteView.as_view(), name='hospedagem_delete'),
    path('hospedagens/<int:pk>/finalizar/', views.finalizar_hospedagem, name='finalizar_hospedagem'),
    
    # Serviços Adicionais
    path('servicos/', views.ServicoAdicionalListView.as_view(), name='servico_adicional_list'),
    path('servicos/novo/', views.ServicoAdicionalCreateView.as_view(), name='servico_adicional_create'),
    path('servicos/<int:pk>/editar/', views.ServicoAdicionalUpdateView.as_view(), name='servico_adicional_update'),
    path('servicos/<int:pk>/excluir/', views.ServicoAdicionalDeleteView.as_view(), name='servico_adicional_delete'),
    
    # Serviços Utilizados
    path('servicos-utilizados/', views.ServicoUtilizadoListView.as_view(), name='servico_utilizado_list'),
    path('servicos-utilizados/novo/', views.ServicoUtilizadoCreateView.as_view(), name='servico_utilizado_create'),
    path('servicos-utilizados/<int:pk>/editar/', views.ServicoUtilizadoUpdateView.as_view(), name='servico_utilizado_update'),
    path('servicos-utilizados/<int:pk>/excluir/', views.ServicoUtilizadoDeleteView.as_view(), name='servico_utilizado_delete'),
    
    # Busca e Relatórios
    path('buscar-quartos/', views.buscar_quartos_disponiveis, name='buscar_quartos_disponiveis'),
    path('relatorios/', views.relatorio_hospedagem, name='relatorio_hospedagem'),
    
    # Views AJAX
    path('ajax/quarto/<int:pk>/info/', views.get_quarto_info, name='get_quarto_info'),
    path('ajax/reserva/<int:pk>/info/', views.get_reserva_info, name='get_reserva_info'),
    path('ajax/hospede/<int:pk>/info/', views.get_hospede_info, name='get_hospede_info'),
    path('ajax/checkin-rapido/', views.checkin_rapido, name='checkin_rapido'),
    path('ajax/checkout-rapido/', views.checkout_rapido, name='checkout_rapido'),
    
    # Modal de detalhes
    path('hospedes/<int:pk>/detalhes-modal/', views.hospede_detail_modal, name='hospede_detail_modal'),
    
    # Views específicas para Associados
    path('associado/quartos-disponiveis/', views.associado_quartos_disponiveis, name='associado_quartos_disponiveis'),
    path('associado/reservar-quarto/<int:quarto_id>/', views.associado_reservar_quarto, name='associado_reservar_quarto'),
    path('associado/minhas-reservas/', views.associado_minhas_reservas, name='associado_minhas_reservas'),
]
