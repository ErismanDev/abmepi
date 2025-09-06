/**
 * Sistema de Modais para Associados
 * Sistema limpo e moderno com mensagens flutuantes
 * 
 * FUNCIONALIDADES IMPLEMENTADAS:
 * ✅ Mensagens flutuantes (sucesso, erro, aviso, informação)
 * ✅ Mensagens de progresso com barra de progresso
 * ✅ Mensagens de confirmação interativas
 * ✅ Sistema de modais robusto com fallbacks
 * ✅ Máscaras para campos (CPF, telefone, CEP)
 * ✅ Integração com Modal Loader
 * ✅ Funções para associados, dependentes e documentos
 */

// ============================================================================
// SISTEMA DE MENSAGENS FLUTUANTES
// ============================================================================

/**
 * Exibir mensagem de sucesso
 */
window.showSuccessMessage = function(message) {
    console.log('✅ Sucesso:', message);
    
    // Remover mensagens anteriores
    removeMessages();
    
    // Criar mensagem de sucesso
    const successDiv = document.createElement('div');
    successDiv.className = 'alert alert-success alert-dismissible fade show position-fixed';
    successDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    successDiv.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(successDiv);
    
    // Auto-remover após 5 segundos
    setTimeout(() => {
        if (successDiv.parentNode) {
            successDiv.remove();
        }
    }, 5000);
};

/**
 * Exibir mensagem de erro
 */
window.showErrorMessage = function(message) {
    console.log('❌ Erro:', message);
    
    // Remover mensagens anteriores
    removeMessages();
    
    // Criar mensagem de erro
    const errorDiv = document.createElement('div');
    errorDiv.className = 'alert alert-danger alert-dismissible fade show position-fixed';
    errorDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(errorDiv);
    
    // Auto-remover após 8 segundos
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 8000);
};

/**
 * Remover mensagens existentes
 */
window.removeMessages = function() {
    document.querySelectorAll('.alert.position-fixed').forEach(alert => {
        alert.remove();
    });
};

/**
 * Exibir mensagem de aviso
 */
window.showWarningMessage = function(message) {
    console.log('⚠️ Aviso:', message);
    
    // Remover mensagens anteriores
    removeMessages();
    
    // Criar mensagem de aviso
    const warningDiv = document.createElement('div');
    warningDiv.className = 'alert alert-warning alert-dismissible fade show position-fixed';
    warningDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    warningDiv.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(warningDiv);
    
    // Auto-remover após 6 segundos
    setTimeout(() => {
        if (warningDiv.parentNode) {
            warningDiv.remove();
        }
    }, 6000);
};

/**
 * Exibir mensagem de informação
 */
