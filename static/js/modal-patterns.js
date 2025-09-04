/**
 * PADRÕES DE MODAIS PARA O SISTEMA ABMEPI
 */

console.log('🎯 Modal Patterns JavaScript carregado');

// Polyfill para bootstrap.Modal.getInstance em Bootstrap 5
(function() {
    // Aguardar Bootstrap estar disponível
    const initPolyfill = function() {
        if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined' && !bootstrap.Modal.getInstance) {
            console.log('🔧 Adicionando polyfill para bootstrap.Modal.getInstance no modal-patterns.js');
            bootstrap.Modal.getInstance = function(element) {
                if (!element) return null;
                
                // Verificar se já existe uma instância armazenada
                if (element._bsModal) {
                    return element._bsModal;
                }
                
                // Tentar encontrar instância existente (Bootstrap 5 interno)
                const dataKey = 'bs.modal';
                if (element._element && element._element[dataKey]) {
                    element._bsModal = element._element[dataKey];
                    return element._bsModal;
                }
                
                // Criar nova instância e armazenar
                try {
                    const modal = new bootstrap.Modal(element);
                    element._bsModal = modal;
                    return modal;
                } catch (error) {
                    console.warn('⚠️ Erro ao criar instância do modal no polyfill:', error);
                    return null;
                }
            };
            console.log('✅ Polyfill bootstrap.Modal.getInstance aplicado com sucesso');
        } else if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined' && bootstrap.Modal.getInstance) {
            console.log('✅ bootstrap.Modal.getInstance já disponível');
        } else if (typeof bootstrap === 'undefined') {
            console.warn('⚠️ Bootstrap não encontrado, tentando novamente em 100ms...');
            setTimeout(initPolyfill, 100);
        }
    };
    
    // Tentar inicializar imediatamente
    initPolyfill();
    
    // Fallback: tentar novamente quando DOM estiver pronto
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initPolyfill);
    }
})();

// Função para fechar modal de forma robusta
window.closeModal = function(modalId) {
    console.log('🔒 Tentando fechar modal:', modalId);
    
    try {
        // Tentar fechar usando Bootstrap se disponível
        const modalElement = document.getElementById(modalId);
        console.log('🔍 Modal element para fechar:', modalElement);
        
        if (modalElement) {
            // Verificar se bootstrap.Modal.getInstance existe (Bootstrap 4) ou usar abordagem alternativa (Bootstrap 5)
            if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined' && typeof bootstrap.Modal.getInstance === 'function') {
                // Bootstrap 4 - usar getInstance
                const bsModal = bootstrap.Modal.getInstance(modalElement);
                console.log('🔍 Instância Bootstrap do modal:', bsModal);
                
                if (bsModal) {
                    console.log('🔒 Fechando via Bootstrap 4...');
                    bsModal.hide();
                    console.log('✅ Modal fechado via Bootstrap 4:', modalId);
                    
                    // Verificar se realmente fechou
                    setTimeout(() => {
                        if (modalElement.classList.contains('show') || modalElement.style.display === 'block') {
                            console.log('⚠️ Modal ainda visível após Bootstrap.hide(), tentando fallback...');
                            closeModalFallback(modalId);
                        } else {
                            console.log('✅ Modal realmente fechado via Bootstrap 4');
                        }
                    }, 100);
                    
                    return;
                } else {
                    console.log('⚠️ Instância Bootstrap não encontrada, usando fallback');
                }
            } else if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined') {
                // Bootstrap 5 - tentar usar hide() diretamente se disponível
                try {
                    if (modalElement._bsModal) {
                        console.log('🔒 Fechando via Bootstrap 5 (instância armazenada)...');
                        modalElement._bsModal.hide();
                        console.log('✅ Modal fechado via Bootstrap 5:', modalId);
                        return;
                    }
                } catch (bsError) {
                    console.log('⚠️ Erro ao usar instância Bootstrap 5, usando fallback:', bsError);
                }
            } else {
                console.log('⚠️ Bootstrap não disponível, usando fallback');
            }
        } else {
            console.log('⚠️ Elemento do modal não encontrado para fechar');
        }
        
        // Fallback: fechar manualmente
        window.closeModalFallback(modalId);
        
    } catch (error) {
        console.error('❌ Erro ao fechar modal:', error);
        window.closeModalFallback(modalId);
    }
}

