# Módulo de Psicologia - ABMEPI

Este módulo gerencia o atendimento psicológico oferecido pela ABMEPI aos seus associados.

## Funcionalidades

### 1. Gestão de Psicólogos
- Cadastro de psicólogos com CRP, especialidades e informações de contato
- Controle de status ativo/inativo
- Visualização de estatísticas e sessões por psicólogo

### 2. Gestão de Pacientes
- Cadastro de pacientes (associados) para atendimento psicológico
- Atribuição de psicólogo responsável
- Registro de primeira consulta e observações iniciais

### 3. Agendamento de Sessões
- Agendamento de sessões com data, hora e duração
- Diferentes tipos de sessão (avaliação, terapia, retorno, emergencial)
- Controle de status (agendada, confirmada, realizada, cancelada, remarcada)
- Definição de valores para as sessões

### 4. Prontuário Eletrônico
- Histórico familiar e pessoal
- Queixa principal
- Hipótese diagnóstica
- Plano terapêutico
- Observações gerais

### 5. Evoluções
- Registro de evoluções por sessão
- Observações do terapeuta
- Definição de próximos passos

### 6. Documentos
- Upload e gestão de documentos (laudos, relatórios, atestados)
- Categorização por tipo
- Associação a pacientes e psicólogos

### 7. Agenda
- Controle de horários disponíveis dos psicólogos
- Definição de períodos de trabalho
- Controle de disponibilidade

## Modelos de Dados

### Psicologo
- Usuário do sistema (OneToOne com User)
- Nome completo, CRP, especialidades
- Telefone, email, status ativo
- Data de cadastro

### Paciente
- Associação com associado (OneToOne)
- Psicólogo responsável
- Data da primeira consulta
- Observações iniciais
- Status ativo

### Sessao
- Paciente e psicólogo
- Data/hora, duração
- Tipo de sessão e status
- Observações e valor
- Data de criação

### Prontuario
- Paciente (OneToOne)
- Histórico familiar e pessoal
- Queixa principal
- Hipótese diagnóstica
- Plano terapêutico
- Observações gerais

### Evolucao
- Sessão relacionada
- Conteúdo da evolução
- Observações do terapeuta
- Próximos passos
- Data da evolução

### Documento
- Paciente e psicólogo
- Tipo, título, descrição
- Arquivo anexado
- Data de criação

### Agenda
- Psicólogo
- Data, hora início/fim
- Status disponível
- Observações

## URLs Principais

- `/psicologia/` - Dashboard principal
- `/psicologia/psicologos/` - Lista de psicólogos
- `/psicologia/pacientes/` - Lista de pacientes
- `/psicologia/sessoes/` - Lista de sessões
- `/psicologia/prontuarios/` - Lista de prontuários
- `/psicologia/evolucoes/` - Lista de evoluções
- `/psicologia/documentos/` - Lista de documentos
- `/psicologia/agenda/` - Lista de agenda

## Permissões

- Todas as views requerem autenticação (`@login_required`)
- Uso de `LoginRequiredMixin` para as views baseadas em classe

## Dependências

- Django 4.0+
- django-crispy-forms
- django-filters
- django-tables2
- Pillow (para upload de arquivos)

## Configuração

1. Adicionar `'psicologia.apps.PsicologiaConfig'` ao `INSTALLED_APPS`
2. Incluir URLs do módulo no arquivo principal de URLs
3. Executar migrações: `python manage.py makemigrations psicologia`
4. Aplicar migrações: `python manage.py migrate`

## Uso

### Cadastro de Psicólogo
1. Acessar `/psicologia/psicologos/novo/`
2. Preencher informações básicas
3. Salvar

### Cadastro de Paciente
1. Acessar `/psicologia/pacientes/novo/`
2. Selecionar associado
3. Atribuir psicólogo responsável
4. Definir data da primeira consulta
5. Salvar

### Agendamento de Sessão
1. Acessar `/psicologia/sessoes/nova/`
2. Selecionar paciente e psicólogo
3. Definir data/hora e duração
4. Escolher tipo e status
5. Salvar

### Registro de Evolução
1. Acessar `/psicologia/evolucoes/nova/`
2. Selecionar sessão
3. Preencher conteúdo da evolução
4. Adicionar observações e próximos passos
5. Salvar

## Recursos de Segurança

- Validação de formulários
- Controle de acesso por autenticação
- Validação de dados de entrada
- Sanitização de arquivos uploadados

## Manutenção

- Backup regular dos dados
- Monitoramento de logs
- Atualizações de segurança
- Verificação de integridade dos dados

## Suporte

Para dúvidas ou problemas, entre em contato com a equipe de desenvolvimento da ABMEPI.
