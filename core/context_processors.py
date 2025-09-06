from .models import Notificacao


def notificacoes_context(request):
    """
    Context processor para adicionar notificações e tipo de usuário em todas as páginas
    """
    if request.user.is_authenticated:
        # Buscar notificações pendentes do usuário
        notificacoes_pendentes = Notificacao.objects.filter(
            usuario_destino=request.user,
            status='pendente'
        ).order_by('-prioridade', '-data_criacao')[:5]
        
        # Contar total de notificações pendentes
        total_notificacoes_pendentes = Notificacao.objects.filter(
            usuario_destino=request.user,
            status='pendente'
        ).count()
        
        # Contar pré-cadastros pendentes (apenas para administradores e atendentes gerais)
        pre_cadastros_pendentes = 0
        if request.user.tipo_usuario in ['administrador_sistema', 'atendente_geral']:
            from associados.models import PreCadastroAssociado
            pre_cadastros_pendentes = PreCadastroAssociado.objects.filter(status='pendente').count()
        
        # Contar reservas pendentes (apenas para administradores e atendentes gerais)
        reservas_pendentes = 0
        if request.user.tipo_usuario in ['administrador_sistema', 'atendente_geral']:
            from hotel_transito.models import Reserva
            reservas_pendentes = Reserva.objects.filter(status='pendente').count()
        
        return {
            'notificacoes_pendentes': notificacoes_pendentes,
            'total_notificacoes_pendentes': total_notificacoes_pendentes,
            'pre_cadastros_pendentes': pre_cadastros_pendentes,
            'reservas_pendentes': reservas_pendentes,
            'user_tipo': request.user.tipo_usuario,
        }
    
    return {
        'notificacoes_pendentes': [],
        'total_notificacoes_pendentes': 0,
        'pre_cadastros_pendentes': 0,
        'reservas_pendentes': 0,
        'user_tipo': None,
    }