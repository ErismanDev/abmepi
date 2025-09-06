/**
 * Sistema de Modais para ASEJUS
 * Sistema limpo e moderno com mensagens flutuantes
 * 
 * FUNCIONALIDADES IMPLEMENTADAS:
 * ✅ Mensagens flutuantes (sucesso, erro, aviso, informação)
 * ✅ Mensagens de progresso com barra de progresso
 * ✅ Mensagens de confirmação interativas
 * ✅ Sistema de modais robusto com fallbacks
 * ✅ Integração com Modal Loader
 * ✅ Funções para advogados e documentos
 */

console.log('🚀 Sistema de Modais ASEJUS carregado');

// Polyfill para bootstrap.Modal.getInstance em Bootstrap 5
(function() {
    const initPolyfill = function() {
        if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined' && !bootstrap.Modal.getInstance) {
            console.log('🔧 Adicionando polyfill para bootstrap.Modal.getInstance no modais_assejus.js');
            bootstrap.Modal.getInstance = function(element) {
                if (!element) return null;
                
                // Verificar se já existe uma instância armazenada
                if (element._bsModal) {
                    return element._bsModal;
                }
                
                // Tentar encontrar instância existente através de dados internos do Bootstrap 5
                try {
                    const dataKey = 'bs.modal';
                    if (element._element && element._element[dataKey]) {
                        element._bsModal = element._element[dataKey];
                        return element._bsModal;
                    }
                    
                    // Como último recurso, retornar null para indicar que não há instância
                    return null;
                } catch (error) {
                    console.warn('⚠️ Erro ao buscar instância existente do modal no polyfill:', error);
                    return null;
                }
            };
            console.log('✅ Polyfill bootstrap.Modal.getInstance aplicado com sucesso no modais_assejus.js');
        } else if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined' && bootstrap.Modal.getInstance) {
            console.log('✅ bootstrap.Modal.getInstance já disponível (Bootstrap 4)');
        } else if (typeof bootstrap === 'undefined') {
            console.warn('⚠️ Bootstrap não encontrado no modais_assejus.js, tentando novamente em 100ms...');
            setTimeout(initPolyfill, 100);
        }
    };
    
    // Tentar inicializar imediatamente
    initPolyfill();
    
    // Fallback: tentar novamente quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPolyfill);
    }
    
    // Fallback adicional: tentar novamente após um delay para garantir que Bootstrap esteja carregado
    setTimeout(initPolyfill, 500);
    setTimeout(initPolyfill, 1000);
})();

// Debug: Confirmar que as funções estão disponíveis
console.log('🔍 Funções de mensagens disponíveis:', {
    showSuccessMessage: typeof window.showSuccessMessage,
    showErrorMessage: typeof window.showErrorMessage,
    removeMessages: typeof window.removeMessages
});

// Teste da função closeModal
setTimeout(() => {
    console.log('🧪 Testando disponibilidade da função closeModal:', typeof window.closeModal);
    if (typeof window.closeModal === 'function') {
        console.log('✅ Função closeModal carregada com sucesso!');
    } else {
        console.error('❌ Função closeModal NÃO foi carregada!');
    }
}, 1000);

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
 * Exibir erros de validação no formulário
 */
window.showValidationErrors = function(errors) {
    console.log('🔍 Exibindo erros de validação:', errors);
    
    // Limpar erros anteriores
    clearValidationErrors();
    
    // Exibir erros para cada campo
    Object.keys(errors).forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            // Adicionar classe de erro
            field.classList.add('is-invalid');
            
            // Criar ou atualizar mensagem de erro
            let errorDiv = field.parentNode.querySelector('.invalid-feedback');
            if (!errorDiv) {
                errorDiv = document.createElement('div');
                errorDiv.className = 'invalid-feedback d-block';
                field.parentNode.appendChild(errorDiv);
            }
            
            // Exibir primeiro erro do campo
            const errorMessage = Array.isArray(errors[fieldName]) ? errors[fieldName][0] : errors[fieldName];
            errorDiv.textContent = errorMessage;
        }
    });
};

/**
 * Limpar erros de validação
 */
window.clearValidationErrors = function() {
    // Remover classes de erro
    document.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
    
    // Remover mensagens de erro
    document.querySelectorAll('.invalid-feedback').forEach(errorDiv => {
        errorDiv.remove();
    });
};

/**
 * Exibir mensagem de progresso
 */
window.showProgressMessage = function(message) {
    console.log('⏳ Progresso:', message);
    
    // Remover mensagens anteriores
    removeMessages();
    
    // Criar mensagem de progresso
    const progressDiv = document.createElement('div');
    progressDiv.className = 'alert alert-info alert-dismissible fade show position-fixed';
    progressDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    progressDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="spinner-border spinner-border-sm me-2" role="status">
                <span class="visually-hidden">Carregando...</span>
            </div>
            ${message}
        </div>
    `;
    
    document.body.appendChild(progressDiv);
};

/**
 * Remover mensagem de progresso
 */
window.removeProgressMessage = function() {
    document.querySelectorAll('.alert-info.position-fixed').forEach(alert => {
        alert.remove();
    });
};

// ============================================================================
// FUNÇÕES PRINCIPAIS
// ============================================================================

/**
 * Abrir modal para criar novo atendimento
 */
window.openAtendimentoModal = function() {
    console.log('🔧 Abrindo modal para novo atendimento');

    // Limpar erros anteriores
    if (typeof clearValidationErrors === 'function') {
        clearValidationErrors();
    }
    
    console.log('📡 Fazendo requisição para:', '/assejus/atendimentos/modal/novo/');
    
    fetch('/assejus/atendimentos/modal/novo/')
        .then(response => {
            console.log('📥 Resposta recebida:', response);
            console.log('📊 Status:', response.status);
            console.log('📊 OK:', response.ok);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response.json();
        })
        .then(data => {
            console.log('📋 Dados recebidos:', data);
            console.log('🔍 Form HTML recebido:', data.form_html ? 'SIM' : 'NÃO');
            
            if (data.form_html) {
                console.log('✅ Dados válidos, criando modal...');
                
                // Criar modal dinamicamente
                const modalId = 'createAtendimentoModal_' + Date.now();
                const modalHtml = `
                    <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
                        <div class="modal-dialog modal-lg modal-dialog-centered">
                            <div class="modal-content">
                                <div class="modal-header bg-primary text-white">
                                    <h5 class="modal-title" id="${modalId}Label">
                                        <i class="fas fa-gavel me-2"></i>Novo Atendimento
                                    </h5>
                                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="container-fluid p-0">
                                        ${data.form_html}
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                                        <i class="fas fa-times me-2"></i>Cancelar
                                    </button>
                                    <button type="submit" form="atendimentoForm" class="btn btn-primary">
                                        <i class="fas fa-save me-2"></i>Salvar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Remover modal anterior se existir
                const existingModal = document.getElementById(modalId);
                if (existingModal) {
                    existingModal.remove();
                }
                
                // Adicionar novo modal ao body
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                
                // Configurar envio do formulário
                                        const form = document.getElementById('atendimentoForm');
                        if (form) {
                            form.addEventListener('submit', function(e) {
                                e.preventDefault();
                                submitAtendimentoForm(form, modalId);
                            });
                            
                            // Inicializar validações do formulário
                            if (typeof window.initializeAtendimentoForm === 'function') {
                                window.initializeAtendimentoForm();
                            }
                        }
                
                // Abrir modal
                const modal = new bootstrap.Modal(document.getElementById(modalId));
                modal.show();
                
            } else {
                console.error('❌ Form HTML não recebido');
                showErrorMessage('Erro: Formulário não foi carregado corretamente.');
            }
        })
        .catch(error => {
            console.error('❌ Erro ao carregar formulário:', error);
            showErrorMessage('Erro ao carregar formulário: ' + error.message);
        });
};

/**
 * Abrir modal para criar novo advogado
 */
