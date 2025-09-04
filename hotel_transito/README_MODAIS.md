# Sistema de Modais - Módulo Hotel de Trânsito

## Visão Geral

O sistema de modais do módulo Hotel de Trânsito oferece uma interface moderna e responsiva para operações rápidas, criação e edição de registros, proporcionando uma experiência de usuário fluida e eficiente.

## Características dos Modais

### Design e Estilo
- **Tema Visual**: Gradientes modernos com cores institucionais
- **Responsividade**: Adaptação automática para diferentes tamanhos de tela
- **Animações**: Transições suaves de entrada e saída
- **Ícones**: Uso de ícones Bootstrap para melhor usabilidade

### Funcionalidades
- **Validação em Tempo Real**: Verificação instantânea de campos
- **Máscaras de Campos**: Formatação automática para telefone, CEP, CPF
- **Campos Dependentes**: Exibição/ocultação baseada em seleções
- **Busca AJAX**: Pesquisa de hóspedes em tempo real
- **Cálculos Automáticos**: Valores totais e diárias

## Estrutura dos Modais

### 1. Modal de Criação Rápida
```html
<div class="modal fade modal-hotel-transito" id="modalCriacaoRapida">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Novo [Tipo]</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <!-- Formulário específico carregado via AJAX -->
            </div>
        </div>
    </div>
</div>
```

### 2. Modal de Edição
```html
<div class="modal fade modal-hotel-transito" id="modalEdicao">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Editar [Tipo]</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <!-- Formulário de edição -->
            </div>
        </div>
    </div>
</div>
```

### 3. Modal de Confirmação
```html
<div class="modal fade modal-hotel-transito" id="modalConfirmacao">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Confirmar Ação</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <p>Deseja realmente executar esta ação?</p>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="button" class="btn btn-primary">Confirmar</button>
            </div>
        </div>
    </div>
</div>
```

## Formulários nos Modais

### Estrutura de Formulário
```html
<form class="form-hotel-transito" method="post">
    {% csrf_token %}
    
    <div class="row">
        <div class="col-md-6">
            <div class="form-group">
                <label class="form-label required-field">Campo Obrigatório</label>
                <input type="text" class="form-control" name="campo" required>
            </div>
        </div>
        <div class="col-md-6">
            <div class="form-group">
                <label class="form-label">Campo Opcional</label>
                <input type="text" class="form-control" name="campo_opcional">
            </div>
        </div>
    </div>
    
    <div class="form-group">
        <label class="form-label">Observações</label>
        <textarea class="form-control" name="observacoes" rows="3"></textarea>
    </div>
    
    <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
        <button type="submit" class="btn btn-primary">Salvar</button>
    </div>
</form>
```

### Tipos de Campos

#### Campos de Texto
```html
<input type="text" class="form-control" name="nome" maxlength="200">
```

#### Campos de Seleção
```html
<select class="form-control" name="tipo">
    <option value="">Selecione...</option>
    <option value="individual">Individual</option>
    <option value="duplo">Duplo</option>
</select>
```

#### Campos de Data
```html
<input type="date" class="form-control" name="data_entrada">
```

#### Campos de Hora
```html
<input type="time" class="form-control" name="hora_entrada">
```

#### Campos de Data/Hora
```html
<input type="datetime-local" class="form-control" name="data_hora">
```

#### Campos Numéricos
```html
<input type="number" class="form-control" name="valor" step="0.01" min="0">
```

#### Campos de Texto Longo
```html
<textarea class="form-control" name="observacoes" rows="3"></textarea>
```

#### Checkboxes
```html
<div class="form-check">
    <input class="form-check-input" type="checkbox" name="ativo" id="ativo">
    <label class="form-check-label" for="ativo">
        Ativo
    </label>
</div>
```

## Validações e Máscaras

### Validação de Datas
```javascript
function validarDatas(input) {
    const dataEntrada = document.querySelector('input[name="data_entrada"]');
    const dataSaida = document.querySelector('input[name="data_saida"]');
    
    if (dataEntrada && dataSaida && dataEntrada.value && dataSaida.value) {
        const entrada = new Date(dataEntrada.value);
        const saida = new Date(dataSaida.value);
        
        if (entrada >= saida) {
            dataSaida.setCustomValidity('A data de saída deve ser posterior à data de entrada');
            dataSaida.classList.add('is-invalid');
        } else {
            dataSaida.setCustomValidity('');
            dataSaida.classList.remove('is-invalid');
        }
    }
}
```