function showInfoMessage(message) {
    console.log('ℹ️ Informação:', message);
    
    // Remover mensagens anteriores
    removeMessages();
    
    // Criar mensagem de informação
    const infoDiv = document.createElement('div');
    infoDiv.className = 'alert alert-info alert-dismissible fade show position-fixed';
    infoDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    infoDiv.innerHTML = `
        <i class="fas fa-info-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(infoDiv);
    
    // Auto-remover após 7 segundos
    setTimeout(() => {
        if (infoDiv.parentNode) {
            infoDiv.remove();
        }
    }, 7000);
}

/**
 * Exibir mensagem de progresso/loading
 */
function showProgressMessage(message, progress = null) {
    console.log('🔄 Progresso:', message, progress ? `(${progress}%)` : '');
    
    // Remover mensagens de progresso anteriores
    document.querySelectorAll('.alert.alert-progress').forEach(alert => alert.remove());
    
    // Criar mensagem de progresso
    const progressDiv = document.createElement('div');
    progressDiv.className = 'alert alert-progress alert-dismissible fade show position-fixed';
    progressDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 350px;';
    
    let progressBar = '';
    if (progress !== null) {
        progressBar = `
            <div class="progress mt-2" style="height: 6px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" 
                     style="width: ${progress}%" 
                     aria-valuenow="${progress}" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                </div>
            </div>
        `;
    }
    
    progressDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-spinner fa-spin me-2"></i>
            <span>${message}</span>
        </div>
        ${progressBar}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Adicionar estilos personalizados para a mensagem de progresso
    progressDiv.style.backgroundColor = '#e3f2fd';
    progressDiv.style.borderColor = '#2196f3';
    progressDiv.style.color = '#0d47a1';
    
    document.body.appendChild(progressDiv);
    
    return progressDiv;
}

/**
 * Atualizar mensagem de progresso
 */
function updateProgressMessage(message, progress) {
    const progressDiv = document.querySelector('.alert.alert-progress');
    if (progressDiv) {
        const messageSpan = progressDiv.querySelector('span');
        const progressBar = progressDiv.querySelector('.progress-bar');
        
        if (messageSpan) messageSpan.textContent = message;
        if (progressBar) progressBar.style.width = `${progress}%`;
        
        return progressDiv;
    }
    return null;
}

/**
 * Remover mensagem de progresso
 */
function removeProgressMessage() {
    document.querySelectorAll('.alert.alert-progress').forEach(alert => alert.remove());
}

/**
 * Exibir mensagem de confirmação
 */
function showConfirmMessage(message, onConfirm, onCancel = null) {
    console.log('❓ Confirmação solicitada:', message);
    
    // Remover mensagens anteriores
    removeMessages();
    
    // Criar mensagem de confirmação
    const confirmDiv = document.createElement('div');
    confirmDiv.className = 'alert alert-confirm alert-dismissible fade show position-fixed';
    confirmDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 400px;';
    
    confirmDiv.innerHTML = `
        <div class="d-flex align-items-start">
            <i class="fas fa-question-circle me-2 mt-1"></i>
            <div class="flex-grow-1">
                <div class="mb-2">${message}</div>
                <div class="btn-group btn-group-sm">
                    <button type="button" class="btn btn-success btn-confirm">
                        <i class="fas fa-check me-1"></i>Confirmar
                    </button>
                    <button type="button" class="btn btn-secondary btn-cancel">
                        <i class="fas fa-times me-1"></i>Cancelar
                    </button>
                </div>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Adicionar estilos personalizados para a mensagem de confirmação
    confirmDiv.style.backgroundColor = '#fff3cd';
    confirmDiv.style.borderColor = '#ffc107';
    confirmDiv.style.color = '#856404';
    
    document.body.appendChild(confirmDiv);
    
    // Configurar eventos dos botões
    const confirmBtn = confirmDiv.querySelector('.btn-confirm');
    const cancelBtn = confirmDiv.querySelector('.btn-cancel');
    
    confirmBtn.addEventListener('click', () => {
        confirmDiv.remove();
        if (typeof onConfirm === 'function') {
            onConfirm();
        }
    });
    
    cancelBtn.addEventListener('click', () => {
        confirmDiv.remove();
        if (typeof onCancel === 'function') {
            onCancel();
        }
    });
    
    // Auto-remover após 30 segundos se não for respondida
    setTimeout(() => {
        if (confirmDiv.parentNode) {
            confirmDiv.remove();
            if (typeof onCancel === 'function') {
                onCancel();
            }
        }
    }, 30000);
    
    return confirmDiv;
}

// ============================================================================
// FUNÇÃO PRINCIPAL PARA ABRIR MODAIS
// ============================================================================

/**
 * Função principal para abrir modais de formulário
 */