window.openAdvogadoModal = function() {
    console.log('🔧 Abrindo modal para novo advogado');

    // Limpar erros anteriores
    clearValidationErrors();
    
    console.log('📡 Fazendo requisição para:', '/assejus/advogados/modal/novo/');
    
    fetch('/assejus/advogados/modal/novo/')
        .then(response => {
            console.log('📥 Resposta recebida:', response);
            console.log('📊 Status:', response.status);
            console.log('📊 OK:', response.ok);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response.json();
        })
        .then(data => {
            console.log('📋 Dados recebidos:', data);
            console.log('🔍 Success:', data.success);
            console.log('🔍 Form HTML recebido:', data.form_html ? 'SIM' : 'NÃO');
            
            if (data.success && data.form_html) {
                console.log('✅ Dados válidos, criando modal...');
                
                // Criar modal dinamicamente
                const modalId = 'createModal_' + Date.now();
                const modalHtml = `
                    <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
                        <div class="modal-dialog modal-lg modal-dialog-centered">
                            <div class="modal-content">
                                <div class="modal-header bg-primary text-white">
                                    <h5 class="modal-title" id="${modalId}Label">
                                        <i class="fas fa-user-plus me-2"></i>Novo Advogado
                                    </h5>
                                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="container-fluid p-0">
                                        ${data.form_html}
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                                        <i class="fas fa-times me-2"></i>Cancelar
                                    </button>
                                    <button type="submit" form="advogadoForm" class="btn btn-primary">
                                        <i class="fas fa-save me-2"></i>Salvar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Remover modal anterior se existir
                const existingModal = document.getElementById(modalId);
                if (existingModal) {
                    existingModal.remove();
                }
                
                // Adicionar novo modal ao body
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                
                // Abrir modal
                const modal = new bootstrap.Modal(document.getElementById(modalId));
                modal.show();
                
            } else {
                console.error('❌ Dados inválidos ou form_html não recebido');
                showErrorMessage('Erro: Formulário não foi carregado corretamente.');
            }
        })
        .catch(error => {
            console.error('❌ Erro ao carregar formulário:', error);
            showErrorMessage('Erro ao carregar formulário: ' + error.message);
        });
};

/**
 * Enviar formulário de atendimento
 */
window.submitAtendimentoForm = function(form, modalId) {
    console.log('🔧 Enviando formulário de atendimento');
    
    // Mostrar mensagem de progresso
    if (typeof showProgressMessage === 'function') {
        showProgressMessage('Salvando atendimento...');
    }
    
    // Coletar dados do formulário
    const formData = new FormData(form);
    
    // Fazer requisição POST
    fetch('/assejus/atendimentos/modal/novo/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('📋 Resposta do servidor:', data);
        
        if (data.success) {
            // Sucesso
            if (typeof showSuccessMessage === 'function') {
                showSuccessMessage(data.message || 'Atendimento criado com sucesso!');
            }
            
            // Fechar modal de forma robusta
            const modalElement = document.getElementById(modalId);
            if (modalElement) {
                try {
                    // Tentar usar Bootstrap se disponível
                    if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined') {
                        // Verificar se bootstrap.Modal.getInstance existe (Bootstrap 4) ou usar abordagem alternativa (Bootstrap 5)
                        if (typeof bootstrap.Modal.getInstance === 'function') {
                            // Bootstrap 4 - usar getInstance
                            const bsModal = bootstrap.Modal.getInstance(modalElement);
                            if (bsModal) {
                                console.log('🔒 Fechando via Bootstrap 4...');
                                bsModal.hide();
                                console.log('✅ Modal fechado via Bootstrap 4:', modalId);
                            }
                        } else if (modalElement._bsModal) {
                            // Bootstrap 5 - usar instância armazenada
                            try {
                                console.log('🔒 Fechando via Bootstrap 5 (instância armazenada)...');
                                modalElement._bsModal.hide();
                                console.log('✅ Modal fechado via Bootstrap 5:', modalId);
                            } catch (bsError) {
                                console.log('⚠️ Erro ao usar instância Bootstrap 5, usando fallback:', bsError);
                            }
                        }
                    }
                    
                    // Fallback: método manual direto
                    console.log('🔄 Usando método manual para fechar modal...');
                    
                    // Remover classes de visibilidade
                    modalElement.classList.remove('show');
                    modalElement.style.display = 'none';
                    modalElement.setAttribute('aria-hidden', 'true');
                    
                    // Limpar classes do body
                    document.body.classList.remove('modal-open');
                    
                    // Remover todos os backdrops
                    const backdrops = document.querySelectorAll('.modal-backdrop');
                    backdrops.forEach(backdrop => {
                        console.log('🧹 Removendo backdrop:', backdrop);
                        backdrop.remove();
                    });
                    
                    // Restaurar scroll do body
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                    
                    console.log('✅ Modal fechado via método manual direto');
                    
                } catch (error) {
                    console.error('❌ Erro ao fechar modal:', error);
                    
                    // Último recurso: remover o modal completamente
                    try {
                        modalElement.remove();
                        console.log('✅ Modal removido completamente como último recurso');
                    } catch (removeError) {
                        console.error('❌ Erro ao remover modal:', removeError);
                    }
                }
            } else {
                console.warn('⚠️ Modal não encontrado para fechar:', modalId);
            }
            
            // Recarregar página se necessário
            if (data.reload) {
                console.log('🔄 Recarregando página em 2 segundos...');
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            }
        } else {
            // Erro de validação
            console.error('❌ Erros de validação:', data.errors);
            displayFormErrors(data.errors);
            
            if (typeof showErrorMessage === 'function') {
                showErrorMessage(data.message || 'Erro na validação do formulário.');
            }
        }
    })
    .catch(error => {
        console.error('❌ Erro ao enviar formulário:', error);
        if (typeof showErrorMessage === 'function') {
            showErrorMessage('Erro ao enviar formulário: ' + error.message);
        }
    })
    .finally(() => {
        // Remover mensagem de progresso
        if (typeof removeProgressMessage === 'function') {
            removeProgressMessage();
        }
    });
};

/**
 * Abrir modal de edição do atendimento
 */
window.openAtendimentoEditModal = function(atendimentoId) {
    console.log('🔧 Abrindo modal de edição para atendimento:', atendimentoId);

    // Limpar erros anteriores
    if (typeof clearValidationErrors === 'function') {
        clearValidationErrors();
    }
    
    const url = `/assejus/atendimentos/modal/${atendimentoId}/editar/`;
    console.log('📡 Fazendo requisição para:', url);
    
    fetch(url)
        .then(response => {
            console.log('📥 Resposta recebida:', response);
            console.log('📊 Status:', response.status);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response.json();
        })
        .then(data => {
            console.log('📋 Dados recebidos:', data);
            console.log('🔍 Form HTML recebido:', data.form_html ? 'SIM' : 'NÃO');
            
            if (data.form_html) {
                console.log('✅ Dados válidos, criando modal...');
                
                // Criar modal dinamicamente
                const modalId = 'editAtendimentoModal_' + atendimentoId;
                const modalHtml = `
                    <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
                        <div class="modal-dialog modal-lg modal-dialog-centered">
                            <div class="modal-content">
                                <div class="modal-header bg-warning text-dark">
                                    <h5 class="modal-title" id="${modalId}Label">
                                        <i class="fas fa-edit me-2"></i>Editar Atendimento
                                    </h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="container-fluid p-0">
                                        ${data.form_html}
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                                        <i class="fas fa-times me-2"></i>Cancelar
                                    </button>
                                    <button type="submit" form="atendimentoForm" class="btn btn-warning">
                                        <i class="fas fa-save me-2"></i>Atualizar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Remover modal anterior se existir
                const existingModal = document.getElementById(modalId);
                if (existingModal) {
                    existingModal.remove();
                }
                
                // Adicionar novo modal ao body
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                
                // Configurar envio do formulário
                                        const form = document.getElementById('atendimentoForm');
                        if (form) {
                            form.addEventListener('submit', function(e) {
                                e.preventDefault();

                                submitAtendimentoEditForm(form, modalId, atendimentoId);
                            });
                            
                            // Inicializar validações do formulário
                            if (typeof window.initializeAtendimentoForm === 'function') {
                                window.initializeAtendimentoForm();
                            }
                        }
                
                // Abrir modal
                const modal = new bootstrap.Modal(document.getElementById(modalId));
                modal.show();
                
            } else {
                console.error('❌ Form HTML não recebido');
                showErrorMessage('Erro: Formulário não foi carregado corretamente.');
            }
        })
        .catch(error => {
            console.error('❌ Erro ao carregar formulário:', error);
            showErrorMessage('Erro ao carregar formulário: ' + error.message);
        });
};

/**
 * Enviar formulário de edição de atendimento
 */