### Máscara de Telefone
```javascript
function configurarMascarasCampos() {
    const telefones = document.querySelectorAll('input[name*="telefone"]');
    telefones.forEach(function(telefone) {
        telefone.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 11) {
                if (value.length <= 2) {
                    value = `(${value}`;
                } else if (value.length <= 6) {
                    value = `(${value.slice(0, 2)}) ${value.slice(2)}`;
                } else if (value.length <= 10) {
                    value = `(${value.slice(0, 2)}) ${value.slice(2, 6)}-${value.slice(6)}`;
                } else {
                    value = `(${value.slice(0, 2)}) ${value.slice(2, 7)}-${value.slice(7)}`;
                }
            }
            e.target.value = value;
        });
    });
}
```

### Máscara de CEP
```javascript
const ceps = document.querySelectorAll('input[name="cep"]');
ceps.forEach(function(cep) {
    cep.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length <= 8) {
            value = value.replace(/^(\d{5})(\d)/, '$1-$2');
        }
        e.target.value = value;
    });
});
```

### Máscara de CPF
```javascript
const cpfs = document.querySelectorAll('input[name="numero_documento"]');
cpfs.forEach(function(cpf) {
    cpf.addEventListener('input', function(e) {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length <= 11) {
            value = value.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4');
        }
        e.target.value = value;
    });
});
```

## Campos Dependentes

### Exemplo: Tipo de Hóspede → Associado
```javascript
function configurarCamposDependentes() {
    const tipoHospede = document.querySelector('select[name="tipo_hospede"]');
    const campoAssociado = document.querySelector('select[name="associado"]');
    
    if (tipoHospede && campoAssociado) {
        tipoHospede.addEventListener('change', function() {
            if (this.value === 'associado') {
                campoAssociado.closest('.form-group').style.display = 'block';
                campoAssociado.required = true;
            } else {
                campoAssociado.closest('.form-group').style.display = 'none';
                campoAssociado.required = false;
                campoAssociado.value = '';
            }
        });
        
        // Executar na inicialização
        if (tipoHospede.value === 'associado') {
            campoAssociado.closest('.form-group').style.display = 'block';
            campoAssociado.required = true;
        }
    }
}
```

## Operações AJAX

### Busca de Hóspedes
```javascript
function buscarHospedes(termo) {
    if (termo.length < 3) return;
    
    fetch(`/hotel_transito/ajax/buscar-hospedes/?q=${encodeURIComponent(termo)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                exibirResultadosBusca(data.hospedes);
            }
        })
        .catch(error => {
            console.error('Erro na busca:', error);
        });
}
```

### Check-in Rápido
```javascript
function checkinRapido(hospedeId, quartoId) {
    fetch('/hotel_transito/ajax/checkin-rapido/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            hospede_id: hospedeId,
            quarto_id: quartoId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostrarMensagem('Check-in realizado com sucesso!', 'success');
            // Atualizar interface
        } else {
            mostrarMensagem(data.error, 'danger');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        mostrarMensagem('Erro ao realizar check-in', 'danger');
    });
}
```

## Estilos CSS

### Classes Principais
```css
.modal-hotel-transito {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.modal-hotel-transito .modal-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-bottom: none;
}

