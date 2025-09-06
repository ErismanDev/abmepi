# Sistema de Modais - ASEJUS

Este documento descreve como usar o sistema de modais implementado no app ASEJUS.

## Visão Geral

O sistema de modais permite criar e editar registros sem sair da página atual, proporcionando uma melhor experiência do usuário. Os modais são implementados usando Bootstrap 5 e JavaScript moderno.

## Arquivos do Sistema

### CSS
- `assejus/static/assejus/css/modais.css` - Estilos específicos para os modais

### JavaScript
- `assejus/static/assejus/js/modais.js` - Funcionalidades JavaScript para os modais

### Templates
- `assejus/templates/assejus/forms/advogado_form_modal.html` - Modal para advogados
- `assejus/templates/assejus/forms/atendimento_form_modal.html` - Modal para atendimentos
- `assejus/templates/assejus/forms/documento_form_modal.html` - Modal para documentos
- `assejus/templates/assejus/forms/andamento_form_modal.html` - Modal para andamentos
- `assejus/templates/assejus/forms/consulta_form_modal.html` - Modal para consultas
- `assejus/templates/assejus/forms/relatorio_form_modal.html` - Modal para relatórios

## Como Usar

### 1. Botões para Abrir Modais

#### Criar Novo Registro
```html
<button type="button" class="btn btn-primary" onclick="openAdvogadoModal()">
    <i class="fas fa-plus me-1"></i>
    Novo Advogado
</button>
```

#### Editar Registro Existente
```html
<button type="button" class="btn btn-warning" onclick="openAdvogadoEditModal({{ advogado.pk }})">
    <i class="fas fa-edit"></i>
</button>
```

### 2. Funções JavaScript Disponíveis

#### Advogados
- `openAdvogadoModal()` - Abre modal para criar novo advogado
- `openAdvogadoEditModal(id)` - Abre modal para editar advogado existente

#### Atendimentos Jurídicos
- `openAtendimentoModal()` - Abre modal para criar novo atendimento
- `openAtendimentoEditModal(id)` - Abre modal para editar atendimento existente

#### Documentos Jurídicos
- `openDocumentoModal()` - Abre modal para criar novo documento
- `openDocumentoEditModal(id)` - Abre modal para editar documento existente

#### Andamentos
- `openAndamentoModal()` - Abre modal para criar novo andamento
- `openAndamentoEditModal(id)` - Abre modal para editar andamento existente

#### Consultas Jurídicas
- `openConsultaModal()` - Abre modal para criar nova consulta
- `openConsultaEditModal(id)` - Abre modal para editar consulta existente

#### Relatórios Jurídicos
- `openRelatorioModal()` - Abre modal para criar novo relatório
- `openRelatorioEditModal(id)` - Abre modal para editar relatório existente

### 3. URLs dos Modais

#### Advogados
- `POST /assejus/advogados/modal/novo/` - Criar advogado
- `GET/POST /assejus/advogados/modal/<id>/editar/` - Editar advogado

#### Atendimentos
- `POST /assejus/atendimentos/modal/novo/` - Criar atendimento
- `GET/POST /assejus/atendimentos/modal/<id>/editar/` - Editar atendimento

#### Documentos
- `POST /assejus/documentos/modal/novo/` - Criar documento
- `GET/POST /assejus/documentos/modal/<id>/editar/` - Editar documento

#### Andamentos
- `POST /assejus/andamentos/modal/novo/` - Criar andamento
- `GET/POST /assejus/andamentos/modal/<id>/editar/` - Editar andamento

#### Consultas
- `POST /assejus/consultas/modal/nova/` - Criar consulta
- `GET/POST /assejus/consultas/modal/<id>/editar/` - Editar consulta

#### Relatórios
- `POST /assejus/relatorios/modal/novo/` - Criar relatório
- `GET/POST /assejus/relatorios/modal/<id>/editar/` - Editar relatório

## Funcionalidades

### Validação de Formulários
- Validação client-side e server-side
- Exibição de erros de validação nos campos
- Feedback visual para campos com erro

### Upload de Arquivos
- Suporte para upload de imagens e documentos
- Validação de tipos de arquivo
- Tratamento de erros de upload

### Responsividade
- Modais responsivos para dispositivos móveis
- Adaptação automática do layout
- Controles touch-friendly

### Acessibilidade
- Suporte para navegação por teclado
- ARIA labels apropriados
- Foco automático nos campos

## Personalização

### Estilos CSS
Os estilos podem ser personalizados editando o arquivo `modais.css`. As principais classes CSS são:

- `.modal-content` - Container principal do modal
- `.modal-header` - Cabeçalho do modal
- `.modal-body` - Corpo do modal
- `.modal-footer` - Rodapé do modal
- `.form-control` - Campos de formulário
- `.btn-primary` - Botões primários

### JavaScript
As funcionalidades JavaScript podem ser estendidas editando o arquivo `modais.js`. As principais funções são:

- `openFormModal()` - Função genérica para abrir modais
- `submitForm()` - Função para submeter formulários
- `showFormErrors()` - Função para exibir erros

## Exemplos de Implementação

### Exemplo 1: Lista com Botões de Modal
```html
<div class="btn-toolbar mb-2 mb-md-0">
    <div class="btn-group me-2">
        <button type="button" class="btn btn-sm btn-primary" onclick="openAdvogadoModal()">
            <i class="fas fa-plus me-1"></i>
            Novo Advogado
        </button>
    </div>
</div>

<table class="table">
    <tbody>
        {% for advogado in advogados %}
        <tr>
            <td>{{ advogado.nome }}</td>
            <td>
                <div class="btn-group">
                    <button type="button" class="btn btn-sm btn-warning" 
                            onclick="openAdvogadoEditModal({{ advogado.pk }})">
                        <i class="fas fa-edit"></i>
                    </button>
                </div>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
```

### Exemplo 2: Modal Personalizado
```html
<button type="button" class="btn btn-primary" onclick="openCustomModal()">
    Abrir Modal Personalizado
</button>

<script>
function openCustomModal() {
    const formHtml = `
        <form id="customForm">
            <div class="mb-3">
                <label class="form-label">Campo Personalizado</label>
                <input type="text" class="form-control" name="campo">
            </div>
        </form>
    `;
    
    openFormModal(
        'Título Personalizado',
        formHtml,
        'customForm',
        '/url/para/submit/'
    );
}
</script>
```

## Troubleshooting

### Problema: Modal não abre
**Solução:** Verifique se os arquivos CSS e JS estão sendo carregados corretamente.

### Problema: Formulário não submete
**Solução:** Verifique se a URL de submit está correta e se o CSRF token está presente.

### Problema: Erros de validação não aparecem
**Solução:** Verifique se a função `showFormErrors()` está sendo chamada corretamente.

### Problema: Modal não fecha após sucesso
**Solução:** Verifique se a resposta JSON tem `reload: true` ou se o modal está sendo fechado manualmente.

## Dependências

- Bootstrap 5.3.0+
- FontAwesome 6.4.0+
- Django 4.0+
- Python 3.8+

## Suporte

Para dúvidas ou problemas com o sistema de modais, consulte:
- Documentação do Bootstrap
- Logs do Django
- Console do navegador para erros JavaScript
