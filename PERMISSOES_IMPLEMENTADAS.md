# Sistema de Permissões Implementado

## Visão Geral
O sistema ABMEPI agora possui controle de acesso baseado no tipo de usuário, garantindo que cada usuário só possa acessar os módulos e funcionalidades apropriadas para seu papel.

## Tipos de Usuário e Acessos

### 1. **Administrador do Sistema** (`administrador_sistema`)
- **Acesso Total**: Pode acessar todos os módulos e funcionalidades
- **Funcionalidades**: Gerenciamento completo do sistema

### 2. **Advogado** (`advogado`)
- **Módulo ASEJUS**: Acesso completo
  - Dashboard
  - Gerenciamento de advogados
  - Atendimentos jurídicos
  - Consultas
  - Documentos
  - Relatórios
  - Andamentos
- **Restrições**: Não pode acessar módulo de psicologia

### 3. **Psicólogo** (`psicologo`)
- **Módulo Psicologia**: Acesso completo
  - Dashboard
  - Gerenciamento de psicólogos
  - Pacientes
  - Sessões
  - Prontuários
  - Evoluções
  - Documentos
  - Agenda
- **Restrições**: Não pode acessar módulo ASEJUS

### 4. **Atendente de Advogado** (`atendente_advogado`)
- **Módulo ASEJUS**: Acesso limitado
  - Dashboard
  - Visualização de atendimentos
  - Consultas
  - Documentos
  - Relatórios
  - Andamentos
- **Restrições**: 
  - Não pode gerenciar advogados
  - Não pode acessar módulo de psicologia

### 5. **Atendente de Psicólogo** (`atendente_psicologo`)
- **Módulo Psicologia**: Acesso limitado
  - Dashboard
  - Pacientes
  - Sessões
  - Agenda
- **Restrições**: 
  - Não pode gerenciar psicólogos
  - Não pode acessar módulo ASEJUS

### 6. **Associado** (`associado`)
- **Acesso**: Apenas às próprias informações
- **Funcionalidades Disponíveis**:
  - Visualização do próprio perfil (sem edição)
  - Minha Ficha (associados)
  - Meus Atendimentos Jurídicos
  - Meus Atendimentos Psicológicos
  - Quartos Disponíveis (reserva de quartos)
  - Minhas Reservas (hotel de trânsito)
- **Restrições**: 
  - Não pode acessar módulos administrativos
  - Não pode acessar menu Hotel de Trânsito completo
  - Não pode editar perfil (apenas visualização)
  - Pode apenas reservar quartos disponíveis, não gerenciar o sistema

### 7. **Atendente Geral** (`atendente_geral`)
- **Acesso**: Funcionalidades básicas do sistema
- **Restrições**: Acesso limitado aos módulos principais

## Implementação Técnica

### Mixins de Permissão
```python
# Para acesso ao módulo ASEJUS
class AssejusAccessMixin(PermissionRequiredMixin):
    user_types_allowed = ['administrador_sistema', 'advogado', 'atendente_advogado']

# Para acesso completo ao ASEJUS
class AssejusFullAccessMixin(PermissionRequiredMixin):
    user_types_allowed = ['administrador_sistema', 'advogado']

# Para acesso ao módulo de psicologia
class PsicologiaAccessMixin(PermissionRequiredMixin):
    user_types_allowed = ['administrador_sistema', 'psicologo', 'atendente_psicologo']

# Para acesso completo à psicologia
class PsicologiaFullAccessMixin(PermissionRequiredMixin):
    user_types_allowed = ['administrador_sistema', 'psicologo']
```

### Decorators de Permissão
```python
# Verificar tipo de usuário
@require_user_type(['administrador_sistema', 'advogado', 'atendente_advogado'])
def view_function(request):
    # Apenas usuários dos tipos especificados podem acessar
    pass

# Verificar permissão específica
@require_permission('assejus_access')
def view_function(request):
    # Apenas usuários com a permissão especificada podem acessar
    pass
```

### Context Processors
As permissões são automaticamente disponibilizadas nos templates através de context processors:
- `can_access_assejus`
- `can_access_psicologia`
- `can_access_assejus_full`
- `can_access_psicologia_full`

## Exemplos de Uso nos Templates

### Controle de Acesso a Módulos
```html
{% if can_access_assejus %}
<li class="nav-item">
    <a class="nav-link" href="#assejusSubmenu">Assejur</a>
    <!-- Submenu do ASEJUS -->
</li>
{% endif %}

{% if can_access_psicologia %}
<li class="nav-item">
    <a class="nav-link" href="#psicologiaSubmenu">Psicologia</a>
    <!-- Submenu da Psicologia -->
</li>
{% endif %}
```

### Controle de Funcionalidades Específicas
```html
{% if can_access_assejus_full %}
<li class="nav-item">
    <a class="nav-link" href="{% url 'assejus:advogado_list' %}">Advogados</a>
</li>
{% endif %}

{% if can_access_psicologia_full %}
<li class="nav-item">
    <a class="nav-link" href="{% url 'psicologia:psicologo_list' %}">Psicólogos</a>
</li>
{% endif %}
```

## Segurança

### Níveis de Proteção
1. **Template Level**: Controle de exibição de menus e links
2. **View Level**: Verificação de permissões antes de executar a view
3. **URL Level**: Redirecionamento automático para login se não autenticado

### Tratamento de Erros
- Usuários sem permissão recebem `PermissionDenied`
- Usuários não autenticados são redirecionados para login
- Mensagens de erro apropriadas são exibidas

## Benefícios

1. **Segurança**: Controle granular de acesso baseado em papel
2. **Usabilidade**: Interface adaptada ao tipo de usuário
3. **Manutenibilidade**: Sistema centralizado de permissões
4. **Escalabilidade**: Fácil adição de novos tipos de usuário e permissões
5. **Auditoria**: Rastreamento de acesso por tipo de usuário

## Configuração

### Adicionar Novo Tipo de Usuário
1. Adicionar no modelo `Usuario.TIPO_USUARIO_CHOICES`
2. Definir permissões no arquivo `core/permissions.py`
3. Atualizar context processors se necessário
4. Atualizar templates para usar as novas permissões

### Adicionar Nova Permissão
1. Definir a permissão no arquivo `core/permissions.py`
2. Aplicar nos mixins apropriados
3. Usar nos decorators das views
4. Atualizar templates para verificar a nova permissão
