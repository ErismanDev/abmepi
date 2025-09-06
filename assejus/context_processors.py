from .models import (
    Advogado, AtendimentoJuridico, DocumentoJuridico, 
    Andamento, ConsultaJuridica, RelatorioJuridico
)


def assejus_context(request):
    """Processador de contexto para fornecer informações do ASSEJUS globalmente"""
    
    # Só processa se o usuário estiver autenticado
    if not request.user.is_authenticated:
        return {}
    
    try:
        # Estatísticas básicas
        context = {
            'assejus_stats': {
                'total_advogados': Advogado.objects.filter(ativo=True).count(),
                'total_atendimentos': AtendimentoJuridico.objects.count(),
                'atendimentos_em_andamento': AtendimentoJuridico.objects.filter(status='em_andamento').count(),
                'consultas_pendentes': ConsultaJuridica.objects.filter(resolvida=False).count(),
                'total_documentos': DocumentoJuridico.objects.count(),
                'total_andamentos': Andamento.objects.count(),
                'total_relatorios': RelatorioJuridico.objects.count(),
            }
        }
        
        # Adiciona informações específicas se estiver na seção ASSEJUS
        if 'assejus' in request.path:
            context['assejus_stats']['is_assejus_section'] = True
            
            # Atendimentos urgentes
            context['assejus_stats']['atendimentos_urgentes'] = AtendimentoJuridico.objects.filter(
                prioridade='alta'
            ).count()
            
            # Atendimentos recentes
            context['assejus_stats']['atendimentos_recentes'] = AtendimentoJuridico.objects.order_by(
                '-data_abertura'
            )[:3]
        
        return context
        
    except Exception:
        # Em caso de erro, retorna contexto vazio
        return {}
