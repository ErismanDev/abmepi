# Sistema de Modais para Psicologia

## Visão Geral
Este documento descreve o sistema de modais implementado para o módulo de psicologia, que converte todos os formulários de criação e edição de páginas completas para modais suspensos.

## Status da Implementação

### ✅ Templates Convertidos para Modais

#### 1. **psicologo_list.html**
- ✅ Botão "Novo Psicólogo" → `openPsicologoModal()`
- ✅ Botão "Editar" na tabela → `openPsicologoEditModal({{ psicologo.pk }})`
- ✅ Botão "Cadastrar Psicólogo" (estado vazio) → `openPsicologoModal()`

#### 2. **psicologo_detail.html**
- ✅ Botão "Editar" no cabeçalho → `openPsicologoEditModal({{ psicologo.pk }})`
- ✅ Botão "Nova Sessão" → `openSessaoModal()`
- ✅ Botão "Nova Agenda" → `openAgendaModal()`
- ✅ Botão "Editar Psicólogo" (ações rápidas) → `openPsicologoEditModal({{ psicologo.pk }})`

#### 3. **dashboard.html**
- ✅ Botão "Novo Paciente" → `openPacienteModal()`
- ✅ Botão "Novo Psicólogo" → `openPsicologoModal()`
- ✅ Botão "Nova Agenda" → `openAgendaModal()`
- ✅ Botão "Editar" na tabela de pacientes → `openPacienteEditModal({{ paciente.pk }})`

#### 4. **sessao_list.html**
- ✅ Botão "Nova Sessão" → `openSessaoModal()`
- ✅ Botão "Editar" na tabela → `openSessaoEditModal({{ sessao.pk }})`
- ✅ Botão "Agendar Sessão" (estado vazio) → `openSessaoModal()`

#### 5. **prontuario_list.html**
- ✅ Botão "Novo Prontuário" → `openProntuarioModal()`
- ✅ Botão "Editar" na tabela → `openProntuarioEditModal({{ prontuario.pk }})`
- ✅ Botão "Novo Prontuário" (estado vazio) → `openProntuarioModal()`

#### 6. **evolucao_list.html**
- ✅ Botão "Nova Evolução" → `openEvolucaoModal()`
- ✅ Botão "Editar" na tabela → `openEvolucaoEditModal({{ evolucao.pk }})`
- ✅ Botão "Nova Evolução" (estado vazio) → `openEvolucaoModal()`

#### 7. **documento_list.html**
- ✅ Botão "Novo Documento" → `openDocumentoModal()`
- ✅ Botão "Editar" na tabela → `openDocumentoEditModal({{ documento.pk }})`
- ✅ Botão "Novo Documento" (estado vazio) → `openDocumentoModal()`

### 🔄 Templates com Sistema Próprio de Modais

#### 8. **agenda_list.html**
- ⚠️ Já possui sistema próprio de modais implementado
- ⚠️ Botão "Criar Primeiro Horário" ainda usa `href="{% url 'psicologia:agenda_create' %}"`
- ⚠️ Sistema pode ser migrado para o sistema unificado se necessário

### ❌ Templates Ainda Não Convertidos

#### 9. **agenda_detail.html**
- ❌ Botão "Editar" no cabeçalho → `href="{% url 'psicologia:agenda_update' agenda.pk %}"`
- ❌ Botão "Editar" (ações rápidas) → `href="{% url 'psicologia:agenda_update' agenda.pk %}"`

#### 10. **evolucao_detail.html**
- ❌ Botão "Editar" no cabeçalho → `href="{% url 'psicologia:evolucao_update' evolucao.pk %}"`
- ❌ Botão "Editar" (ações rápidas) → `href="{% url 'psicologia:evolucao_update' evolucao.pk %}"`

#### 11. **documento_detail.html**
- ❌ Botão "Editar" no cabeçalho → `href="{% url 'psicologia:documento_update' documento.pk %}"`
- ❌ Botão "Novo Documento" → `href="{% url 'psicologia:documento_create' %}"`
- ❌ Botão "Editar" (ações rápidas) → `href="{% url 'psicologia:documento_update' documento.pk %}"`

#### 12. **prontuario_detail.html**
- ❌ Botão "Editar" no cabeçalho → `href="{% url 'psicologia:prontuario_update' prontuario.pk %}"`
- ❌ Botão "Nova Sessão" → `href="{% url 'psicologia:sessao_from_paciente_create' prontuario.paciente.pk %}"`
- ❌ Botão "Nova Evolução" → `href="{% url 'psicologia:evolucao_from_paciente_create' prontuario.paciente.pk %}"`
- ❌ Botão "Novo Documento" → `href="{% url 'psicologia:documento_from_paciente_create' prontuario.paciente.pk %}"`
- ❌ Botão "Editar" (ações rápidas) → `href="{% url 'psicologia:prontuario_update' prontuario.pk %}"`

#### 13. **psicologo_dashboard.html**
- ❌ Botão "Nova Sessão" → `href="{% url 'psicologia:sessao_create' %}"`
- ❌ Botão "Nova Sessão" (por paciente) → `href="{% url 'psicologia:sessao_from_paciente_create' paciente.pk %}"`
- ❌ Botão "Novo Paciente" → `href="{% url 'psicologia:paciente_create' %}"`
- ❌ Botão "Editar" na tabela de sessões → `href="{% url 'psicologia:sessao_update' sessao.pk %}"`

