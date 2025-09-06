from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class AdvogadoAtivoFilter(admin.SimpleListFilter):
    """Filtro para advogados ativos/inativos"""
    title = _('Status do Advogado')
    parameter_name = 'status_advogado'

    def lookups(self, request, model_admin):
        return (
            ('ativo', _('Ativo')),
            ('inativo', _('Inativo')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'ativo':
            return queryset.filter(ativo=True)
        if self.value() == 'inativo':
            return queryset.filter(ativo=False)


class AtendimentoPrioridadeFilter(admin.SimpleListFilter):
    """Filtro para prioridade de atendimentos"""
    title = _('Prioridade')
    parameter_name = 'prioridade_atendimento'

    def lookups(self, request, model_admin):
        return (
            ('alta', _('Alta')),
            ('media', _('Média')),
            ('baixa', _('Baixa')),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(prioridade=self.value())


class AtendimentoStatusFilter(admin.SimpleListFilter):
    """Filtro para status de atendimentos"""
    title = _('Status do Atendimento')
    parameter_name = 'status_atendimento'

    def lookups(self, request, model_admin):
        return (
            ('em_andamento', _('Em Andamento')),
            ('concluido', _('Concluído')),
            ('pendente', _('Pendente')),
            ('cancelado', _('Cancelado')),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())


class ConsultaResolvidaFilter(admin.SimpleListFilter):
    """Filtro para consultas resolvidas/pendentes"""
    title = _('Status da Consulta')
    parameter_name = 'status_consulta'

    def lookups(self, request, model_admin):
        return (
            ('resolvida', _('Resolvida')),
            ('pendente', _('Pendente')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'resolvida':
            return queryset.filter(resolvida=True)
        if self.value() == 'pendente':
            return queryset.filter(resolvida=False)


class DocumentoAtivoFilter(admin.SimpleListFilter):
    """Filtro para documentos ativos/inativos"""
    title = _('Status do Documento')
    parameter_name = 'status_documento'

    def lookups(self, request, model_admin):
        return (
            ('ativo', _('Ativo')),
            ('inativo', _('Inativo')),
        )

    def queryset(self, request, queryset):
        if self.value() == 'ativo':
            return queryset.filter(ativo=True)
        if self.value() == 'inativo':
            return queryset.filter(ativo=False)


class DataRangeFilter(admin.SimpleListFilter):
    """Filtro base para filtros de data"""
    title = _('Período')
    parameter_name = 'periodo'

    def lookups(self, request, model_admin):
        return (
            ('hoje', _('Hoje')),
            ('semana', _('Esta Semana')),
            ('mes', _('Este Mês')),
            ('trimestre', _('Este Trimestre')),
            ('ano', _('Este Ano')),
        )

    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if self.value() == 'hoje':
            return queryset.filter(data_abertura__date=now.date())
        elif self.value() == 'semana':
            start_of_week = now - timedelta(days=now.weekday())
            return queryset.filter(data_abertura__gte=start_of_week)
        elif self.value() == 'mes':
            return queryset.filter(
                data_abertura__year=now.year,
                data_abertura__month=now.month
            )
        elif self.value() == 'trimestre':
            quarter = (now.month - 1) // 3
            start_month = quarter * 3 + 1
            end_month = start_month + 2
            return queryset.filter(
                data_abertura__year=now.year,
                data_abertura__month__gte=start_month,
                data_abertura__month__lte=end_month
            )
        elif self.value() == 'ano':
            return queryset.filter(data_abertura__year=now.year)


class AtendimentoDataFilter(DataRangeFilter):
    """Filtro específico para datas de atendimento"""
    title = _('Data de Abertura')
    parameter_name = 'data_atendimento'
    
    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if self.value() == 'hoje':
            return queryset.filter(data_abertura__date=now.date())
        elif self.value() == 'semana':
            start_of_week = now - timedelta(days=now.weekday())
            return queryset.filter(data_abertura__gte=start_of_week)
        elif self.value() == 'mes':
            return queryset.filter(
                data_abertura__year=now.year,
                data_abertura__month=now.month
            )
        elif self.value() == 'trimestre':
            quarter = (now.month - 1) // 3
            start_month = quarter * 3 + 1
            end_month = start_month + 2
            return queryset.filter(
                data_abertura__year=now.year,
                data_abertura__month__gte=start_month,
                data_abertura__month__lte=end_month
            )
        elif self.value() == 'ano':
            return queryset.filter(data_abertura__year=now.year)


class ConsultaDataFilter(DataRangeFilter):
    """Filtro específico para datas de consulta"""
    title = _('Data da Consulta')
    parameter_name = 'data_consulta'
    
    def queryset(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        now = timezone.now()
        
        if self.value() == 'hoje':
            return queryset.filter(data_consulta__date=now.date())
        elif self.value() == 'semana':
            start_of_week = now - timedelta(days=now.weekday())
            return queryset.filter(data_consulta__gte=start_of_week)
        elif self.value() == 'mes':
            return queryset.filter(
                data_consulta__year=now.year,
                data_consulta__month=now.month
            )
        elif self.value() == 'trimestre':
            quarter = (now.month - 1) // 3
            start_month = quarter * 3 + 1
            end_month = start_month + 2
            return queryset.filter(
                data_consulta__year=now.year,
                data_consulta__month__gte=start_month,
                data_consulta__month__lte=end_month
            )
        elif self.value() == 'ano':
            return queryset.filter(data_consulta__year=now.year)


# Dicionário de filtros por modelo
ASSEJUS_FILTERS = {
    'Advogado': [AdvogadoAtivoFilter],
    'AtendimentoJuridico': [
        AtendimentoPrioridadeFilter, 
        AtendimentoStatusFilter, 
        AtendimentoDataFilter
    ],
    'ConsultaJuridica': [
        ConsultaResolvidaFilter, 
        ConsultaDataFilter
    ],
    'DocumentoJuridico': [DocumentoAtivoFilter],
    'Andamento': [DataRangeFilter],
    'RelatorioJuridico': [DataRangeFilter],
    'ProcessoJuridico': [DataRangeFilter],
}