window.submitAtendimentoEditForm = function(form, modalId, atendimentoId) {
    console.log('🔧 submitAtendimentoEditForm chamada com:', { form, modalId, atendimentoId });
    
    // Mostrar mensagem de progresso
    if (typeof showProgressMessage === 'function') {
        showProgressMessage('Atualizando atendimento...');
    }
    
    // Coletar dados do formulário
    const formData = new FormData(form);
    console.log('📋 Dados do formulário coletados:', Object.fromEntries(formData));
    
    // Fazer requisição POST para a URL de edição
    fetch(`/assejus/atendimentos/modal/${atendimentoId}/editar/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }

    })
    .then(response => response.json())
    .then(data => {
        console.log('📋 Resposta do servidor:', data);
        
        if (data.success) {
            console.log('✅ Sucesso na atualização, fechando modal...');
            
            // Sucesso
            if (typeof showSuccessMessage === 'function') {
                showSuccessMessage(data.message || 'Atendimento atualizado com sucesso!');
            }
            
            // Fechar modal de forma robusta
            console.log('🔧 Tentando fechar modal com ID:', modalId);
            const modalElement = document.getElementById(modalId);
            if (modalElement) {
                try {
                    // Tentar usar Bootstrap se disponível
                    if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined') {
                        // Verificar se bootstrap.Modal.getInstance existe (Bootstrap 4) ou usar abordagem alternativa (Bootstrap 5)
                        if (typeof bootstrap.Modal.getInstance === 'function') {
                            // Bootstrap 4 - usar getInstance
                            const bsModal = bootstrap.Modal.getInstance(modalElement);
                            if (bsModal) {
                                console.log('🔒 Fechando via Bootstrap 4...');
                                bsModal.hide();
                                console.log('✅ Modal fechado via Bootstrap 4:', modalId);
                            }
                        } else if (modalElement._bsModal) {
                            // Bootstrap 5 - usar instância armazenada
                            try {
                                console.log('🔒 Fechando via Bootstrap 5 (instância armazenada)...');
                                modalElement._bsModal.hide();
                                console.log('✅ Modal fechado via Bootstrap 5:', modalId);
                            } catch (bsError) {
                                console.log('⚠️ Erro ao usar instância Bootstrap 5, usando fallback:', bsError);
                            }
                        }
                    }
                    
                    // Fallback: método manual direto
                    console.log('🔄 Usando método manual para fechar modal...');
                    
                    // Remover classes de visibilidade
                    modalElement.classList.remove('show');
                    modalElement.style.display = 'none';
                    modalElement.setAttribute('aria-hidden', 'true');
                    
                    // Limpar classes do body
                    document.body.classList.remove('modal-open');
                    
                    // Remover todos os backdrops
                    const backdrops = document.querySelectorAll('.modal-backdrop');
                    backdrops.forEach(backdrop => {
                        console.log('🧹 Removendo backdrop:', backdrop);
                        backdrop.remove();
                    });
                    
                    // Restaurar scroll do body
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                    
                    console.log('✅ Modal fechado via método manual direto');
                    
                } catch (error) {
                    console.error('❌ Erro ao fechar modal:', error);
                    
                    // Último recurso: remover o modal completamente
                    try {
                        modalElement.remove();
                        console.log('✅ Modal removido completamente como último recurso');
                    } catch (removeError) {
                        console.error('❌ Erro ao remover modal:', removeError);
                    }
                }
            } else {
                console.warn('⚠️ Modal não encontrado para fechar:', modalId);
            }
            
            // Recarregar página se necessário
            if (data.reload) {
                console.log('🔄 Recarregando página em 2 segundos...');
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            }
        } else {
            console.log('❌ Falha na atualização, mostrando erros...');
            // Erro de validação
            console.error('❌ Erros de validação:', data.errors);
            displayFormErrors(data.errors);
            
            if (typeof showErrorMessage === 'function') {
                showErrorMessage(data.message || 'Erro na validação do formulário.');
            }
        }
    })
    .catch(error => {
        console.error('❌ Erro ao enviar formulário:', error);
        if (typeof showErrorMessage === 'function') {
            showErrorMessage('Erro ao enviar formulário: ' + error.message);
        }
    })
    .finally(() => {
        // Remover mensagem de progresso
        if (typeof removeProgressMessage === 'function') {
            removeProgressMessage();
        }
    });
};

/**
 * Abrir modal de detalhes do atendimento
 */
window.openAtendimentoDetailModal = function(atendimentoId) {
    console.log('🔧 Abrindo modal de detalhes para atendimento:', atendimentoId);
    
    // Implementar modal de detalhes se necessário
    showErrorMessage('Funcionalidade de detalhes em desenvolvimento.');
};

/**
 * Abrir modal de edição do advogado
 */
window.openAdvogadoEditModal = function(advogadoId) {
    console.log('🔧 Abrindo modal de edição para advogado:', advogadoId);
    console.log('🔍 Função chamada com sucesso');

    // Limpar erros anteriores
    if (typeof clearValidationErrors === 'function') {
        clearValidationErrors();
        console.log('✅ clearValidationErrors executado');
    } else {
        console.warn('⚠️ clearValidationErrors não está disponível');
    }
    
    const url = `/assejus/advogados/modal/${advogadoId}/editar/`;
    console.log('📡 Fazendo requisição para:', url);
    
    fetch(url)
        .then(response => {
            console.log('📥 Resposta recebida:', response);
            console.log('📊 Status:', response.status);
            console.log('📊 OK:', response.ok);
            console.log('📊 Headers:', response.headers);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response.json();
        })
        .then(data => {
            console.log('📋 Dados recebidos:', data);
            console.log('🔍 Success:', data.success);
            console.log('🔍 Form HTML recebido:', data.form_html ? 'SIM' : 'NÃO');
            console.log('🔍 Tamanho do HTML:', data.form_html ? data.form_html.length : 'N/A');
            
            if (data.success && data.form_html) {
                console.log('✅ Dados válidos, criando modal de edição...');
                
                // Criar modal de edição dinamicamente
                const modalId = 'editModal_' + advogadoId;
                console.log('🔧 Modal ID criado:', modalId);
                
                const modalHtml = `
                    <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
                        <div class="modal-dialog modal-lg modal-dialog-centered">
                            <div class="modal-content">
                                <div class="modal-header bg-warning text-dark">
                                    <h5 class="modal-title" id="${modalId}Label">
                                        <i class="fas fa-edit me-2"></i>Editar Advogado
                                    </h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="container-fluid p-0">
                                        ${data.form_html}
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                                        <i class="fas fa-times me-2"></i>Cancelar
                                    </button>
                                    <button type="submit" form="advogadoForm" class="btn btn-warning">
                                        <i class="fas fa-save me-2"></i>Salvar
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                console.log('🔧 HTML do modal criado, tamanho:', modalHtml.length);
                
                // Remover modal anterior se existir
                const existingModal = document.getElementById(modalId);
                if (existingModal) {
                    console.log('🗑️ Removendo modal anterior');
                    existingModal.remove();
                }
                
                // Adicionar novo modal ao body
                console.log('🔧 Inserindo modal no DOM...');
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                console.log('✅ Modal inserido no DOM');
                
                // Verificar se o modal foi inserido
                const modalElement = document.getElementById(modalId);
                if (modalElement) {
                    console.log('✅ Modal encontrado no DOM');
                    console.log('🔍 Modal HTML:', modalElement.outerHTML.substring(0, 500) + '...');
                    
                    try {
                        const modal = new bootstrap.Modal(modalElement);
                        console.log('✅ Modal Bootstrap criado');
                        modal.show();
                        console.log('✅ Modal aberto com sucesso');
                    } catch (error) {
                        console.error('❌ Erro ao abrir modal:', error);
                        showErrorMessage('Erro ao abrir modal: ' + error.message);
                    }
                } else {
                    console.error('❌ Modal não encontrado no DOM após inserção');
                    showErrorMessage('Erro: Modal não foi criado corretamente');
                }
                
            } else {
                console.error('❌ Dados inválidos ou form_html não recebido');
                console.error('Data completo:', data);
                showErrorMessage('Erro: Formulário não foi carregado corretamente. Verifique o console para mais detalhes.');
            }
         })
         .catch(error => {
             console.error('❌ Erro ao carregar formulário:', error);
             console.error('Stack trace:', error.stack);
             showErrorMessage('Erro ao carregar formulário: ' + error.message);
         });
};

/**
 * Abrir modal de detalhes do advogado
 */
window.openAdvogadoDetailModal = function(advogadoId) {
    console.log('🔧 Abrindo modal de detalhes para advogado:', advogadoId);

    // Limpar erros anteriores
    clearValidationErrors();
    
    console.log('📡 Fazendo requisição para:', `/assejus/advogados/${advogadoId}/detalhes-modal/`);
    
    fetch(`/assejus/advogados/${advogadoId}/detalhes-modal/`)
        .then(response => {
            console.log('📥 Resposta recebida:', response);
            console.log('📊 Status:', response.status);
            console.log('📊 OK:', response.ok);
            console.log('📊 Headers:', response.headers);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response.json();
        })
        .then(data => {
            console.log('📋 Dados recebidos:', data);
            console.log('🔍 Success:', data.success);
            console.log('🔍 Modal HTML recebido:', data.modal_html ? 'SIM' : 'NÃO');
            console.log('🔍 Tamanho do Modal HTML:', data.modal_html ? data.modal_html.length : 'N/A');
            console.log('🔍 Primeiros 200 caracteres do HTML:', data.modal_html ? data.modal_html.substring(0, 200) + '...' : 'N/A');
            
            if (data.success && data.modal_html) {
                console.log('✅ Dados válidos, criando modal dinamicamente...');
                
                // Criar modal dinamicamente (padrão dos associados)
                const modalId = 'advogadoDetailModal_' + advogadoId;
                const modalHtml = data.modal_html.replace('advogadoDetailModal', modalId);
                
                // Remover modal anterior se existir
                const existingModal = document.getElementById(modalId);
                if (existingModal) {
                    console.log('🗑️ Removendo modal anterior');
                    existingModal.remove();
                }
                
                // Adicionar novo modal ao body
                console.log('🔧 Inserindo modal no DOM...');
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                console.log('✅ Modal inserido no DOM');
                
                // Verificar se o modal foi inserido
                const modalElement = document.getElementById(modalId);
                if (modalElement) {
                    console.log('✅ Modal encontrado no DOM');
                    console.log('🔍 Modal HTML:', modalElement.outerHTML.substring(0, 500) + '...');
                    
                    try {
                        const modal = new bootstrap.Modal(modalElement);
                        console.log('✅ Modal Bootstrap criado');
                        modal.show();
                        console.log('✅ Modal aberto com sucesso');
                    } catch (error) {
                        console.error('❌ Erro ao abrir modal:', error);
                        showErrorMessage('Erro ao abrir modal: ' + error.message);
                    }
                } else {
                    console.error('❌ Modal não encontrado no DOM após inserção');
                    showErrorMessage('Erro: Modal não foi criado corretamente');
                }
                
            } else {
                console.error('❌ Dados inválidos ou modal_html não recebido');
                console.error('Data completo:', data);
                
                // Tentar mostrar modal mesmo sem HTML
                if (data.message) {
                    showDetailModal('Erro ao Carregar Detalhes', `
                        <div class="alert alert-danger">
                            <h5><i class="fas fa-exclamation-triangle me-2"></i>Erro ao Carregar Detalhes</h5>
                            <p>${data.message}</p>
                            <button type="button" class="btn btn-primary" onclick="openAdvogadoDetailModal(${advogadoId})">
                                <i class="fas fa-redo me-2"></i>Tentar Novamente
                            </button>
                        </div>
                    `);
                } else {
                    showErrorMessage('Erro: Detalhes não foram carregados corretamente. Verifique o console para mais detalhes.');
                }
            }
        })
        .catch(error => {
            console.error('❌ Erro ao carregar detalhes:', error);
            console.error('Stack trace:', error.stack);
            showErrorMessage('Erro ao carregar detalhes: ' + error.message);
        });
};

/**
 * Abrir modal para criar novo andamento
 */