.form-hotel-transito .form-control {
    border-radius: 0.375rem;
    border: 1px solid #ced4da;
    padding: 0.5rem 0.75rem;
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.form-hotel-transito .form-control:focus {
    border-color: #667eea;
    box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
}
```

### Responsividade
```css
@media (max-width: 768px) {
    .modal-hotel-transito .modal-body {
        padding: 1rem;
    }
    
    .form-hotel-transito .col-md-6,
    .form-hotel-transito .col-md-4 {
        margin-bottom: 1rem;
    }
}
```

### Animações
```css
.modal-hotel-transito .modal.fade .modal-dialog {
    transition: transform 0.3s ease-out;
    transform: translate(0, -50px);
}

.modal-hotel-transito .modal.show .modal-dialog {
    transform: none;
}
```

## Uso dos Modais

### 1. Abrir Modal de Criação
```javascript
// Via JavaScript
const modal = new bootstrap.Modal(document.getElementById('modalCriacaoRapida'));
modal.show();

// Via atributo data
<button data-bs-toggle="modal" data-bs-target="#modalCriacaoRapida">
    Novo Hóspede
</button>
```

### 2. Fechar Modal
```javascript
// Via JavaScript
const modal = bootstrap.Modal.getInstance(document.getElementById('modalCriacaoRapida'));
modal.hide();

// Via botão com data-bs-dismiss
<button type="button" class="btn-close" data-bs-dismiss="modal"></button>
```

### 3. Eventos do Modal
```javascript
const modal = document.getElementById('modalCriacaoRapida');
modal.addEventListener('show.bs.modal', function() {
    // Modal está sendo exibido
    console.log('Modal abrindo...');
});

modal.addEventListener('shown.bs.modal', function() {
    // Modal foi exibido completamente
    console.log('Modal aberto');
});

modal.addEventListener('hide.bs.modal', function() {
    // Modal está sendo fechado
    console.log('Modal fechando...');
});

modal.addEventListener('hidden.bs.modal', function() {
    // Modal foi fechado completamente
    console.log('Modal fechado');
});
```

## Boas Práticas

### 1. Estrutura HTML
- Sempre incluir `{% csrf_token %}` em formulários
- Usar classes CSS consistentes
- Estruturar campos em grid responsivo

### 2. JavaScript
- Inicializar modais quando o DOM estiver carregado
- Tratar erros adequadamente
- Usar debounce para campos de busca

### 3. CSS
- Manter consistência visual
- Usar variáveis CSS para cores
- Testar em diferentes dispositivos

### 4. Validação
- Validar tanto no frontend quanto no backend
- Fornecer feedback visual claro
- Prevenir envio de dados inválidos

## Troubleshooting

### Problemas Comuns

#### Modal não abre
- Verificar se o Bootstrap está carregado
- Confirmar se o ID do modal está correto
- Verificar se não há conflitos de JavaScript

#### Formulário não envia
- Verificar se o CSRF token está presente
- Confirmar se o método POST está configurado
- Verificar se não há erros de validação

#### Campos não funcionam
- Verificar se os nomes dos campos estão corretos
- Confirmar se os eventos estão sendo registrados
- Verificar se não há conflitos de CSS

#### Responsividade
- Testar em diferentes tamanhos de tela
- Verificar se as classes Bootstrap estão corretas
- Confirmar se o CSS personalizado não está interferindo

## Exemplos de Implementação

### Modal Completo de Hóspede
```html
<!-- Modal de Hóspede -->
<div class="modal fade modal-hotel-transito" id="modalHospede" tabindex="-1">
    <div class="modal-dialog modal-xl">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Novo Hóspede</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form class="form-hotel-transito" method="post" id="formHospede">
                    {% csrf_token %}
                    
                    <!-- Tipo de Hóspede -->
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-group">
                                <label class="form-label required-field">Tipo de Hóspede</label>
                                <select class="form-control" name="tipo_hospede" required>
                                    <option value="">Selecione...</option>
                                    <option value="associado">Associado</option>
                                    <option value="nao_associado">Não Associado</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-6" id="campoAssociado" style="display: none;">
                            <div class="form-group">
                                <label class="form-label">Associado</label>
                                <select class="form-control" name="associado">
                                    <option value="">Selecione um associado...</option>
                                    <!-- Opções carregadas via AJAX -->
                                </select>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Dados Pessoais -->
                    <div class="row">
                        <div class="col-md-8">
                            <div class="form-group">
                                <label class="form-label required-field">Nome Completo</label>
                                <input type="text" class="form-control" name="nome_completo" required>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-group">
                                <label class="form-label">Data de Nascimento</label>
                                <input type="date" class="form-control" name="data_nascimento">
                            </div>
                        </div>
                    </div>
                    
                    <!-- Documentos -->
                    <div class="row">
                        <div class="col-md-4">
                            <div class="form-group">
                                <label class="form-label required-field">Tipo de Documento</label>
                                <select class="form-control" name="tipo_documento" required>
                                    <option value="">Selecione...</option>
                                    <option value="cpf">CPF</option>
                                    <option value="rg">RG</option>
                                    <option value="passaporte">Passaporte</option>
                                    <option value="cnh">CNH</option>
                                </select>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                                <label class="form-label required-field">Número do Documento</label>
                                <input type="text" class="form-control" name="numero_documento" required>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="form-group">
                                <label class="form-label">UF</label>
                                <input type="text" class="form-control uf-field" name="uf_emissor" maxlength="2">
                            </div>
                        </div>
                    </div>
                    
                    <!-- Contato -->
                    <div class="row">
                        <div class="col-md-6">
                            <div class="form-group">
                                <label class="form-label">Telefone</label>
                                <input type="text" class="form-control telefone-field" name="telefone">
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group">
                                <label class="form-label">E-mail</label>
                                <input type="email" class="form-control" name="email">
                            </div>
                        </div>
                    </div>
                    
                    <!-- Endereço -->
                    <div class="row">
                        <div class="col-md-2">
                            <div class="form-group">
                                <label class="form-label">CEP</label>
                                <input type="text" class="form-control cep-field" name="cep">
                            </div>
                        </div>
                        <div class="col-md-8">
                            <div class="form-group">
                                <label class="form-label">Endereço</label>
                                <input type="text" class="form-control" name="endereco">
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="form-group">
                                <label class="form-label">Número</label>
                                <input type="text" class="form-control" name="numero">
                            </div>
                        </div>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-4">
                            <div class="form-group">
                                <label class="form-label">Complemento</label>
                                <input type="text" class="form-control" name="complemento">
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="form-group">
                                <label class="form-label">Bairro</label>
                                <input type="text" class="form-control" name="bairro">
                            </div>
                        </div>
                        <div class="col-md-3">
                            <div class="form-group">
                                <label class="form-label">Cidade</label>
                                <input type="text" class="form-control" name="cidade">
                            </div>
                        </div>
                        <div class="col-md-1">
                            <div class="form-group">
                                <label class="form-label">UF</label>
                                <input type="text" class="form-control uf-field" name="estado" maxlength="2">
                            </div>
                        </div>
                    </div>
                    
                    <!-- Observações -->
                    <div class="form-group">
                        <label class="form-label">Observações</label>
                        <textarea class="form-control" name="observacoes" rows="3"></textarea>
                    </div>
                    
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                        <button type="submit" class="btn btn-primary">Salvar Hóspede</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
```

---

**Documentação do Sistema de Modais**  
**Módulo**: Hotel de Trânsito  
**Versão**: 1.0.0  
**Data**: 2024