// Função de fallback para fechar modal
window.closeModalFallback = function(modalId) {
    console.log('🔄 Usando fallback para fechar modal:', modalId);
    
    try {
        const allModals = document.querySelectorAll('.modal');
        console.log('🔍 Modais encontrados:', allModals.length);
        
        allModals.forEach((modal, index) => {
            console.log(`🔍 Modal ${index}:`, {
                id: modal.id,
                visible: modal.style.display === 'block' || modal.classList.contains('show'),
                classes: modal.className
            });
            
            if (modal.style.display === 'block' || modal.classList.contains('show')) {
                console.log(`🔒 Fechando modal ${modal.id || index}...`);
                
                modal.style.display = 'none';
                modal.classList.remove('show');
                modal.classList.remove('fade');
                modal.setAttribute('aria-hidden', 'true');
                modal.removeAttribute('aria-modal');
                modal.removeAttribute('role');
                
                // Remover backdrop
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    backdrop.remove();
                    console.log('✅ Backdrop removido');
                }
                
                // Remover classe modal-open do body
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
                
                console.log('✅ Modal fechado manualmente:', modal.id || 'sem id');
            }
        });
        
    } catch (error) {
        console.error('❌ Erro no fallback de fechar modal:', error);
        
        // Último recurso: remover todos os modais
        const allModals = document.querySelectorAll('.modal');
        allModals.forEach(modal => modal.remove());
        console.log('🔄 Todos os modais removidos como último recurso');
    }
}