window.openAndamentoModal = function() {
    console.log('🔧 Abrindo modal para novo andamento');

    // Limpar erros anteriores
    if (typeof clearValidationErrors === 'function') {
        clearValidationErrors();
    }
    
    console.log('📡 Fazendo requisição para:', '/assejus/andamentos/modal/novo/');
    
    fetch('/assejus/andamentos/modal/novo/')
        .then(response => {
            console.log('📥 Resposta recebida:', response);
            console.log('📊 Status:', response.status);
            console.log('📊 OK:', response.ok);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response.json();
        })
        .then(data => {
            console.log('📋 Dados recebidos:', data);
            
            if (data.form_html) {
                // Criar ID único para o modal
                const modalId = 'andamentoModal_' + Date.now();
                
                // Criar HTML do modal
                const modalHtml = `
                    <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
                        <div class="modal-dialog modal-xl">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="${modalId}Label">
                                        <i class="fas fa-tasks me-2"></i>
                                        Novo Andamento
                                    </h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    ${data.form_html}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Adicionar novo modal ao body
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                
                // Configurar envio do formulário
                const form = document.getElementById('andamentoForm');
                if (form) {
                    form.addEventListener('submit', function(e) {
                        e.preventDefault();
                        submitAndamentoForm(form, modalId);
                    });
                }
                
                // Abrir modal
                const modal = new bootstrap.Modal(document.getElementById(modalId));
                modal.show();
                
            } else {
                console.error('❌ Form HTML não recebido');
                showErrorMessage('Erro: Formulário não foi carregado corretamente.');
            }
        })
        .catch(error => {
            console.error('❌ Erro ao carregar formulário:', error);
            showErrorMessage('Erro ao carregar formulário: ' + error.message);
        });
};

/**
 * Abrir modal para editar andamento existente
 */
window.openAndamentoEditModal = function(andamentoId) {
    console.log('🔧 Abrindo modal para editar andamento:', andamentoId);

    // Limpar erros anteriores
    if (typeof clearValidationErrors === 'function') {
        clearValidationErrors();
    }
    
    console.log('📡 Fazendo requisição para:', `/assejus/andamentos/modal/${andamentoId}/editar/`);
    
    fetch(`/assejus/andamentos/modal/${andamentoId}/editar/`)
        .then(response => {
            console.log('📥 Resposta recebida:', response);
            console.log('📊 Status:', response.status);
            console.log('📊 OK:', response.ok);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return response.json();
        })
        .then(data => {
            console.log('📋 Dados recebidos:', data);
            
            if (data.form_html) {
                // Criar ID único para o modal
                const modalId = 'andamentoEditModal_' + Date.now();
                
                // Criar HTML do modal
                const modalHtml = `
                    <div class="modal fade" id="${modalId}" tabindex="-1" aria-labelledby="${modalId}Label" aria-hidden="true">
                        <div class="modal-dialog modal-xl">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="${modalId}Label">
                                        <i class="fas fa-edit me-2"></i>
                                        Editar Andamento
                                    </h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    ${data.form_html}
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                
                // Adicionar modal ao DOM
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                
                // Mostrar modal
                const modalElement = document.getElementById(modalId);
                if (modalElement) {
                    // Configurar envio do formulário
                    const form = document.getElementById('andamentoForm');
                    if (form) {
                        form.addEventListener('submit', function(e) {
                            e.preventDefault();
                            submitAndamentoForm(form, modalId);
                        });
                        
                        // Configurar funcionalidades do formulário de andamento
                        setupAndamentoForm(form);
                    }
                    
                    const modal = new bootstrap.Modal(modalElement);
                    modal.show();
                    
                    // Limpar modal quando fechado
                    modalElement.addEventListener('hidden.bs.modal', function() {
                        modalElement.remove();
                    });
                }
            } else {
                console.error('❌ HTML do formulário não recebido');
                showErrorMessage('Erro ao carregar formulário de edição.');
            }
        })
        .catch(error => {
            console.error('❌ Erro ao carregar formulário:', error);
            showErrorMessage('Erro ao carregar formulário: ' + error.message);
        });
};

/**
 * Enviar formulário de andamento
 */
window.submitAndamentoForm = function(form, modalId) {
    console.log('🔧 Enviando formulário de andamento');
    console.log('📋 Formulário:', form);
    console.log('🎯 Action do formulário:', form.action);
    console.log('🆔 Modal ID:', modalId);
    
    // Mostrar mensagem de progresso
    if (typeof showProgressMessage === 'function') {
        showProgressMessage('Salvando andamento...');
    }
    
    // Coletar dados do formulário
    const formData = new FormData(form);
    
    // Debug: mostrar todos os dados do formulário
    console.log('📊 Dados do formulário:');
    for (let [key, value] of formData.entries()) {
        console.log(`  ${key}: ${value}`);
    }
    
    // Fazer requisição POST usando a action do formulário
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    })
    .then(response => response.json())
    .then(data => {
        console.log('📋 Resposta do servidor:', data);
        
        if (data.success) {
            // Sucesso
            if (typeof showSuccessMessage === 'function') {
                showSuccessMessage(data.message || 'Andamento criado com sucesso!');
            }
            
            // Fechar modal de forma robusta
            const modalElement = document.getElementById(modalId);
            if (modalElement) {
                try {
                    // Tentar usar Bootstrap se disponível
                    if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined') {
                        // Verificar se bootstrap.Modal.getInstance existe (Bootstrap 4) ou usar abordagem alternativa (Bootstrap 5)
                        if (typeof bootstrap.Modal.getInstance === 'function') {
                            // Bootstrap 4 - usar getInstance
                            const bsModal = bootstrap.Modal.getInstance(modalElement);
                            if (bsModal) {
                                console.log('🔒 Fechando via Bootstrap 4...');
                                bsModal.hide();
                                console.log('✅ Modal fechado via Bootstrap 4:', modalId);
                            }
                        } else if (modalElement._bsModal) {
                            // Bootstrap 5 - usar instância armazenada
                            try {
                                console.log('🔒 Fechando via Bootstrap 5 (instância armazenada)...');
                                modalElement._bsModal.hide();
                                console.log('✅ Modal fechado via Bootstrap 5:', modalId);
                            } catch (bsError) {
                                console.log('⚠️ Erro ao usar instância Bootstrap 5, usando fallback:', bsError);
                            }
                        }
                    }
                    
                    // Fallback: método manual direto
                    console.log('🔄 Usando método manual para fechar modal...');
                    
                    // Remover classes de visibilidade
                    modalElement.classList.remove('show');
                    modalElement.style.display = 'none';
                    modalElement.setAttribute('aria-hidden', 'true');
                    
                    // Limpar classes do body
                    document.body.classList.remove('modal-open');
                    
                    // Remover todos os backdrops
                    const backdrops = document.querySelectorAll('.modal-backdrop');
                    backdrops.forEach(backdrop => {
                        console.log('🧹 Removendo backdrop:', backdrop);
                        backdrop.remove();
                    });
                    
                    // Restaurar scroll do body
                    document.body.style.overflow = '';
                    document.body.style.paddingRight = '';
                    
                    console.log('✅ Modal fechado via método manual direto');
                    
                } catch (error) {
                    console.error('❌ Erro ao fechar modal:', error);
                    
                    // Último recurso: remover o modal completamente
                    try {
                        modalElement.remove();
                        console.log('✅ Modal removido completamente como último recurso');
                    } catch (removeError) {
                        console.error('❌ Erro ao remover modal:', removeError);
                    }
                }
            } else {
                console.warn('⚠️ Modal não encontrado para fechar:', modalId);
            }
            
            // Recarregar página se necessário
            if (data.reload) {
                console.log('🔄 Recarregando página em 2 segundos...');
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
            }
        } else {
            // Erro de validação
            console.error('❌ Erros de validação:', data.errors);
            displayFormErrors(data.errors);
            
            if (typeof showErrorMessage === 'function') {
                showErrorMessage(data.message || 'Erro na validação do formulário.');
            }
        }
    })
    .catch(error => {
        console.error('❌ Erro ao enviar formulário:', error);
        if (typeof showErrorMessage === 'function') {
            showErrorMessage('Erro ao enviar formulário: ' + error.message);
        }
    })
    .finally(() => {
        // Remover mensagem de progresso
        if (typeof removeProgressMessage === 'function') {
            removeProgressMessage();
        }
    });
};

// ============================================================================
// FUNÇÕES AUXILIARES
// ============================================================================

/**
 * Criar modal de fallback
 */
function createFallbackModal(titulo, conteudo, formId) {
    console.log('🔧 Criando modal de fallback:', { titulo, formId });

    // Remover modal anterior se existir
    const existingModal = document.getElementById('fallbackModal');
    if (existingModal) {
        existingModal.remove();
    }

    const modalHtml = `
        <div class="modal fade" id="fallbackModal" tabindex="-1" aria-labelledby="fallbackModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-xl">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="fallbackModalLabel">
                            <i class="fas fa-user-plus me-2"></i>
                            ${titulo}
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ${conteudo}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-2"></i>Cancelar
                        </button>
                        <button type="button" class="btn btn-primary" id="assejusFallbackSubmit">
                            <i class="fas fa-save me-2"></i>Salvar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Inserir modal no DOM
    document.body.insertAdjacentHTML('beforeend', modalHtml);

    // Configurar botão de submit
    const submitBtn = document.getElementById('assejusFallbackSubmit');
    if (submitBtn) {
        submitBtn.addEventListener('click', function(e) {
            e.preventDefault();
            handleFormSubmit(e, formId);
        });
    }

    // Abrir modal
    const modal = new bootstrap.Modal(document.getElementById('fallbackModal'));
    modal.show();
}

/**
 * Mostrar modal de detalhes
 */
function showDetailModal(titulo, conteudo) {
    console.log('🔧 Mostrando modal de detalhes:', titulo);
    console.log('🔍 Conteúdo recebido:', conteudo ? 'SIM' : 'NÃO');
    console.log('🔍 Tamanho do conteúdo:', conteudo ? conteudo.length : 'N/A');
    console.log('🔍 Primeiros 200 caracteres:', conteudo ? conteudo.substring(0, 200) + '...' : 'N/A');

    // Remover modal anterior se existir
    const existingModal = document.getElementById('detailModal');
    if (existingModal) {
        console.log('🗑️ Removendo modal anterior');
        existingModal.remove();
    }

    const modalHtml = `
        <div class="modal fade" id="detailModal" tabindex="-1" aria-labelledby="detailModalLabel" aria-hidden="true">
            <div class="modal-dialog modal-xl modal-dialog-scrollable">
                <div class="modal-content">
                    <div class="modal-header bg-primary text-white">
                        <h5 class="modal-title" id="detailModalLabel">
                            <i class="fas fa-eye me-2"></i>${titulo}
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        ${conteudo}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-outline-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-times me-2"></i>Fechar
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    console.log('🔧 Inserindo modal no DOM...');
    document.body.insertAdjacentHTML('beforeend', modalHtml);
    console.log('✅ Modal inserido no DOM');

    // Verificar se o modal foi inserido
    const modalElement = document.getElementById('detailModal');
    if (modalElement) {
        console.log('✅ Modal encontrado no DOM');
        console.log('🔍 Modal HTML:', modalElement.outerHTML.substring(0, 500) + '...');
        
        // Abrir modal
        try {
            const modal = new bootstrap.Modal(modalElement);
            console.log('✅ Modal Bootstrap criado');
            modal.show();
            console.log('✅ Modal aberto com sucesso');
        } catch (error) {
            console.error('❌ Erro ao abrir modal:', error);
            showErrorMessage('Erro ao abrir modal: ' + error.message);
        }
    } else {
        console.error('❌ Modal não encontrado no DOM após inserção');
        showErrorMessage('Erro: Modal não foi criado corretamente');
    }
}