#### 14. **sessao_detail.html**
- ❌ Botão "Editar" no cabeçalho → `href="{% url 'psicologia:sessao_update' sessao.pk %}"`
- ❌ Botão "Nova Evolução" → `href="{% url 'psicologia:evolucao_create' %}"`
- ❌ Botão "Editar" (ações rápidas) → `href="{% url 'psicologia:sessao_update' sessao.pk %}"`

#### 15. **paciente_list.html**
- ⚠️ Já possui sistema próprio de modais implementado
- ⚠️ Botão "Novo Paciente" ainda usa `href="{% url 'psicologia:paciente_create' %}"`
- ⚠️ Sistema pode ser migrado para o sistema unificado se necessário

## Próximos Passos Recomendados

### Prioridade Alta (Templates de Detalhes)
1. **agenda_detail.html** - Converter botões de edição
2. **evolucao_detail.html** - Converter botões de edição
3. **documento_detail.html** - Converter botões de edição e criação
4. **prontuario_detail.html** - Converter botões de edição e criação

### Prioridade Média (Dashboards)
1. **psicologo_dashboard.html** - Converter botões de criação e edição
2. **sessao_detail.html** - Converter botões de edição e criação

### Prioridade Baixa (Sistemas Próprios)
1. **agenda_list.html** - Migrar para sistema unificado (opcional)
2. **paciente_list.html** - Migrar para sistema unificado (opcional)

## Funcionalidades Implementadas

### Sistema de Modais Base
- ✅ `ModalManager` class no `base.html`
- ✅ Funções globais `openFormModal()` e `openConfirmModal()`
- ✅ Gerenciamento automático de CSRF tokens
- ✅ Tratamento de erros de validação
- ✅ Mensagens de sucesso/erro
- ✅ Recarregamento automático da página após sucesso

### Views de Modais
- ✅ `psicologo_modal_create` e `psicologo_modal_update`
- ✅ `paciente_modal_create` e `paciente_modal_update`
- ✅ `sessao_modal_create` e `sessao_modal_update`
- ✅ `prontuario_modal_create` e `prontuario_modal_update`
- ✅ `evolucao_modal_create` e `evolucao_modal_update`
- ✅ `documento_modal_create` e `documento_modal_update`
- ✅ `agenda_modal_create` e `agenda_modal_update`

### Templates de Formulários
- ✅ `psicologo_form_modal.html`
- ✅ `paciente_form_modal.html`
- ✅ `sessao_form_modal.html`
- ✅ `prontuario_form_modal.html`
- ✅ `evolucao_form_modal.html`
- ✅ `documento_form_modal.html`
- ✅ `agenda_form_modal.html`

### JavaScript e CSS
- ✅ `modais.js` com todas as funções necessárias
- ✅ `modais.css` com estilos personalizados
- ✅ Integração com Bootstrap 5
- ✅ Responsividade para dispositivos móveis

## URLs de Modais
Todas as URLs de modais seguem o padrão:
- Criação: `/psicologia/{modelo}/modal/novo/`
- Edição: `/psicologia/{modelo}/modal/{pk}/editar/`

## Como Usar

### Para Abrir Modal de Criação
```javascript
openPsicologoModal();        // Psicólogo
openPacienteModal();          // Paciente
openSessaoModal();            // Sessão
openProntuarioModal();        // Prontuário
openEvolucaoModal();          // Evolução
openDocumentoModal();         // Documento
openAgendaModal();            // Agenda
```

### Para Abrir Modal de Edição
```javascript
openPsicologoEditModal(id);        // Psicólogo
openPacienteEditModal(id);          // Paciente
openSessaoEditModal(id);            // Sessão
openProntuarioEditModal(id);        // Prontuário
openEvolucaoEditModal(id);          // Evolução
openDocumentoEditModal(id);         // Documento
openAgendaEditModal(id);            // Agenda
```

## Notas Importantes

1. **Sistema Unificado**: Todos os modais agora usam o mesmo sistema base, garantindo consistência na experiência do usuário.

2. **Validação**: Os formulários mantêm toda a validação do Django, com feedback visual em tempo real.

3. **Upload de Arquivos**: Suporte completo para upload de arquivos nos modais (ex: foto do psicólogo, documentos).

4. **Permissões**: Todas as views de modais respeitam as permissões de usuário existentes.

5. **Responsividade**: Os modais são responsivos e funcionam bem em dispositivos móveis.

## Troubleshooting

### Problemas Comuns

1. **Modal não abre**: Verificar se o arquivo `modais.js` está sendo carregado
2. **Erro de CSRF**: Verificar se o token CSRF está sendo enviado corretamente
3. **Formulário não envia**: Verificar se a URL do modal está correta
4. **Erros de validação não aparecem**: Verificar se o JavaScript está funcionando

### Debug
- Abrir o console do navegador para ver mensagens de erro
- Verificar se as URLs de modais estão funcionando
- Confirmar se os templates de formulários estão sendo renderizados corretamente