// Função principal para abrir modais de formulário
window.openFormModal = function(titulo, conteudo, formId, actionUrl) {
    console.log('🚀 openFormModal chamada:', { titulo, formId, actionUrl });
    
    try {
        if (typeof bootstrap === 'undefined' || typeof bootstrap.Modal === 'undefined') {
            console.error('❌ Bootstrap não disponível, usando fallback');
            createFallbackModal(titulo, conteudo, formId, actionUrl);
            return;
        }

        if (!titulo || !conteudo || !formId) {
            console.error('❌ Parâmetros obrigatórios não fornecidos:', { titulo, conteudo, formId });
            return;
        }

        // Remover modal existente se houver
        const existingModal = document.getElementById('formModal');
        if (existingModal) {
            // Verificar se bootstrap.Modal.getInstance existe (Bootstrap 4) ou usar abordagem alternativa (Bootstrap 5)
            if (typeof bootstrap.Modal.getInstance === 'function') {
                const bsModal = bootstrap.Modal.getInstance(existingModal);
                if (bsModal) {
                    bsModal.dispose();
                }
            } else if (existingModal._bsModal) {
                // Bootstrap 5 - usar instância armazenada
                try {
                    existingModal._bsModal.dispose();
                } catch (error) {
                    console.warn('⚠️ Erro ao dispor modal Bootstrap 5:', error);
                }
            }
            existingModal.remove();
        }

        // Criar estrutura do modal
        const modalHtml = `
            <div class="modal fade" id="formModal" tabindex="-1" aria-labelledby="formModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="formModalLabel">${titulo}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            ${conteudo}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="submit" class="btn btn-primary" id="modalSubmitBtn">Salvar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        console.log('🔧 Criando modal com HTML:', modalHtml);

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Aguardar um momento para o DOM ser atualizado
        setTimeout(() => {
            console.log('🔍 Configurando formulário após 50ms...');
            
            // Configurar formulário
            const form = document.getElementById(formId);
            console.log('🔍 Formulário encontrado:', form);
            
            if (form && actionUrl) {
                form.action = actionUrl;
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    console.log('📝 Submit do formulário interceptado');
                    handleFormSubmit(form, actionUrl);
                });
                
                // Configurar botão do modal para submeter o formulário
                const modalSubmitBtn = document.getElementById('modalSubmitBtn');
                console.log('🔍 Botão modalSubmitBtn encontrado:', modalSubmitBtn);
                
                if (modalSubmitBtn) {
                    modalSubmitBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        console.log('📝 Clique no botão modalSubmitBtn interceptado');
                        handleFormSubmit(form, actionUrl);
                    });
                    console.log('✅ Botão do modal configurado para submeter formulário');
                } else {
                    // Tentar configurar botão que usa form attribute
                    const formSubmitBtn = document.querySelector(`button[type="submit"][form="${formId}"]`);
                    console.log('🔍 Botão com form attribute encontrado:', formSubmitBtn);
                    
                    if (formSubmitBtn) {
                        formSubmitBtn.addEventListener('click', function(e) {
                            e.preventDefault();
                            console.log('📝 Clique no botão com form attribute interceptado');
                            handleFormSubmit(form, actionUrl);
                        });
                        console.log('✅ Botão com form attribute configurado para submeter formulário');
                    } else {
                        console.warn('⚠️ Nenhum botão de submit encontrado no modal');
                        
                        // Debug: listar todos os botões no modal
                        const modal = document.getElementById('formModal');
                        if (modal) {
                            const allButtons = modal.querySelectorAll('button');
                            console.log('🔍 Todos os botões no modal:', allButtons);
                            allButtons.forEach((btn, index) => {
                                console.log(`Botão ${index}:`, {
                                    type: btn.type,
                                    id: btn.id,
                                    form: btn.getAttribute('form'),
                                    text: btn.textContent.trim()
                                });
                            });
                        }
                    }
                }
                
                console.log('✅ Formulário configurado:', formId);
            } else {
                console.warn('⚠️ Formulário não encontrado ou actionUrl não fornecido:', { formId, actionUrl, form: !!form });
                
                setTimeout(() => {
                    console.log('🔍 Segunda tentativa após 100ms...');
                    const retryForm = document.getElementById(formId);
                    if (retryForm && actionUrl) {
                        retryForm.action = actionUrl;
                        retryForm.addEventListener('submit', function(e) {
                            e.preventDefault();
                            console.log('📝 Submit do formulário interceptado na segunda tentativa');
                            handleFormSubmit(retryForm, actionUrl);
                        });
                        
                        // Configurar botão do modal na segunda tentativa
                        const modalSubmitBtn = document.getElementById('modalSubmitBtn');
                        if (modalSubmitBtn) {
                            modalSubmitBtn.addEventListener('click', function(e) {
                                e.preventDefault();
                                console.log('📝 Clique no botão modalSubmitBtn interceptado na segunda tentativa');
                                handleFormSubmit(retryForm, actionUrl);
                            });
                            console.log('✅ Botão do modal configurado na segunda tentativa');
                        } else {
                            // Tentar configurar botão que usa form attribute na segunda tentativa
                            const formSubmitBtn = document.querySelector(`button[type="submit"][form="${formId}"]`);
                            if (formSubmitBtn) {
                                formSubmitBtn.addEventListener('click', function(e) {
                                    e.preventDefault();
                                    console.log('📝 Clique no botão com form attribute interceptado na segunda tentativa');
                                    handleFormSubmit(retryForm, actionUrl);
                                });
                                console.log('✅ Botão com form attribute configurado na segunda tentativa');
                            } else {
                                console.warn('⚠️ Nenhum botão de submit encontrado na segunda tentativa');
                            }
                        }
                        
                        console.log('✅ Formulário configurado na segunda tentativa:', formId);
                    } else {
                        console.error('❌ Formulário ainda não encontrado após retry:', formId);
                    }
                }, 100);
            }
        }, 100); // Aumentar para 100ms para dar mais tempo ao DOM

        // Mostrar modal
        const modalElement = document.getElementById('formModal');
        console.log('🔍 Modal element encontrado:', modalElement);
        
        if (modalElement) {
            // Debug: verificar se o botão está no modal
            const modalSubmitBtn = modalElement.querySelector('#modalSubmitBtn');
            console.log('🔍 Botão modalSubmitBtn no modal:', modalSubmitBtn);
            
            try {
                const modal = new bootstrap.Modal(modalElement, {
                    backdrop: true,
                    keyboard: true,
                    focus: true
                });

                modal.show();
                console.log('✅ Modal criado e exibido com sucesso');
                
                // Debug: verificar novamente após mostrar
                setTimeout(() => {
                    const btnAfterShow = document.getElementById('modalSubmitBtn');
                    console.log('🔍 Botão modalSubmitBtn após mostrar modal:', btnAfterShow);
                }, 200);
                
            } catch (modalError) {
                console.error('❌ Erro ao criar modal Bootstrap:', modalError);
                modalElement.style.display = 'block';
                modalElement.classList.add('show');
                console.log('✅ Modal exibido diretamente (fallback)');
            }
        } else {
            console.error('❌ Elemento do modal não encontrado');
        }

    } catch (error) {
        console.error('❌ Erro ao criar modal:', error);
        createFallbackModal(titulo, conteudo, formId, actionUrl);
    }
};

// Função para lidar com o submit do formulário
function handleFormSubmit(form, actionUrl) {
    console.log('🚀 handleFormSubmit chamado para:', actionUrl);
    console.log('🔍 Formulário:', form);
    console.log('🔍 ID do formulário:', form.id);
    
    const formData = new FormData(form);
    
    // Procurar botão de submit no modal (padrão modal-patterns.js)
    let submitBtn = document.getElementById('modalSubmitBtn');
    console.log('🔍 Botão modalSubmitBtn encontrado:', submitBtn);
    
    if (!submitBtn) {
        // Procurar botão de submit que usa form attribute (padrão base.html)
        submitBtn = document.querySelector(`button[type="submit"][form="${form.id}"]`);
        console.log('🔍 Procurando botão com form attribute:', submitBtn);
    }
    
    if (!submitBtn) {
        // Fallback: procurar botão de submit no formulário
        submitBtn = form.querySelector('button[type="submit"]');
        console.log('🔍 Procurando botão no formulário:', submitBtn);
    }
    
    if (!submitBtn) {
        console.warn('⚠️ Botão de submit não encontrado no modal nem no formulário');
        
        // Debug: listar todos os botões na página
        const allButtons = document.querySelectorAll('button');
        console.log('🔍 Todos os botões na página:', allButtons.length);
        allButtons.forEach((btn, index) => {
            if (index < 10) { // Limitar a 10 para não poluir o console
                console.log(`Botão ${index}:`, {
                    type: btn.type,
                    id: btn.id,
                    form: btn.getAttribute('form'),
                    text: btn.textContent.trim(),
                    visible: btn.offsetParent !== null
                });
            }
        });
        
        handleFormSubmitWithoutButton(form, actionUrl);
        return;
    }
    
    const originalText = submitBtn.innerHTML || 'Salvar';
    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...';
    submitBtn.disabled = true;

    console.log('📤 Enviando formulário para:', actionUrl);
    console.log('📤 Dados do formulário:', Object.fromEntries(formData));
    console.log('📤 Token CSRF:', getCSRFToken());
    
    fetch(actionUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => {
        console.log('📥 Resposta recebida:', response);
        console.log('📥 Status:', response.status);
        console.log('📥 Headers:', response.headers);
        return response.json();
    })
    .then(data => {
        console.log('📥 Dados da resposta:', data);
        
        if (data.success) {
            console.log('✅ Sucesso! Fechando modal...');
            if (typeof showSuccessMessage === 'function') {
                showSuccessMessage(data.message || 'Operação realizada com sucesso!');
            } else {
                showAlert('success', data.message || 'Operação realizada com sucesso!');
            }
            
            // Fechar modal de forma mais robusta
            window.closeModal('formModal');
            
            if (data.reload) {
                console.log('🔄 Recarregando página em 1 segundo...');
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
        } else {
            console.log('❌ Erro na operação:', data.message);
            if (typeof showErrorMessage === 'function') {
                showErrorMessage(data.message || 'Erro na operação');
            } else {
                showAlert('danger', data.message || 'Erro na operação');
            }
            displayFormErrors(data.errors);
        }
    })
    .catch(error => {
        console.error('❌ Erro no submit:', error);
        if (typeof showErrorMessage === 'function') {
            showErrorMessage('Erro ao processar formulário. Tente novamente.');
        } else {
            showAlert('danger', 'Erro ao processar formulário. Tente novamente.');
        }
    })
    .finally(() => {
        if (submitBtn) {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    });
}

// Função para lidar com submit quando não há botão
function handleFormSubmitWithoutButton(form, actionUrl) {
    console.log('📝 Processando submit sem botão para:', actionUrl);
    
    // Tentar encontrar o botão no modal mesmo assim (múltiplos padrões)
    let submitBtn = document.getElementById('modalSubmitBtn') || 
                   document.getElementById('fallbackSubmitBtn') ||
                   document.querySelector(`button[type="submit"][form="${form.id}"]`);
                   
    if (submitBtn) {
        console.log('✅ Botão encontrado no modal, usando ele');
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...';
        submitBtn.disabled = true;
    } else {
        console.log('ℹ️ Nenhum botão de submit encontrado, processando diretamente');
    }
    
    fetch(actionUrl, {
        method: 'POST',
        body: new FormData(form),
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (typeof showSuccessMessage === 'function') {
                showSuccessMessage(data.message || 'Operação realizada com sucesso!');
            } else {
                showAlert('success', data.message || 'Operação realizada com sucesso!');
            }
            
            // Fechar modal de forma mais robusta
            window.closeModal('formModal');
            
            if (data.reload) {
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
        } else {
            if (typeof showErrorMessage === 'function') {
                showErrorMessage(data.message || 'Erro na operação');
            } else {
                showAlert('danger', data.message || 'Erro na operação');
            }
            displayFormErrors(data.errors);
        }
    })
    .catch(error => {
        console.error('❌ Erro no submit sem botão:', error);
        if (typeof showErrorMessage === 'function') {
            showErrorMessage('Erro ao processar formulário. Tente novamente.');
        } else {
            showAlert('danger', 'Erro ao processar formulário. Tente novamente.');
        }
    })
    .finally(() => {
        // Restaurar botão se existir
        const submitBtn = document.getElementById('modalSubmitBtn') || document.getElementById('fallbackSubmitBtn');
        if (submitBtn) {
            submitBtn.innerHTML = 'Salvar';
            submitBtn.disabled = false;
        }
    });
}

// Função para exibir erros de validação
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
    
    // Exibir resumo dos erros no topo do modal
    const modalBody = document.querySelector('.modal-body');
    if (modalBody) {
        // Remover resumo anterior se existir
        const existingSummary = modalBody.querySelector('.validation-summary');
        if (existingSummary) {
            existingSummary.remove();
        }
        
        // Criar resumo dos erros
        const errorSummary = document.createElement('div');
        errorSummary.className = 'alert alert-danger validation-summary mb-3';
        errorSummary.innerHTML = `
            <h6><i class="fas fa-exclamation-triangle"></i> Erros de Validação:</h6>
            <ul class="mb-0">
                ${Object.entries(errors).map(([field, messages]) => 
                    `<li><strong>${field}:</strong> ${Array.isArray(messages) ? messages.join(', ') : messages}</li>`
                ).join('')}
            </ul>
        `;
        
        modalBody.insertBefore(errorSummary, modalBody.firstChild);
    }
    
    // Marcar campos com erro
    Object.keys(errors).forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            console.log(`🔍 Marcando campo ${fieldName} como inválido`);
            field.classList.add('is-invalid');
            
            // Remover feedback anterior se existir
            const existingFeedback = field.parentNode.querySelector('.invalid-feedback');
            if (existingFeedback) {
                existingFeedback.remove();
            }
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = Array.isArray(errors[fieldName]) ? errors[fieldName].join(', ') : errors[fieldName];
            
            field.parentNode.appendChild(errorDiv);
        } else {
            console.warn(`⚠️ Campo ${fieldName} não encontrado no DOM`);
        }
    });
    
    // Scroll para o primeiro erro
    const firstError = document.querySelector('.is-invalid');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstError.focus();
    }
}

// Função para obter token CSRF
function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
}

// Função para mostrar alertas
function showAlert(type, message) {
    console.log(`📢 Mostrando alerta ${type}:`, message);
    
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
    
    const container = document.querySelector('.main-content') || document.body;
    console.log('🔍 Container para alerta:', container);
    
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
        console.log('✅ Alerta inserido no container');
        
        // Verificar se o alerta foi inserido
        const alert = container.querySelector('.alert');
        if (alert) {
            console.log('✅ Alerta encontrado após inserção');
        } else {
            console.warn('⚠️ Alerta não encontrado após inserção');
        }
        
        setTimeout(() => {
            const alertToRemove = container.querySelector('.alert');
            if (alertToRemove) {
                alertToRemove.remove();
                console.log('✅ Alerta removido após 5 segundos');
            }
        }, 5000);
    } else {
        console.error('❌ Container para alerta não encontrado');
    }
}

// Função de fallback para criar modal básico
window.createFallbackModal = function(titulo, conteudo, formId, actionUrl) {
    console.log('🔄 Criando modal de fallback para:', titulo);
    
    try {
        if (!titulo || !conteudo || !formId) {
            console.error('❌ Parâmetros obrigatórios não fornecidos para fallback:', { titulo, conteudo, formId });
            return;
        }
        
        const modalHtml = `
            <div class="modal fade" id="fallbackModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${titulo}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            ${conteudo}
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                            <button type="submit" class="btn btn-primary" id="fallbackSubmitBtn">Salvar</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        const form = document.getElementById(formId);
        if (form && actionUrl) {
            form.action = actionUrl;
            form.addEventListener('submit', function(e) {
                e.preventDefault();
                handleFormSubmit(form, actionUrl);
            });
            
            // Configurar botão do modal de fallback
            const fallbackSubmitBtn = document.getElementById('fallbackSubmitBtn');
            if (fallbackSubmitBtn) {
                fallbackSubmitBtn.addEventListener('click', function(e) {
                    e.preventDefault();
                    handleFormSubmit(form, actionUrl);
                });
                console.log('✅ Botão do modal de fallback configurado');
            }
            
            console.log('✅ Formulário configurado no fallback:', formId);
        } else {
            console.warn('⚠️ Formulário não encontrado no fallback:', { formId, actionUrl, form: !!form });
            
            setTimeout(() => {
                const retryForm = document.getElementById(formId);
                if (retryForm && actionUrl) {
                    retryForm.action = actionUrl;
                    retryForm.addEventListener('submit', function(e) {
                        e.preventDefault();
                        handleFormSubmit(retryForm, actionUrl);
                    });
                    
                    // Configurar botão do modal de fallback na segunda tentativa
                    const fallbackSubmitBtn = document.getElementById('fallbackSubmitBtn');
                    if (fallbackSubmitBtn) {
                        fallbackSubmitBtn.addEventListener('click', function(e) {
                            e.preventDefault();
                            handleFormSubmit(retryForm, actionUrl);
                        });
                        console.log('✅ Botão do modal de fallback configurado na segunda tentativa');
                    }
                    
                    console.log('✅ Formulário configurado no fallback na segunda tentativa:', formId);
                } else {
                    console.error('❌ Formulário ainda não encontrado no fallback após retry:', formId);
                }
            }, 100);
        }
        
        const modalElement = document.getElementById('fallbackModal');
        if (modalElement) {
            try {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
                console.log('✅ Modal de fallback criado com sucesso');
            } catch (modalError) {
                console.error('❌ Erro ao criar modal Bootstrap de fallback:', modalError);
                modalElement.style.display = 'block';
                modalElement.classList.add('show');
                console.log('✅ Modal de fallback exibido diretamente');
            }
        } else {
            console.error('❌ Elemento do modal de fallback não encontrado');
        }
        
    } catch (error) {
        console.error('❌ Erro ao criar modal de fallback:', error);
    }
};

// Função para verificar se Bootstrap está disponível
window.checkBootstrapAvailability = function() {
    const bootstrapAvailable = typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined';
    console.log('Bootstrap disponível:', bootstrapAvailable ? 'object' : 'undefined');
    return bootstrapAvailable;
};

// Verificar disponibilidade ao carregar
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 Verificando sistema de modais...');
    window.checkBootstrapAvailability();
    
    const functions = ['openFormModal', 'createFallbackModal'];
    functions.forEach(funcName => {
        if (typeof window[funcName] === 'function') {
            console.log(`✅ ${funcName} disponível`);
        } else {
            console.error(`❌ ${funcName} não disponível`);
        }
    });
    
    const existingModals = document.querySelectorAll('.modal');
    if (existingModals.length > 0) {
        console.log(`📋 Encontrados ${existingModals.length} modais existentes na página`);
    }
});

window.addEventListener('load', function() {
    console.log('🚀 Página completamente carregada, verificando sistema de modais...');
    window.checkBootstrapAvailability();
});

console.log('🎯 Modal Patterns JavaScript configurado e pronto');

// Registrar no Modal Loader se disponível
if (typeof window.ModalLoader !== 'undefined') {
    window.ModalLoader.register('patterns');
}