/**
 * Exibir erros de validação do formulário
 */
function displayFormErrors(errors) {
    console.log('🔍 Exibindo erros de validação:', errors);
    
    // Limpar erros anteriores
    document.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
    document.querySelectorAll('.invalid-feedback').forEach(error => {
        error.remove();
    });
    
    // Processar cada erro
    Object.keys(errors).forEach(fieldName => {
        if (fieldName === '__all__') {
            // Erro geral do formulário
            console.log('🔍 Processando erro __all__:', errors[fieldName]);
            const form = document.querySelector('.modal.show form') || document.querySelector('#documentoForm');
            if (form) {
                // Criar alerta de erro
                let alertDiv = form.querySelector('.alert-danger');
                if (!alertDiv) {
                    alertDiv = document.createElement('div');
                    alertDiv.className = 'alert alert-danger';
                    alertDiv.style.cssText = 'display: block !important; position: relative !important; z-index: 9999 !important;';
                    form.insertBefore(alertDiv, form.firstChild);
                }
                
                alertDiv.innerHTML = `
                    <h6 class="alert-heading">
                        <i class="fas fa-exclamation-triangle me-2"></i>Erro de Validação
                    </h6>
                    <p class="mb-0">${Array.isArray(errors[fieldName]) ? errors[fieldName].join(', ') : errors[fieldName]}</p>
                `;
                
                // Forçar modal a ficar aberto
                const modal = form.closest('.modal');
                if (modal) {
                    modal.classList.add('show');
                    modal.style.display = 'block';
                }
                
                // Scroll para o formulário
                form.scrollIntoView({ behavior: 'smooth', block: 'center' });
                
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
            // Campo não encontrado - verificar se é um campo que foi removido intencionalmente
            if (fieldName === 'atendimento') {
                // Para o campo atendimento, verificar se é um erro de campo removido intencionalmente
                const form = document.querySelector('.modal.show form') || document.querySelector('#documentoForm');
                if (form) {
                    // Verificar se existe informação de associado (indicando que atendimento foi predefinido)
                    const associadoInfo = form.querySelector('.alert-info');
                    if (associadoInfo) {
                        // Campo foi removido intencionalmente, o erro pode ser de validação backend
                        console.log(`ℹ️ Campo ${fieldName} foi removido intencionalmente (atendimento pré-definido)`);
                        
                        // Mostrar erro geral
                        let alertDiv = form.querySelector('.alert-danger');
                        if (!alertDiv) {
                            alertDiv = document.createElement('div');
                            alertDiv.className = 'alert alert-danger';
                            form.insertBefore(alertDiv, form.firstChild);
                        }
                        
                        alertDiv.innerHTML = `
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            <strong>Erro de validação:</strong> ${Array.isArray(errors[fieldName]) ? errors[fieldName].join(', ') : errors[fieldName]}
                        `;
                    } else {
                        // Campo deveria estar presente
                        console.warn(`⚠️ Campo obrigatório não encontrado: ${fieldName}`);
                        
                        let alertDiv = form.querySelector('.alert-warning');
                        if (!alertDiv) {
                            alertDiv = document.createElement('div');
                            alertDiv.className = 'alert alert-warning';
                            form.insertBefore(alertDiv, form.firstChild);
                        }
                        
                        alertDiv.innerHTML = `
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            <strong>Campo obrigatório:</strong> ${Array.isArray(errors[fieldName]) ? errors[fieldName].join(', ') : errors[fieldName]}
                        `;
                    }
                }
            } else {
                // Outros campos não encontrados
                console.warn(`⚠️ Campo não encontrado: ${fieldName}`);
                
                // Se for um campo importante, mostrar erro geral
                if (fieldName === 'associado') {
                    const form = document.querySelector('.modal.show form') || document.querySelector('#documentoForm');
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
        }
    });
    
    // Scroll para o primeiro erro
    const firstError = document.querySelector('.is-invalid');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstError.focus();
    }
}

/**
 * Manipular envio do formulário
 */
function handleFormSubmit(e, formId) {
    // Verificar se é um evento válido
    if (e && typeof e.preventDefault === 'function') {
        e.preventDefault();
    }
    
    console.log('🚀 Formulário enviado via fallback');
    
    // Encontrar o formulário correto
    let form;
    if (e && e.target) {
        form = e.target;
    } else if (e && e.currentTarget) {
        form = e.currentTarget;
    } else {
        // Fallback: procurar pelo formulário no modal
        form = document.querySelector('.modal.show form') || document.querySelector('#advogadoForm');
    }
    
    if (!form) {
        console.error('❌ Formulário não encontrado');
        showErrorMessage('Erro: Formulário não encontrado');
        return;
    }
    
    console.log('🔍 Formulário encontrado:', form);
    console.log('🔍 Action do formulário:', form.action);
    
    // Limpar erros anteriores
    clearValidationErrors();
    
    const formData = new FormData(form);
    
    // Mostrar loading no botão
    let submitBtn = form.querySelector('button[type="submit"]');
    if (!submitBtn) {
        submitBtn = document.querySelector('#assejusModalSubmit');
    }
    if (!submitBtn) {
        submitBtn = document.querySelector('#assejusFallbackSubmit');
    }
    if (!submitBtn) {
        submitBtn = document.querySelector('.modal.show .btn-primary');
    }
    
    if (!submitBtn) {
        console.error('❌ Botão submit não encontrado');
        showErrorMessage('Erro: Botão de envio não encontrado');
        return;
    }
    
    let originalText = '';
    if (submitBtn) {
        originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Salvando...';
        submitBtn.disabled = true;
    }
    
    // Enviar formulário
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => {
        console.log('📡 Resposta recebida:', response.status, response.statusText);
        console.log('📊 Content-Type:', response.headers.get('Content-Type'));
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('Content-Type');
        if (contentType && contentType.includes('application/json')) {
            return response.json();
        } else {
            // Se não for JSON, pode ser HTML (erro de validação ou redirecionamento)
            return response.text().then(text => {
                console.error('❌ Resposta não é JSON:', text.substring(0, 200));
                throw new Error('Resposta do servidor não é JSON válido');
            });
        }
    })
    .then(data => {
        if (data.success) {
            // Sucesso
            showSuccessMessage(data.message);
            
            // Fechar modal PRIMEIRO
            const modal = form.closest('.modal');
            if (modal) {
                // Usar a função closeModal se disponível
                if (typeof window.closeModal === 'function') {
                    // Encontrar o ID do modal
                    const modalId = modal.id;
                    if (modalId) {
                        window.closeModal(modalId);
                    } else {
                        // Fallback manual se não tiver ID
                        modal.style.display = 'none';
                        modal.classList.remove('show');
                        document.body.classList.remove('modal-open');
                        
                        // Remover backdrop se existir
                        const backdrop = document.querySelector('.modal-backdrop');
                        if (backdrop) {
                            backdrop.remove();
                        }
                    }
                } else {
                    // Fallback para versões antigas
                    try {
                        if (typeof bootstrap !== 'undefined' && 
                            typeof bootstrap.Modal !== 'undefined' && 
                            typeof bootstrap.Modal.getInstance === 'function') {
                            
                            const bootstrapModal = bootstrap.Modal.getInstance(modal);
                            if (bootstrapModal) {
                                bootstrapModal.hide();
                                console.log('✅ Modal fechado via Bootstrap Modal.getInstance');
                            }
                        } else if (modal._bsModal) {
                            // Bootstrap 5 - usar instância armazenada
                            try {
                                modal._bsModal.hide();
                                console.log('✅ Modal fechado via Bootstrap 5 (instância armazenada)');
                            } catch (bsError) {
                                console.log('⚠️ Erro ao usar instância Bootstrap 5:', bsError);
                            }
                        } else {
                            // Fallback: usar jQuery se disponível
                            if (typeof $ !== 'undefined' && typeof $.fn.modal !== 'undefined') {
                                $(modal).modal('hide');
                                console.log('✅ Modal fechado via jQuery fallback');
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
                                
                                console.log('✅ Modal fechado via fallback manual');
                            }
                        }
                    } catch (error) {
                        console.warn('⚠️ Erro ao fechar modal, usando fallback:', error);
                        
                        // Fallback de emergência
                        modal.style.display = 'none';
                        modal.classList.remove('show');
                        document.body.classList.remove('modal-open');
                    }
                }
            }
            
            // Recarregar página se necessário (após fechar o modal)
            if (data.reload) {
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
            
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
}



// Funções de mensagens flutuantes já definidas no início do arquivo

/**
 * Processar erros de validação
 */
function handleValidationErrors(errors, message) {
    console.log('❌ Processando erros de validação:', errors);
    
    // Exibir resumo dos erros no topo do modal
    showErrorSummaryInModal(errors, Object.keys(errors).length, message);
    
    // Aplicar estilos de erro aos campos
    setTimeout(() => {
        applyErrorStylesToFields(errors);
        scrollToFirstError();
    }, 100);
}

/**
 * Exibir resumo de erros no topo do modal
 */
function showErrorSummaryInModal(errors, errorCount, errorSummary) {
    console.log('🔍 showErrorSummaryInModal chamada com:', { errors, errorCount, errorSummary });
    
    // Encontrar o modal atual
    const modal = document.querySelector('.modal.show');
    if (!modal) {
        console.warn('⚠️ Modal não encontrado');
        return;
    }
    
    const modalBody = modal.querySelector('.modal-body');
    if (!modalBody) {
        console.warn('⚠️ Modal body não encontrado');
        return;
    }
    
    // Remover alertas de erro anteriores
    const existingAlerts = modalBody.querySelectorAll('.alert-danger.border-danger');
    existingAlerts.forEach(alert => alert.remove());
    
    // Criar alerta de erro estilizado
    const errorAlert = document.createElement('div');
    errorAlert.className = 'alert alert-danger border-danger mb-4';
    errorAlert.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-exclamation-triangle fa-2x me-3 text-danger"></i>
            <div>
                <h5 class="alert-heading mb-2">
                    <i class="fas fa-times-circle me-2"></i>Formulário com Erros de Validação
                </h5>
                <p class="mb-2">${errorSummary || `Foram encontrados ${errorCount} erro(s) no formulário.`}</p>
                <p class="mb-0 small text-muted">Por favor, corrija os campos destacados em vermelho e tente novamente.</p>
            </div>
        </div>
        <button type="button" class="btn-close position-absolute top-0 end-0 m-3" aria-label="Fechar" onclick="this.parentElement.remove()"></button>
    `;
    errorAlert.style.position = 'relative';
    
    // Inserir no topo do modal
    modalBody.insertBefore(errorAlert, modalBody.firstChild);
    console.log('✅ Resumo de erros inserido no modal');
}

/**
 * Aplicar estilos de erro aos campos
 */
function applyErrorStylesToFields(errors) {
    if (!errors) {
        console.warn('⚠️ Nenhum erro fornecido para applyErrorStylesToFields');
        return;
    }
    
    console.log('🔍 Aplicando estilos de erro para:', errors);
    console.log('🔍 Total de campos com erro:', Object.keys(errors).length);
    
    let camposProcessados = 0;
    let camposComErro = 0;
    
    Object.keys(errors).forEach(fieldName => {
        console.log(`🔍 Procurando campo: ${fieldName}`);
        
        // Tentar diferentes seletores para encontrar o campo
        let field = document.querySelector(`[name="${fieldName}"]`);
        
        if (!field) {
            // Tentar por ID
            field = document.getElementById(fieldName);
        }
        
        if (!field) {
            // Tentar por nome com diferentes variações
            field = document.querySelector(`input[name="${fieldName}"], select[name="${fieldName}"], textarea[name="${fieldName}"]`);
        }
        
        if (field) {
            console.log(`✅ Campo encontrado: ${fieldName}`, field);
            camposComErro++;
            
            // Adicionar classe de erro
            field.classList.add('is-invalid');
            
            // Adicionar classe de erro ao grupo do campo
            const formGroup = field.closest('.form-group, .mb-3, .col-md-6, .col-md-4, .col-md-3');
            if (formGroup) {
                formGroup.classList.add('has-error');
                console.log(`✅ Grupo do campo marcado com erro:`, formGroup);
            }
            
            // Criar mensagem de erro abaixo do campo
            createFieldErrorMessage(field, errors[fieldName]);
        } else {
            console.warn(`⚠️ Campo não encontrado: ${fieldName}`);
        }
        
        camposProcessados++;
    });
    
    console.log(`📊 Resumo: ${camposProcessados} campos processados, ${camposComErro} campos com erro aplicado`);
}

/**
 * Criar mensagem de erro para um campo específico
 */
function createFieldErrorMessage(field, errorMessages) {
    if (!field || !errorMessages) return;
    
    // Remover mensagens de erro anteriores
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Criar nova mensagem de erro
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback d-block';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-1"></i>
        ${Array.isArray(errorMessages) ? errorMessages.join(', ') : errorMessages}
    `;
    
    // Inserir após o campo
    field.parentNode.insertBefore(errorDiv, field.nextSibling);
    console.log(`✅ Mensagem de erro criada para ${field.name}:`, errorMessages);
}

/**
 * Rolar para o primeiro campo com erro
 */
function scrollToFirstError() {
    const firstErrorField = document.querySelector('.is-invalid');
    if (firstErrorField) {
        firstErrorField.scrollIntoView({ 
            behavior: 'smooth', 
            block: 'center' 
        });
        console.log('✅ Rolado para o primeiro campo com erro');
    } else {
        console.warn('⚠️ Nenhum campo com erro encontrado para rolar');
    }
}

/**
 * Limpar todos os erros de validação
 */
function clearValidationErrors() {
    console.log('🧹 Limpando erros de validação...');
    
    // Remover classes de erro dos campos
    document.querySelectorAll('.is-invalid').forEach(field => {
        field.classList.remove('is-invalid');
    });
    
    // Remover classes de erro dos grupos
    document.querySelectorAll('.has-error').forEach(group => {
        group.classList.remove('has-error');
    });
    
    // Remover mensagens de erro
    document.querySelectorAll('.invalid-feedback').forEach(error => {
        error.remove();
    });
    
    // Remover alertas de erro
    document.querySelectorAll('.alert-danger.border-danger').forEach(alert => {
        alert.remove();
    });
    
    console.log('✅ Todos os erros de validação foram limpos');
}

// ============================================================================
// INICIALIZAÇÃO
// ============================================================================

// Aguardar DOM carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Sistema de Modais ASEJUS inicializado (Versão Limpa)');
    
    // Verificar se as funções estão disponíveis
    console.log('✅ openAdvogadoModal:', typeof window.openAdvogadoModal === 'function');
    console.log('✅ openAtendimentoModal:', typeof window.openAtendimentoModal === 'function');
    console.log('✅ submitAtendimentoForm:', typeof window.submitAtendimentoForm === 'function');
    console.log('✅ openAtendimentoEditModal:', typeof window.openAtendimentoEditModal === 'function');
    console.log('✅ submitAtendimentoEditForm:', typeof window.submitAtendimentoEditForm === 'function');
    console.log('✅ openAtendimentoDetailModal:', typeof window.openAtendimentoDetailModal === 'function');
    console.log('✅ openAdvogadoEditModal:', typeof window.openAdvogadoEditModal === 'function');
    console.log('✅ openAndamentoModal:', typeof window.openAndamentoModal === 'function');
    console.log('✅ closeModal:', typeof window.closeModal === 'function');

    // Registrar no Modal Loader se disponível
    if (typeof window.ModalLoader !== 'undefined') {
        window.ModalLoader.register('assejus');
        console.log('📝 Módulo ASSEJUS registrado no Modal Loader');
    }
    
    console.log('ℹ️ Modal de detalhes removido - usando apenas página completa');
    
    // Configurar envio de formulários via AJAX
    setupFormSubmission();
    
    // Configurar evento global para botões "Atualizar"
    setupGlobalButtonHandlers();
});

/**
 * Configurar envio de formulários via AJAX
 */
function setupFormSubmission() {
    // Interceptar envio de formulários
    document.addEventListener('submit', function(e) {
        // Handler para formulário de advogado
        if (e.target.id === 'advogadoForm') {
            e.preventDefault();
            console.log('📝 Formulário de advogado submetido via AJAX');
            
            const form = e.target;
            const formData = new FormData(form);
            const modal = form.closest('.modal');
            const modalId = modal ? modal.id : null;
            
            // Determinar URL baseada no modal
            let url;
            if (modalId && modalId.startsWith('editModal_')) {
                const advogadoId = modalId.replace('editModal_', '');
                url = `/assejus/advogados/modal/${advogadoId}/editar/`;
                console.log('🔧 Modal de edição detectado, ID:', advogadoId);
            } else {
                url = '/assejus/advogados/modal/novo/';
                console.log('🔧 Modal de criação detectado');
            }
            
            console.log('📡 Enviando para:', url);
            console.log('🔍 Modal ID:', modalId);
            console.log('🔍 Formulário:', form);
            console.log('🔍 Dados do formulário:', Object.fromEntries(formData));
            
            // Enviar formulário via AJAX
            fetch(url, {
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
                    
                    // Verificar se há informações de login (novo advogado)
                    if (data.login_info) {
                        const loginInfo = data.login_info;
                        const loginMessage = `
                            <div class="alert alert-success">
                                <h5><i class="fas fa-user-plus me-2"></i>Advogado Criado com Sucesso!</h5>
                                <p><strong>${data.message}</strong></p>
                                <hr>
                                <h6><i class="fas fa-key me-2"></i>Informações de Acesso:</h6>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="card border-success">
                                            <div class="card-body">
                                                <h6 class="card-title text-success">
                                                    <i class="fas fa-user me-2"></i>Dados de Login
                                                </h6>
                                                <ul class="list-unstyled mb-0">
                                                    <li><strong>Usuário:</strong> <code>${loginInfo.username}</code></li>
                                                    <li><strong>Senha Padrão:</strong> <code>${loginInfo.senha_padrao}</code></li>
                                                    <li><strong>Tipo:</strong> <span class="badge bg-primary">${loginInfo.tipo_usuario}</span></li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <div class="card border-warning">
                                            <div class="card-body">
                                                <h6 class="card-title text-warning">
                                                    <i class="fas fa-exclamation-triangle me-2"></i>Importante
                                                </h6>
                                                <ul class="list-unstyled mb-0">
                                                    <li><i class="fas fa-check-circle text-success me-2"></i>Guarde essas informações</li>
                                                    <li><i class="fas fa-check-circle text-success me-2"></i>Altere a senha no primeiro acesso</li>
                                                    <li><i class="fas fa-check-circle text-success me-2"></i>Use o CPF como usuário</li>
                                                </ul>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div class="mt-3">
                                    <button type="button" class="btn btn-outline-primary btn-sm" onclick="copiarInformacoesLogin('${loginInfo.username}', '${loginInfo.senha_padrao}')">
                                        <i class="fas fa-mouse-pointer me-2"></i>Preencher Campos de Login
                                    </button>
                                    <button type="button" class="btn btn-outline-success btn-sm ms-2" onclick="imprimirInformacoesLogin('${loginInfo.username}', '${loginInfo.senha_padrao}', '${data.message}')">
                                        <i class="fas fa-print me-2"></i>Imprimir
                                    </button>
                                </div>
                            </div>
                        `;
                        
                        // Mostrar modal com informações de login
                        showDetailModal('Informações de Acesso', loginMessage);
                        
                        // Não fechar o modal automaticamente para que o usuário possa ver as informações
                        return;
                    }
                    
                    // Fechar modal
                    if (modal) {
                        try {
                            // Tentar usar bootstrap.Modal.getInstance se disponível
                            if (typeof bootstrap !== 'undefined' && 
                                typeof bootstrap.Modal !== 'undefined' && 
                                typeof bootstrap.Modal.getInstance === 'function') {
                                
                                const bootstrapModal = bootstrap.Modal.getInstance(modal);
                                if (bootstrapModal) {
                                    bootstrapModal.hide();
                                    console.log('✅ Modal fechado via Bootstrap Modal.getInstance');
                                }
                            } else if (modal._bsModal) {
                                // Bootstrap 5 - usar instância armazenada
                                try {
                                    modal._bsModal.hide();
                                    console.log('✅ Modal fechado via Bootstrap 5 (instância armazenada)');
                                } catch (bsError) {
                                    console.log('⚠️ Erro ao usar instância Bootstrap 5:', bsError);
                                }
                            } else {
                                // Fallback: usar jQuery se disponível
                                if (typeof $ !== 'undefined' && typeof $.fn.modal !== 'undefined') {
                                    $(modal).modal('hide');
                                    console.log('✅ Modal fechado via jQuery fallback');
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
                                    
                                    console.log('✅ Modal fechado via fallback manual');
                                }
                            }
                        } catch (error) {
                            console.warn('⚠️ Erro ao fechar modal, usando fallback:', error);
                            
                            // Fallback de emergência
                            modal.style.display = 'none';
                            modal.classList.remove('show');
                            document.body.classList.remove('modal-open');
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
            });
        }
        

    });
}
 
/**
 * Função auxiliar para fechar modais de forma compatível com Bootstrap 5
 */
window.closeModal = function(modalId) {
    console.log('🔧 closeModal chamada com ID:', modalId);
    
    const modalElement = document.getElementById(modalId);
    if (!modalElement) {
        console.warn('⚠️ Modal não encontrado:', modalId);
        return false;
    }
    
    console.log('✅ Modal encontrado:', modalElement);
    console.log('🔍 Modal classes:', modalElement.className);
    console.log('🔍 Modal style display:', modalElement.style.display);
    
    try {
        // Primeiro tentar usar Bootstrap se disponível
        if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined') {
            // Verificar se bootstrap.Modal.getInstance existe (Bootstrap 4) ou usar abordagem alternativa (Bootstrap 5)
            if (typeof bootstrap.Modal.getInstance === 'function') {
                // Bootstrap 4 - usar getInstance
                const bsModal = bootstrap.Modal.getInstance(modalElement);
                if (bsModal) {
                    console.log('🔒 Fechando via Bootstrap 4...');
                    bsModal.hide();
                    console.log('✅ Modal fechado via Bootstrap 4:', modalId);
                    return true;
                }
            } else if (modalElement._bsModal) {
                // Bootstrap 5 - usar instância armazenada
                try {
                    console.log('🔒 Fechando via Bootstrap 5 (instância armazenada)...');
                    modalElement._bsModal.hide();
                    console.log('✅ Modal fechado via Bootstrap 5:', modalId);
                    return true;
                } catch (bsError) {
                    console.log('⚠️ Erro ao usar instância Bootstrap 5, usando fallback:', bsError);
                }
            }
        }
        
        // Fallback: método manual direto
        console.log('🔄 Usando método manual para fechar modal...');
        
        // Remover classes de visibilidade
        modalElement.classList.remove('show');
        modalElement.style.display = 'none';
        modalElement.setAttribute('aria-hidden', 'true');
        
        // Limpar classes do body
        document.body.classList.remove('modal-open');
        
        // Remover todos os backdrops
        const backdrops = document.querySelectorAll('.modal-backdrop');
        backdrops.forEach(backdrop => {
            console.log('🧹 Removendo backdrop:', backdrop);
            backdrop.remove();
        });
        
        // Restaurar scroll do body
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
        
        console.log('✅ Modal fechado via método manual direto');
        return true;
        
    } catch (error) {
        console.error('❌ Erro ao fechar modal:', error);
        
        // Último recurso: remover o modal completamente
        try {
            modalElement.remove();
            console.log('✅ Modal removido completamente como último recurso');
            return true;
        } catch (removeError) {
            console.error('❌ Erro ao remover modal:', removeError);
            return false;
        }
    }
};

/**
 * Configurar evento global para botões "Atualizar"
 */
function setupGlobalButtonHandlers() {
    console.log('🔧 Configurando handlers globais para botões...');
    
    document.addEventListener('click', function(e) {
        const target = e.target;
        
        // Verificar se é um botão ou link de documento (apenas se NÃO for um modal)
        if ((target.tagName === 'BUTTON' || target.tagName === 'A') && (
            target.textContent.trim().includes('Documento') || 
            target.textContent.trim().includes('Novo Documento') ||
            target.getAttribute('data-action') === 'documento' ||
            target.classList.contains('btn-documento')
        )) {
            // Verificar se é um botão/link de modal - se for, não interceptar
            if (target.getAttribute('data-bs-toggle') === 'modal' || 
                target.getAttribute('data-bs-target') === '#modalBase' ||
                target.href && target.href.includes('modal') ||
                target.closest('a[data-bs-toggle="modal"]')) {
                console.log('🖱️ Botão/link de documento modal detectado, permitindo comportamento padrão');
                return; // Permitir que o modal funcione normalmente
            }
            
            console.log('🖱️ Botão de documento clicado:', target.textContent.trim());
            
            // Tentar encontrar o ID do atendimento atual
            let atendimentoId = null;
            
            // Método 1: Verificar se há um atributo data-atendimento
            if (target.getAttribute('data-atendimento')) {
                atendimentoId = target.getAttribute('data-atendimento');
                console.log('🔍 Atendimento ID encontrado via data-atendimento:', atendimentoId);
            }

            // Método 3: Procurar na URL atual
            else {
                const urlMatch = window.location.pathname.match(/\/atendimentos\/(\d+)/);
                if (urlMatch) {
                    atendimentoId = urlMatch[1];
                    console.log('🔍 Atendimento ID encontrado via URL:', atendimentoId);
                } else {
                    // Método 4: Procurar em elementos da página
                    const atendimentoElement = document.querySelector('[data-atendimento-id]');
                    if (atendimentoElement) {
                        atendimentoId = atendimentoElement.getAttribute('data-atendimento-id');
                        console.log('🔍 Atendimento ID encontrado via elemento da página:', atendimentoId);
                    }
                }
            }
            
            if (atendimentoId) {
                console.log('✅ Atendimento ID encontrado, redirecionando para página do processo:', atendimentoId);
                // Redirecionar para a página do processo
                window.location.href = '/assejus/processos/2/';
            } else {
                console.error('❌ Não foi possível encontrar o ID do atendimento');
                showErrorMessage('Erro: Não foi possível identificar o atendimento atual. Tente novamente.');
            }
            
            return;
        }
        
        // Verificar se é um botão com texto "Atualizar"
        if (target.tagName === 'BUTTON' && target.textContent.trim().includes('Atualizar')) {
            console.log('🖱️ Botão "Atualizar" clicado:', target.textContent.trim());
            
            // Encontrar o formulário mais próximo
            const form = target.closest('form');
            if (form) {
                console.log('🔍 Formulário encontrado:', form.id);
                
                // Verificar se é um formulário de atendimento
                if (form.id === 'atendimentoForm') {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('🚀 Formulário de atendimento detectado, enviando...');
                    
                    // Encontrar o modal pai
                    const modal = target.closest('.modal');
                    if (modal) {
                        const modalId = modal.id;
                        console.log('🔍 Modal ID:', modalId);
                        
                        // Determinar se é edição ou criação
                        if (modalId.includes('editAtendimentoModal_')) {
                            const atendimentoId = modalId.replace('editAtendimentoModal_', '');
                            console.log('🔍 Atendimento ID para edição:', atendimentoId);
                            
                            // Chamar função de envio
                            if (typeof window.submitAtendimentoEditForm === 'function') {
                                window.submitAtendimentoEditForm(form, modalId, atendimentoId);
                            } else {
                                console.error('❌ Função submitAtendimentoEditForm não disponível');
                            }
                        } else {
                            console.log('🔍 Modal de criação detectado');
                            // Chamar função de criação
                            if (typeof window.submitAtendimentoForm === 'function') {
                                window.submitAtendimentoForm(form, modalId);
                            } else {
                                console.error('❌ Função submitAtendimentoForm não disponível');
                            }
                        }
                    } else {
                        console.warn('⚠️ Modal não encontrado');
                    }
                }
                // Verificar se é um formulário de advogado
                else if (form.id === 'advogadoForm') {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log('🚀 Formulário de advogado detectado, enviando...');
                    
                    // Encontrar o modal pai
                    const modal = target.closest('.modal');
                    if (modal) {
                        const modalId = modal.id;
                        console.log('🔍 Modal ID:', modalId);
                        
                        // Determinar se é edição ou criação
                        if (modalId.includes('editModal_')) {
                            const advogadoId = modalId.replace('editModal_', '');
                            console.log('🔍 Advogado ID para edição:', advogadoId);
                            
                            // Aqui você pode implementar a lógica para advogados
                            console.log('ℹ️ Lógica para advogados em desenvolvimento');
                        } else {
                            console.log('🔍 Modal de criação de advogado detectado');
                            // Aqui você pode implementar a lógica para criação
                            console.log('ℹ️ Lógica para criação de advogados em desenvolvimento');
                        }
                    }
                }
                else {
                    console.log('🔍 Formulário não reconhecido:', form.id);
                }
            } else {
                console.warn('⚠️ Formulário não encontrado para o botão');
            }
        }
    });
    
    console.log('✅ Handlers globais configurados com sucesso');
}



/**
 * Funções auxiliares para informações de login
 */

/**
 * Copiar informações de login para a área de transferência
 */
window.copiarInformacoesLogin = function(username, senha, nome = '') {
    const texto = `Informações de Acesso - ${nome}
Usuário: ${username}
Senha Padrão: ${senha}

IMPORTANTE: Guarde essas informações e altere a senha no primeiro acesso.`;
    
    if (navigator.clipboard && window.isSecureContext) {
        // Usar Clipboard API moderna
        navigator.clipboard.writeText(texto).then(() => {
            showSuccessMessage('Informações copiadas para a área de transferência!');
        }).catch(err => {
            console.error('Erro ao copiar:', err);
            fallbackCopyTextToClipboard(texto);
        });
    } else {
        // Fallback para navegadores mais antigos
        fallbackCopyTextToClipboard(texto);
    }
};

/**
 * Fallback para copiar texto (navegadores antigos)
 */
function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showSuccessMessage('Informações copiadas para a área de transferência!');
        } else {
            showErrorMessage('Erro ao copiar informações. Tente selecionar e copiar manualmente.');
        }
    } catch (err) {
        console.error('Erro ao copiar:', err);
        showErrorMessage('Erro ao copiar informações. Tente selecionar e copiar manualmente.');
    }
    
    document.body.removeChild(textArea);
}

/**
 * Imprimir informações de login
 */
window.imprimirInformacoesLogin = function(username, senha, nome = '') {
    const conteudo = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Informações de Acesso - ${nome}</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
                .info-box { border: 2px solid #333; padding: 20px; margin: 20px 0; background: #f9f9f9; }
                .warning { border: 2px solid #ff6b6b; padding: 15px; margin: 20px 0; background: #fff5f5; }
                .field { margin: 10px 0; }
                .label { font-weight: bold; }
                .value { font-family: monospace; background: #fff; padding: 5px; border: 1px solid #ddd; }
                @media print { body { margin: 0; } }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Informações de Acesso</h1>
                <h2>${nome}</h2>
                <p>Data: ${new Date().toLocaleDateString('pt-BR')}</p>
            </div>
            
            <div class="info-box">
                <h3>Dados de Login:</h3>
                <div class="field">
                    <span class="label">Usuário:</span>
                    <span class="value">${username}</span>
                </div>
                <div class="field">
                    <span class="label">Senha Padrão:</span>
                    <span class="value">${senha}</span>
                </div>
                <div class="field">
                    <span class="label">Tipo de Usuário:</span>
                    <span class="value">Advogado</span>
                </div>
            </div>
            
            <div class="warning">
                <h3>⚠️ IMPORTANTE:</h3>
                <ul>
                    <li>Guarde essas informações em local seguro</li>
                    <li>Altere a senha padrão no primeiro acesso</li>
                    <li>Use o CPF como nome de usuário</li>
                    <li>Não compartilhe essas informações</li>
                </ul>
            </div>
            
            <div style="margin-top: 40px; text-align: center; font-size: 12px; color: #666;">
                <p>Documento gerado automaticamente pelo sistema ABMEPI ASEJUS</p>
            </div>
        </body>
        </html>
    `;
    
    const printWindow = window.open('', '_blank');
    printWindow.document.write(conteudo);
    printWindow.document.close();
    
    // Aguardar o conteúdo carregar e imprimir
    printWindow.onload = function() {
        printWindow.print();
        printWindow.close();
    };
};

// ============================================================================
// FUNÇÃO PARA ABRIR MODAL DE DOCUMENTO
// ============================================================================



/**
 * Configurar funcionalidades do formulário de andamento
 */
function setupAndamentoForm(form) {
    // Templates de andamento
    const templates = {
        contato: {
            titulo: 'Contato com Cliente',
            descricao: 'Realizado contato com o cliente para esclarecimentos sobre o caso.\n\nDetalhes:\n- Forma de contato: \n- Assunto tratado: \n- Próximos passos: '
        },
        documento: {
            titulo: 'Documento Recebido',
            descricao: 'Documento recebido e analisado.\n\nDetalhes:\n- Tipo de documento: \n- Data de recebimento: \n- Conteúdo relevante: \n- Ações necessárias: '
        },
        audiencia: {
            titulo: 'Audiência Realizada',
            descricao: 'Audiência realizada conforme agendamento.\n\nDetalhes:\n- Data e hora: \n- Local: \n- Juiz: \n- Decisões tomadas: \n- Próximas audiências: '
        },
        decisao: {
            titulo: 'Decisão Judicial',
            descricao: 'Decisão judicial recebida e analisada.\n\nDetalhes:\n- Tipo de decisão: \n- Data da decisão: \n- Conteúdo principal: \n- Impacto no caso: \n- Ações necessárias: '
        }
    };

    // Função para usar template
    window.usarTemplate = function(tipo) {
        const template = templates[tipo];
        if (template) {
            const tituloField = form.querySelector('input[name="titulo"]');
            const descricaoField = form.querySelector('textarea[name="descricao"]');
            const tipoAndamentoField = form.querySelector('select[name="tipo_andamento"]');
            
            if (tituloField) tituloField.value = template.titulo;
            if (descricaoField) descricaoField.value = template.descricao;
            if (tipoAndamentoField) tipoAndamentoField.value = tipo;
            
            // Mostrar campos específicos do tipo
            mostrarCamposTipo(tipo);
            
            // Focar no campo de descrição para edição
            if (descricaoField) {
                descricaoField.focus();
                // Posicionar cursor no final
                const len = descricaoField.value.length;
                descricaoField.setSelectionRange(len, len);
            }
        }
    };

    // Função para mostrar/ocultar campos específicos baseado no tipo
    function mostrarCamposTipo(tipo) {
        // Ocultar todos os campos específicos
        const todosCampos = document.querySelectorAll('.campos-tipo');
        todosCampos.forEach(campo => {
            campo.style.display = 'none';
        });
        
        // Mostrar apenas os campos do tipo selecionado
        const camposTipo = document.getElementById(`campos-${tipo}`);
        if (camposTipo) {
            camposTipo.style.display = 'block';
        }
    }

    // Listener para mudança no tipo de andamento
    const tipoAndamentoField = form.querySelector('select[name="tipo_andamento"]');
    if (tipoAndamentoField) {
        tipoAndamentoField.addEventListener('change', function() {
            mostrarCamposTipo(this.value);
        });
        
        // Mostrar campos do tipo inicial se já estiver selecionado
        if (tipoAndamentoField.value) {
            mostrarCamposTipo(tipoAndamentoField.value);
        }
    }

    // Atualizar data e hora em tempo real
    const dataAndamentoSpan = document.getElementById('dataAndamento');
    if (dataAndamentoSpan && !dataAndamentoSpan.textContent.includes('Agora')) {
        const now = new Date();
        const options = {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        dataAndamentoSpan.textContent = now.toLocaleDateString('pt-BR', options);
    }
    
    // Atualizar usuário atual
    const usuarioRegistroSpan = document.getElementById('usuarioRegistro');
    if (usuarioRegistroSpan && usuarioRegistroSpan.textContent.includes('Usuário Atual')) {
        // Manter o texto "Usuário Atual" se não houver usuário específico
        usuarioRegistroSpan.textContent = 'Usuário Atual';
    }
    
    // Validação de campos obrigatórios
    const tituloField = form.querySelector('input[name="titulo"]');
    const descricaoField = form.querySelector('textarea[name="descricao"]');
    
    if (tituloField) {
        tituloField.addEventListener('input', function() {
            if (this.value.trim().length < 5) {
                this.classList.add('is-invalid');
                let feedback = this.parentNode.querySelector('.invalid-feedback');
                if (!feedback) {
                    feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback d-block';
                    feedback.textContent = 'O título deve ter pelo menos 5 caracteres.';
                    this.parentNode.appendChild(feedback);
                }
            } else {
                this.classList.remove('is-invalid');
                const feedback = this.parentNode.querySelector('.invalid-feedback');
                if (feedback) {
                    feedback.remove();
                }
            }
        });
    }
    
    if (descricaoField) {
        descricaoField.addEventListener('input', function() {
            if (this.value.trim().length < 20) {
                this.classList.add('is-invalid');
                let feedback = this.parentNode.querySelector('.invalid-feedback');
                if (!feedback) {
                    feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback d-block';
                    feedback.textContent = 'A descrição deve ter pelo menos 20 caracteres.';
                    this.parentNode.appendChild(feedback);
                }
            } else {
                this.classList.remove('is-invalid');
                const feedback = this.parentNode.querySelector('.invalid-feedback');
                if (feedback) {
                    feedback.remove();
                }
            }
        });
    }
    
    // Auto-completar baseado no atendimento selecionado
    const atendimentoField = form.querySelector('select[name="atendimento"]');
    if (atendimentoField) {
        atendimentoField.addEventListener('change', function() {
            if (this.value) {
                const selectedOption = this.options[this.selectedIndex];
                const atendimentoText = selectedOption.textContent;
                
                // Se o título estiver vazio, sugerir baseado no atendimento
                if (tituloField && !tituloField.value) {
                    if (atendimentoText.includes('Civil')) {
                        tituloField.value = 'Andamento - Processo Civil';
                    } else if (atendimentoText.includes('Trabalhista')) {
                        tituloField.value = 'Andamento - Processo Trabalhista';
                    } else if (atendimentoText.includes('Previdenciário')) {
                        tituloField.value = 'Andamento - Processo Previdenciário';
                    } else {
                        tituloField.value = 'Andamento - Processo';
                    }
                }
            }
        });
    }
}