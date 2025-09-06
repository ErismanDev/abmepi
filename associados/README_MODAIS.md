# Sistema de Modais para Associados

Este documento descreve como usar o sistema de modais implementado no módulo de associados.

## Arquivos Incluídos

### CSS
- `associados/static/associados/css/modais.css` - Estilos para os modais

### JavaScript
- `associados/static/associados/js/modais.js` - Funções JavaScript para gerenciar os modais

## Funcionalidades Implementadas

### 1. Modais para Associados

#### `openAssociadoModal()`
Abre um modal para criar um novo associado.

**Uso:**
```html
<button type="button" onclick="openAssociadoModal()">
    Novo Associado
</button>
```

#### `openAssociadoEditModal(associadoId)`
Abre um modal para editar um associado existente.

**Uso:**
```html
<button type="button" onclick="openAssociadoEditModal({{ associado.pk }})">
    Editar
</button>
```

### 2. Modais para Dependentes

#### `openDependenteModal(associadoId)`
Abre um modal para criar um novo dependente, opcionalmente vinculado a um associado.

**Uso:**
```html
<button type="button" onclick="openDependenteModal({{ associado.pk }})">
    Novo Dependente
</button>
```

#### `openDependenteEditModal(dependenteId)`
Abre um modal para editar um dependente existente.

**Uso:**
```html
<button type="button" onclick="openDependenteEditModal({{ dependente.pk }})">
    Editar Dependente
</button>
```

### 3. Modais para Documentos

#### `openDocumentoModal(associadoId, dependenteId)`
Abre um modal para criar um novo documento, opcionalmente vinculado a um associado ou dependente.

**Uso:**
```html
<button type="button" onclick="openDocumentoModal({{ associado.pk }})">
    Novo Documento
</button>
```

#### `openDocumentoEditModal(documentoId)`
Abre um modal para editar um documento existente.

**Uso:**
```html
<button type="button" onclick="openDocumentoEditModal({{ documento.pk }})">
    Editar Documento
</button>
```

### 4. Modal para Pré-Cadastro

#### `openPreCadastroModal()`
Abre um modal para pré-cadastro de associados.

**Uso:**
```html
<button type="button" onclick="openPreCadastroModal()">
    Pré-Cadastro
</button>
```

## Funções Auxiliares

### Validação e Formatação

#### `validarCPF(cpf)`
Valida se um CPF é válido.

#### `formatarCPF(cpf)`
Formata um CPF no padrão XXX.XXX.XXX-XX.

#### `formatarTelefone(telefone)`
Formata um telefone no padrão (XX) XXXX-XXXX ou (XX) XXXXX-XXXX.

#### `formatarCEP(cep)`
Formata um CEP no padrão XXXXX-XXX.

### Máscaras Automáticas

O sistema aplica automaticamente máscaras nos seguintes campos:
- CPF: XXX.XXX.XXX-XX
- Telefone: (XX) XXXX-XXXX ou (XX) XXXXX-XXXX
- CEP: XXXXX-XXX

### Confirmações

#### `confirmarExclusao(url, mensagem)`
Abre um modal de confirmação para exclusão.

**Uso:**
```html
<button type="button" onclick="confirmarExclusao('{% url 'associados:associado_delete' associado.pk %}')">
    Excluir
</button>
```

#### `confirmarAcao(titulo, mensagem, callback)`
Abre um modal de confirmação personalizado.

**Uso:**
```javascript
confirmarAcao(
    'Confirmar Ação',
    'Tem certeza que deseja executar esta ação?',
    function() {
        // Código a ser executado após confirmação
        console.log('Ação confirmada!');
    }
);
```

### Mensagens

#### `mostrarSucesso(mensagem)`
Exibe uma mensagem de sucesso.

#### `mostrarErro(mensagem)`
Exibe uma mensagem de erro.

## Como Implementar em Novos Templates

### 1. Incluir os Arquivos Estáticos

```html
{% load static %}

{% block extra_css %}
<link rel="stylesheet" href="{% static 'associados/css/modais.css' %}">
{% endblock %}

{% block extra_js %}
<script src="{% static 'associados/js/modais.js' %}"></script>
{% endblock %}
```

### 2. Usar as Funções JavaScript

```html
<!-- Botão para criar novo associado -->
<button type="button" class="btn btn-primary" onclick="openAssociadoModal()">
    <i class="fas fa-plus"></i> Novo Associado
</button>

<!-- Botão para editar associado -->
<button type="button" class="btn btn-warning" onclick="openAssociadoEditModal({{ associado.pk }})">
    <i class="fas fa-edit"></i> Editar
</button>

<!-- Botão para excluir com confirmação -->
<button type="button" class="btn btn-danger" onclick="confirmarExclusao('{% url 'associados:associado_delete' associado.pk %}')">
    <i class="fas fa-trash"></i> Excluir
</button>
```

## Dependências

O sistema de modais depende do `ModalManager` global definido no template base (`templates/base.html`). Certifique-se de que este arquivo está sendo usado como template base.

## URLs Necessárias

Para que os modais funcionem corretamente, as seguintes URLs devem estar implementadas:

- `/associados/associados/modal/novo/` - Formulário de novo associado
- `/associados/associados/modal/{id}/editar/` - Formulário de edição de associado
- `/associados/dependentes/modal/novo/` - Formulário de novo dependente
- `/associados/dependentes/modal/{id}/editar/` - Formulário de edição de dependente
- `/associados/documentos/modal/novo/` - Formulário de novo documento
- `/associados/documentos/modal/{id}/editar/` - Formulário de edição de documento
- `/associados/pre-cadastro/modal/` - Formulário de pré-cadastro

## Estilos Personalizados

Os modais incluem estilos específicos para:
- Cabeçalhos com gradiente azul
- Formulários responsivos
- Validação visual
- Animações suaves
- Scrollbars personalizadas
- Estados de loading

## Responsividade

Os modais são totalmente responsivos e se adaptam a diferentes tamanhos de tela:
- Desktop: Largura máxima com padding generoso
- Tablet: Largura média com padding moderado
- Mobile: Largura total com padding reduzido
