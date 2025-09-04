from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Psicologo, Paciente, Sessao, Prontuario, Evolucao, Documento, Agenda, PsicologoResponsavel, PacientePsicologo


@admin.register(Psicologo)
class PsicologoAdmin(admin.ModelAdmin):
    list_display = ['nome_completo', 'crp', 'uf_crp', 'telefone', 'email', 'cidade', 'ativo', 'data_cadastro']
    list_filter = ['ativo', 'data_cadastro', 'cidade', 'estado', 'aceita_planos_saude', 'uf_crp']
    search_fields = ['nome_completo', 'crp', 'uf_crp', 'email', 'telefone', 'cpf', 'cidade']
    readonly_fields = ['data_cadastro', 'data_atualizacao']
    list_editable = ['ativo']
    date_hierarchy = 'data_cadastro'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('user', 'nome_completo', 'crp', 'uf_crp', 'ativo', 'foto')
        }),
        ('Dados Pessoais', {
            'fields': ('data_nascimento', 'cpf', 'rg', 'orgao_emissor')
        }),
        ('Contato', {
            'fields': ('telefone', 'telefone_secundario', 'email', 'email_secundario')
        }),
        ('Endereço', {
            'fields': ('cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado')
        }),
        ('Dados Profissionais', {
            'fields': ('especialidades', 'formacao_academica', 'cursos_complementares', 'experiencia_profissional', 'areas_atuacao')
        }),
        ('Dados de Trabalho', {
            'fields': ('horario_atendimento', 'valor_consulta', 'aceita_planos_saude', 'planos_aceitos')
        }),
        ('Documentos', {
            'fields': ('curriculo', 'documentos_complementares')
        }),
        ('Controle', {
            'fields': ('data_cadastro', 'data_atualizacao', 'observacoes')
        }),
    )


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ['associado', 'psicologo_responsavel', 'data_primeira_consulta', 'ativo', 'data_cadastro']
    list_filter = ['ativo', 'psicologo_responsavel', 'data_primeira_consulta', 'data_cadastro']
    search_fields = ['associado__nome', 'associado__cpf']
    readonly_fields = ['data_cadastro']
    list_editable = ['ativo']
    
    fieldsets = (
        ('Associado', {
            'fields': ('associado', 'psicologo_responsavel')
        }),
        ('Informações Clínicas', {
            'fields': ('data_primeira_consulta', 'observacoes_iniciais')
        }),
        ('Status', {
            'fields': ('ativo', 'data_cadastro')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Validação personalizada antes de salvar"""
        try:
            # Verificar se já existe um paciente para este associado
            if not change:  # Se for criação
                if Paciente.objects.filter(associado=obj.associado).exists():
                    self.message_user(
                        request, 
                        f'ERRO: O associado {obj.associado.nome} já é paciente no sistema. '
                        'Não é possível cadastrar o mesmo associado duas vezes.',
                        level='ERROR'
                    )
                    return  # Não salvar
            
            super().save_model(request, obj, form, change)
            if not change:
                self.message_user(request, f'Paciente {obj.associado.nome} cadastrado com sucesso!')
            else:
                self.message_user(request, f'Paciente {obj.associado.nome} atualizado com sucesso!')
                
        except Exception as e:
            self.message_user(
                request, 
                f'Erro ao salvar paciente: {str(e)}',
                level='ERROR'
            )


@admin.register(Sessao)
class SessaoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'psicologo', 'data_hora', 'tipo_sessao', 'status', 'duracao', 'valor']
    list_filter = ['status', 'tipo_sessao', 'psicologo', 'data_hora']
    search_fields = ['paciente__associado__nome', 'psicologo__nome_completo']
    readonly_fields = ['data_criacao']
    list_editable = ['status', 'valor']
    date_hierarchy = 'data_hora'
    
    fieldsets = (
        ('Agendamento', {
            'fields': ('paciente', 'psicologo', 'data_hora', 'duracao')
        }),
        ('Tipo e Status', {
            'fields': ('tipo_sessao', 'status')
        }),
        ('Informações', {
            'fields': ('observacoes', 'valor')
        }),
        ('Sistema', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Prontuario)
class ProntuarioAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'data_criacao', 'data_atualizacao']
    list_filter = ['data_criacao', 'data_atualizacao']
    search_fields = ['paciente__associado__nome']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    
    fieldsets = (
        ('Paciente', {
            'fields': ('paciente',)
        }),
        ('Histórico', {
            'fields': ('historico_familiar', 'historico_pessoal')
        }),
        ('Avaliação', {
            'fields': ('queixa_principal', 'hipotese_diagnostica')
        }),
        ('Plano', {
            'fields': ('plano_terapeutico', 'observacoes_gerais')
        }),
        ('Sistema', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Evolucao)
class EvolucaoAdmin(admin.ModelAdmin):
    list_display = ['sessao', 'data_evolucao', 'paciente', 'psicologo']
    list_filter = ['data_evolucao', 'sessao__psicologo']
    search_fields = ['sessao__paciente__associado__nome', 'sessao__psicologo__nome_completo']
    readonly_fields = ['data_evolucao']
    
    def paciente(self, obj):
        return obj.sessao.paciente.associado.nome
    paciente.short_description = 'Paciente'
    
    def psicologo(self, obj):
        return obj.sessao.psicologo.nome_completo
    psicologo.short_description = 'Psicólogo'
    
    fieldsets = (
        ('Sessão', {
            'fields': ('sessao',)
        }),
        ('Evolução', {
            'fields': ('conteudo', 'observacoes_terapeuta', 'proximos_passos')
        }),
        ('Sistema', {
            'fields': ('data_evolucao',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Documento)
class DocumentoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'paciente', 'psicologo', 'tipo', 'data_criacao']
    list_filter = ['tipo', 'psicologo', 'data_criacao']
    search_fields = ['titulo', 'paciente__associado__nome', 'psicologo__nome_completo']
    readonly_fields = ['data_criacao']
    
    fieldsets = (
        ('Documento', {
            'fields': ('titulo', 'tipo', 'descricao', 'arquivo')
        }),
        ('Responsáveis', {
            'fields': ('paciente', 'psicologo')
        }),
        ('Sistema', {
            'fields': ('data_criacao',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ['psicologo', 'data', 'hora_inicio', 'hora_fim', 'disponivel']
    list_filter = ['psicologo', 'data', 'disponivel']
    search_fields = ['psicologo__nome_completo']
    list_editable = ['disponivel']
    date_hierarchy = 'data'
    
    fieldsets = (
        ('Agenda', {
            'fields': ('psicologo', 'data', 'hora_inicio', 'hora_fim')
        }),
        ('Status', {
            'fields': ('disponivel', 'observacoes')
        }),
    )


@admin.register(PacientePsicologo)
class PacientePsicologoAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'psicologo', 'data_inicio', 'data_fim', 'ativo', 'principal', 'especialidade_foco']
    list_filter = ['ativo', 'principal', 'psicologo', 'data_inicio', 'data_criacao']
    search_fields = ['paciente__associado__nome', 'psicologo__nome_completo', 'especialidade_foco', 'motivo_inicio']
    readonly_fields = ['data_criacao', 'data_atualizacao']
    list_editable = ['ativo', 'principal']
    
    fieldsets = (
        ('Relacionamento Principal', {
            'fields': ('paciente', 'psicologo', 'data_inicio', 'data_fim', 'ativo', 'principal')
        }),
        ('Detalhes do Atendimento', {
            'fields': ('especialidade_foco', 'motivo_inicio', 'motivo_encerramento')
        }),
        ('Observações', {
            'fields': ('observacoes',)
        }),
        ('Controle', {
            'fields': ('data_criacao', 'data_atualizacao'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente', 'psicologo')


@admin.register(PsicologoResponsavel)
class PsicologoResponsavelAdmin(admin.ModelAdmin):
    list_display = ['paciente', 'psicologo', 'data_inicio', 'data_fim', 'ativo', 'data_criacao']
    list_filter = ['ativo', 'psicologo', 'data_inicio', 'data_criacao']
    search_fields = ['paciente__associado__nome', 'psicologo__nome_completo', 'motivo_transferencia']
    readonly_fields = ['data_criacao']
    
    fieldsets = (
        ('⚠️ DEPRECATED - Use PacientePsicologo', {
            'description': 'Este modelo está obsoleto. Use o modelo PacientePsicologo para novos relacionamentos.',
            'fields': ()
        }),
        ('Relacionamento', {
            'fields': ('paciente', 'psicologo', 'data_inicio', 'data_fim', 'ativo')
        }),
        ('Detalhes da Transferência', {
            'fields': ('motivo_transferencia', 'observacoes')
        }),
        ('Controle', {
            'fields': ('data_criacao',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('paciente', 'psicologo')