function openFormModal(title, formHtml, formId, submitUrl) {
    console.log('🔧 Abrindo modal:', title);
    console.log('🔍 Form ID:', formId);
    console.log('🔍 Submit URL:', submitUrl);
    
    // Remover modal anterior se existir
    const existingModal = document.querySelector('.modal.show');
    if (existingModal) {
        // Verificar se bootstrap.Modal.getInstance existe (Bootstrap 4) ou usar abordagem alternativa (Bootstrap 5)
        if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined' && typeof bootstrap.Modal.getInstance === 'function') {
            const bsModal = bootstrap.Modal.getInstance(existingModal);
            if (bsModal) {
                bsModal.hide();
            }
        } else if (existingModal._bsModal) {
            // Bootstrap 5 - usar instância armazenada
            try {
                existingModal._bsModal.hide();
            } catch (error) {
                console.warn('⚠️ Erro ao usar instância Bootstrap 5:', error);
            }
        } else {
            // Fallback: esconder manualmente
            existingModal.style.display = 'none';
            existingModal.classList.remove('show');
            document.body.classList.remove('modal-open');
            
            // Remover backdrop se existir
            const backdrop = document.querySelector('.modal-backdrop');
            if (backdrop) {
                backdrop.remove();
            }
        }
        existingModal.remove();
    }
    
    // Criar ID único para o modal
    const modalId = 'formModal_' + Date.now();
    
    // Criar HTML do modal
    const modalHtml = `
        <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
            <div class="modal-dialog modal-xl modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="${modalId}Label">
                            <i class="fas fa-edit me-2"></i>${title}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ${formHtml}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-2"></i>Cancelar
                        </button>
                        <button type="submit" form="${formId}" class="btn btn-primary">
                            <i class="fas fa-save me-2"></i>Salvar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Inserir modal no body
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    
    // Configurar envio do formulário
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('📝 Formulário submetido:', formId);
            
            // Coletar dados do formulário
            const formData = new FormData(form);
            
            // Mostrar loading no botão
            const submitBtn = form.querySelector('button[type="submit"]');
            let originalText = '';
            if (submitBtn) {
                originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Salvando...';
                submitBtn.disabled = true;
            }
            
            // Enviar dados
            fetch(submitUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                console.log('📋 Resposta recebida:', data);
                
                if (data.success) {
                    // Sucesso - mostrar mensagem e fechar modal
                    showSuccessMessage(data.message || 'Operação realizada com sucesso!');
                    
                    // Fechar modal
                    const modal = form.closest('.modal');
                    if (modal) {
                        // Verificar se bootstrap.Modal.getInstance existe (Bootstrap 4) ou usar abordagem alternativa (Bootstrap 5)
                        if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined' && typeof bootstrap.Modal.getInstance === 'function') {
                            const bootstrapModal = bootstrap.Modal.getInstance(modal);
                            if (bootstrapModal) {
                                bootstrapModal.hide();
                            }
                        } else if (modal._bsModal) {
                            // Bootstrap 5 - usar instância armazenada
                            try {
                                modal._bsModal.hide();
                            } catch (error) {
                                console.warn('⚠️ Erro ao usar instância Bootstrap 5:', error);
                            }
                        } else {
                            // Fallback: esconder manualmente
                            modal.style.display = 'none';
                            modal.classList.remove('show');
                            document.body.classList.remove('modal-open');
                            
                            // Remover backdrop se existir
                            const backdrop = document.querySelector('.modal-backdrop');
                            if (backdrop) {
                                backdrop.remove();
                            }
                        }
                    }
                    
                    // Recarregar página após um pequeno delay
                    setTimeout(() => {
                        window.location.reload();
                    }, 1500);
                    
                } else {
                    // Erro - mostrar mensagem de erro
                    showErrorMessage(data.message || 'Erro ao processar formulário');
                    
                    // Aplicar erros de validação se houver
                    if (data.errors) {
                        displayFormErrors(data.errors);
                    }
                }
            })
            .catch(error => {
                console.error('❌ Erro ao enviar formulário:', error);
                showErrorMessage('Erro de conexão. Tente novamente.');
            })
            .finally(() => {
                // Restaurar botão
                if (submitBtn) {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }
            });
        });
    }
    
    // Abrir modal
    const modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
    
    // Configurar funcionalidade do campo tipo personalizado para documentos
    if (formId === 'documentoForm') {
        setupDocumentoTipoPersonalizado();
    }
    
    return modal;
}

// ============================================================================
// FUNÇÕES PARA ASSOCIADOS
// ============================================================================

function openAssociadoModal() {
    console.log('🔍 Abrindo modal de associado...');
    
    fetch('/associados/associados/modal/novo/')
        .then(response => {
            console.log('📡 Resposta recebida:', response.status, response.statusText);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response.json();
        })
        .then(data => {
            console.log('📋 Dados recebidos:', data);
            
            if (data.form_html) {
                console.log('✅ Form HTML recebido, tamanho:', data.form_html.length);
                
                if (typeof window.openFormModal === 'function') {
                    console.log('✅ Usando openFormModal');
                    openFormModal(
                        'Novo Associado',
                        data.form_html,
                        'associadoForm',
                        '/associados/associados/modal/novo/'
                    );
                } else {
                    console.warn('⚠️ openFormModal não disponível, usando fallback');
                    // Fallback: criar modal básico
                    createFallbackModal(
                        'Novo Associado',
                        data.form_html,
                        'associadoForm'
                    );
                }
            } else {
                console.error('❌ Form HTML não encontrado nos dados');
                console.error('Dados recebidos:', data);
                showErrorMessage('Erro: Formulário não foi carregado corretamente.');
            }
        })
        .catch(error => {
            console.error('❌ Erro ao carregar formulário:', error);
            
            // Tentar usar fallback
            console.log('🔄 Tentando usar modal de fallback...');
            createFallbackModal(
                'Novo Associado', 
                '<div class="alert alert-danger">Erro ao carregar formulário. Tente novamente.</div>', 
                'associadoForm'
            );
        });
}

function openAssociadoEditModal(associadoId) {
    fetch(`/associados/associados/modal/${associadoId}/editar/`)
        .then(response => response.json())
        .then(data => {
            if (data.form_html) {
                if (typeof window.openFormModal === 'function') {
                    openFormModal(
                        'Editar Associado',
                        data.form_html,
                        'associadoForm',
                        `/associados/associados/modal/${associadoId}/editar/`
                    );
                } else {
                    console.error('openFormModal não está disponível');
                    // Fallback: criar modal básico
                    createFallbackModal('Editar Associado', data.form_html, 'associadoForm');
                }
            } else if (data.errors) {
                // Se houver erros, exibir mensagem
                console.error('Erros recebidos:', data.errors);
                showErrorMessage('Erro ao carregar formulário: ' + (data.message || 'Erro desconhecido'));
                displayFormErrors(data.errors);
            }
        })
        .catch(error => {
            console.error('Erro ao carregar formulário:', error);
            showErrorMessage('Erro ao carregar formulário. Tente novamente.');
        });
}

// ============================================================================
// FUNÇÕES PARA DEPENDENTES
// ============================================================================

function openDependenteModal(associadoId = null) {
    let url = '/associados/dependentes/modal/novo/';
    if (associadoId) {
        url += `?associado=${associadoId}`;
    }
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.form_html) {
                if (typeof window.openFormModal === 'function') {
                    openFormModal(
                        'Novo Dependente',
                        data.form_html,
                        'dependenteForm',
                        url
                    );
                } else {
                    console.error('openFormModal não está disponível');
                    // Fallback: criar modal básico
                    createFallbackModal('Novo Dependente', data.form_html, 'dependenteForm');
                }
            }
        })
        .catch(error => {
            console.error('Erro ao carregar formulário:', error);
            showErrorMessage('Erro ao carregar formulário. Tente novamente.');
        });
}

function openDependenteEditModal(dependenteId) {
    fetch(`/associados/dependentes/modal/${dependenteId}/editar/`)
        .then(response => response.json())
        .then(data => {
            if (data.form_html) {
                if (typeof window.openFormModal === 'function') {
                    openFormModal(
                        'Editar Dependente',
                        data.form_html,
                        'dependenteForm',
                        `/associados/dependentes/modal/${dependenteId}/editar/`
                    );
                } else {
                    console.error('openFormModal não está disponível');
                    // Fallback: criar modal básico
                    createFallbackModal('Editar Dependente', data.form_html, 'dependenteForm');
                }
            }
        })
        .catch(error => {
            console.error('Erro ao carregar formulário:', error);
            showErrorMessage('Erro ao carregar formulário. Tente novamente.');
        });
}

// ============================================================================
// FUNÇÕES PARA DOCUMENTOS
// ============================================================================

function openDocumentoModal(associadoId = null, dependenteId = null) {
    let url = '/associados/documentos/modal/novo/';
    let params = new URLSearchParams();
    
    if (associadoId) {
        params.append('associado', associadoId);
    }
    if (dependenteId) {
        params.append('dependente', dependenteId);
    }
    
    if (params.toString()) {
        url += '?' + params.toString();
    }
    
    fetch(url, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
        .then(response => {
            console.log('📡 Resposta recebida:', response.status, response.statusText);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('📋 Dados recebidos:', data);
            if (data.form_html) {
                openFormModal(
                    'Novo Documento',
                    data.form_html,
                    'documentoForm',
                    url
                );
            }
        })
        .catch(error => {
            console.error('Erro ao carregar formulário:', error);
            showErrorMessage('Erro ao carregar formulário. Tente novamente.');
        });
}

function openDocumentoEditModal(documentoId) {
    fetch(`/associados/documentos/modal/${documentoId}/editar/`)
        .then(response => response.json())
        .then(data => {
            if (data.form_html) {
                openFormModal(
                    'Editar Documento',
                    data.form_html,
                    'documentoForm',
                    `/associados/documentos/modal/${documentoId}/editar/`
                );
            }
        })
        .catch(error => {
            console.error('Erro ao carregar formulário:', error);
            showErrorMessage('Erro ao carregar formulário. Tente novamente.');
        });
}

// ============================================================================
// FUNÇÕES PARA PRÉ-CADASTRO
// ============================================================================

function openPreCadastroModal() {
    fetch('/associados/pre-cadastro/modal/')
        .then(response => response.json())
        .then(data => {
            if (data.form_html) {
                openFormModal(
                    'Pré-Cadastro de Associado',
                    data.form_html,
                    'preCadastroForm',
                    '/associados/pre-cadastro/modal/'
                );
            }
        })
        .catch(error => {
            console.error('Erro ao carregar formulário:', error);
            showErrorMessage('Erro ao carregar formulário. Tente novamente.');
        });
}

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

// Função para confirmar exclusão
function confirmarExclusao(url, mensagem = 'Tem certeza que deseja excluir este item?') {
    showConfirmMessage(mensagem, () => {
        // Redirecionar para a URL de exclusão
        window.location.href = url;
    });
}

// Função para abrir modal de confirmação personalizado
function confirmarAcao(titulo, mensagem, callback) {
    showConfirmMessage(mensagem, callback);
}

// Função para aplicar máscaras nos campos (simplificada)
function aplicarMascaras() {
    console.log('🔧 Aplicando máscaras nos campos...');
    
    // Máscara para CPF
    const cpfFields = document.querySelectorAll('input[name*="cpf"], input[name*="CPF"]');
    cpfFields.forEach(field => {
        field.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 11) {
                e.target.value = value.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
            }
        });
    });
    
    // Máscara para telefone
    const telefoneFields = document.querySelectorAll('input[name*="telefone"], input[name*="celular"]');
    telefoneFields.forEach(field => {
        field.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 11) {
                if (value.length === 11) {
                    e.target.value = value.replace(/(\d{2})(\d{5})(\d{4})/, '($1) $2-$3');
                } else if (value.length === 10) {
                    e.target.value = value.replace(/(\d{2})(\d{4})(\d{4})/, '($1) $2-$3');
                } else {
                    e.target.value = value;
                }
            }
        });
    });
    
    // Máscara para CEP
    const cepFields = document.querySelectorAll('input[name*="cep"], input[name*="CEP"]');
    cepFields.forEach(field => {
        field.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length <= 8) {
                e.target.value = value.replace(/(\d{5})(\d{3})/, '$1-$2');
            }
        });
    });
    
    console.log('✅ Máscaras aplicadas com sucesso');
}

// Inicialização quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Sistema de Modais Associados inicializado');

// Debug: Confirmar que as funções estão disponíveis
console.log('🔍 Funções de mensagens disponíveis (Associados):', {
    showSuccessMessage: typeof window.showSuccessMessage,
    showErrorMessage: typeof window.showErrorMessage,
    removeMessages: typeof window.removeMessages
});
    
    // Aplicar máscaras nos campos
    aplicarMascaras();
    
    // Registrar no Modal Loader se disponível
    if (typeof window.ModalLoader !== 'undefined') {
        window.ModalLoader.register('associados');
        console.log('📝 Módulo Associados registrado no Modal Loader');
    }
});

// Função de fallback para criar modal básico quando openFormModal não estiver disponível
function createFallbackModal(title, formHtml, formId) {
    console.log('🔧 Criando modal de fallback para:', title);
    
    try {
        // Remover modais de fallback existentes
        const existingModals = document.querySelectorAll('[id^="fallbackModal_"]');
        existingModals.forEach(modal => modal.remove());
        
        // Criar modal básico
        const modalId = 'fallbackModal_' + Date.now();
        const modalHtml = `
            <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
                <div class="modal-dialog modal-xl modal-dialog-scrollable">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="${modalId}Label">${title}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            ${formHtml}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="submit" form="${formId}" class="btn btn-primary">Salvar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Inserir no body
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Criar e mostrar modal
        const modalElement = document.getElementById(modalId);
        if (modalElement && typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined') {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();
            
            // Configurar envio do formulário
            const form = document.getElementById(formId);
            if (form) {
                console.log('🔧 Configurando envio do formulário de fallback');
                form.addEventListener('submit', (e) => {
                    e.preventDefault();
                    console.log('📤 Formulário enviado via fallback');
                    
                    // Coletar dados do formulário
                    const formData = new FormData(form);
                    const submitUrl = form.action || '/associados/associados/modal/novo/';
                    
                    // Enviar dados
                    fetch(submitUrl, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-Requested-With': 'XMLHttpRequest',
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            showSuccessMessage(data.message || 'Associado criado com sucesso!');
                            modal.hide();
                            // Recarregar página se necessário
                            if (data.reload) {
                                location.reload();
                            }
                        } else {
                            showErrorMessage('Erro: ' + (data.message || 'Erro desconhecido'));
                            if (data.errors) {
                                displayFormErrors(data.errors);
                            }
                        }
                    })
                    .catch(error => {
                        console.error('Erro ao enviar formulário:', error);
                        showErrorMessage('Erro ao enviar formulário. Verifique o console para mais detalhes.');
                    });
                });
            }
            
            return modal;
        } else {
            console.error('❌ Bootstrap não está disponível para criar modal de fallback');
            // Fallback: mostrar formulário em uma nova janela
            const newWindow = window.open('', '_blank', 'width=800,height=600');
            newWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>${title}</title>
                    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                </head>
                <body>
                    <div class="container mt-4">
                        <h2>${title}</h2>
                        ${formHtml}
                    </div>
                </body>
                </html>
            `);
        }
    } catch (error) {
        console.error('❌ Erro ao criar modal de fallback:', error);
        // Último recurso: mostrar formulário em alerta
        showErrorMessage(`Erro ao abrir modal para ${title}. Verifique o console para mais detalhes.`);
    }
}

// ============================================================================
// FUNÇÃO PARA EXIBIR ERROS DE VALIDAÇÃO
// ============================================================================

function displayFormErrors(errors) {
    if (!errors) return;
    
    console.log('🔍 Exibindo erros de validação:', errors);
    
    // Limpar erros anteriores
    document.querySelectorAll('.is-invalid').forEach(el => {
        el.classList.remove('is-invalid');
    });
    document.querySelectorAll('.invalid-feedback').forEach(el => {
        el.remove();
    });
    // Limpar alertas de erro anteriores
    document.querySelectorAll('.alert-danger').forEach(el => {
        el.remove();
    });
    
    // Marcar campos com erro
    Object.keys(errors).forEach(fieldName => {
        // Tratar erros gerais (__all__)
        if (fieldName === '__all__') {
            console.log('🔍 Processando erro __all__:', errors[fieldName]);
            
            // Tentar encontrar o formulário ativo (dentro do modal aberto)
            let form = document.querySelector('.modal.show form');
            if (!form) {
                form = document.querySelector('form');
            }
            
            console.log('🔍 Formulário encontrado:', form);
            
            if (form) {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger mb-3';
                errorDiv.style.cssText = 'display: block !important; position: relative !important; z-index: 9999 !important;';
                errorDiv.innerHTML = `
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    <strong>Erro de Validação:</strong><br>
                    ${Array.isArray(errors[fieldName]) ? errors[fieldName].join('<br>') : errors[fieldName]}
                `;
                form.insertBefore(errorDiv, form.firstChild);
                
                // Garantir que o modal permaneça aberto e o erro seja visível
                const modal = form.closest('.modal');
                if (modal) {
                    modal.classList.add('show');
                    modal.style.display = 'block';
                    modal.setAttribute('aria-hidden', 'false');
                }
                
                // Scroll para o topo do formulário para mostrar o erro
                form.scrollIntoView({ behavior: 'smooth', block: 'start' });
                
                console.log('✅ Erro __all__ exibido no formulário');
            } else {
                console.warn('⚠️ Formulário não encontrado para exibir erro __all__');
            }
            return;
        }
        
        // Tratar erros de campos específicos
        console.log(`🔍 Processando erro do campo: ${fieldName}`);
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.classList.add('is-invalid');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = Array.isArray(errors[fieldName]) ? errors[fieldName].join(', ') : errors[fieldName];
            
            field.parentNode.appendChild(errorDiv);
            console.log(`✅ Erro exibido para o campo: ${fieldName}`);
        } else {
            // Campo não encontrado - pode ser um campo oculto
            console.warn(`⚠️ Campo não encontrado: ${fieldName} (pode ser um campo oculto)`);
            
            // Se for um campo oculto importante, mostrar erro geral
            if (fieldName === 'atendimento' || fieldName === 'associado' || fieldName === 'dependente') {
                const form = document.querySelector('.modal.show form') || document.querySelector('#documentoForm') || document.querySelector('#associadoForm');
                if (form) {
                    let alertDiv = form.querySelector('.alert-warning');
                    if (!alertDiv) {
                        alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-warning';
                        form.insertBefore(alertDiv, form.firstChild);
                    }
                    
                    alertDiv.innerHTML = `
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        <strong>Erro no campo ${fieldName}:</strong> ${Array.isArray(errors[fieldName]) ? errors[fieldName].join(', ') : errors[fieldName]}
                    `;
                }
            }
        }
    });
    
    // Scroll para o primeiro erro
    const firstError = document.querySelector('.is-invalid');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstError.focus();
    }
}

// ============================================================================
// FUNÇÃO PARA CONFIGURAR CAMPO TIPO PERSONALIZADO DE DOCUMENTOS
// ============================================================================

function setupDocumentoTipoPersonalizado() {
    const tipoSelect = document.getElementById('id_tipo');
    const tipoPersonalizadoRow = document.getElementById('tipo-personalizado-row');
    const tipoPersonalizadoField = document.getElementById('id_tipo_personalizado');
    
    if (!tipoSelect || !tipoPersonalizadoRow || !tipoPersonalizadoField) {
        console.warn('⚠️ Elementos do campo tipo personalizado não encontrados');
        return;
    }
    
    function toggleTipoPersonalizado() {
        if (tipoSelect.value === 'outro') {
            tipoPersonalizadoRow.style.display = 'block';
            tipoPersonalizadoField.required = true;
            console.log('✅ Campo tipo personalizado exibido');
        } else {
            tipoPersonalizadoRow.style.display = 'none';
            tipoPersonalizadoField.required = false;
            tipoPersonalizadoField.value = ''; // Limpar o campo quando ocultar
            console.log('✅ Campo tipo personalizado ocultado');
        }
    }
    
    // Verificar estado inicial
    toggleTipoPersonalizado();
    
    // Adicionar listener para mudanças
    tipoSelect.addEventListener('change', toggleTipoPersonalizado);
    
    console.log('✅ Funcionalidade tipo personalizado configurada');
}
