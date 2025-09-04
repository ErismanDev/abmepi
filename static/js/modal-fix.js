/**
 * CORREÇÃO PARA ERRO DE BACKDROP UNDEFINED
 * Este arquivo resolve o problema de "Cannot read properties of undefined (reading 'backdrop')"
 * que ocorre quando o Bootstrap tenta inicializar modais sem opções válidas
 */

console.log('🔧 Modal Fix JavaScript carregado');

// Polyfill para bootstrap.Modal.getInstance em Bootstrap 5
(function() {
    // Aguardar Bootstrap estar disponível e aplicar polyfill
    const initPolyfill = function() {
        if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined' && !bootstrap.Modal.getInstance) {
            console.log('🔧 Adicionando polyfill para bootstrap.Modal.getInstance no modal-fix.js');
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
            console.log('✅ Polyfill bootstrap.Modal.getInstance aplicado com sucesso no modal-fix.js');
        } else if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined' && bootstrap.Modal.getInstance) {
            console.log('✅ bootstrap.Modal.getInstance já disponível no modal-fix.js');
        } else if (typeof bootstrap === 'undefined') {
            console.warn('⚠️ Bootstrap não encontrado no modal-fix.js, tentando novamente em 100ms...');
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

// Função para interceptar erros específicos do Bootstrap Modal
function interceptBootstrapModalErrors() {
    console.log('🔧 Configurando interceptação de erros específicos do Bootstrap Modal...');
    
    // Interceptar erros específicos da linha 158 do modal.js
    const originalErrorHandler = window.onerror;
    
    window.onerror = function(message, source, lineno, colno, error) {
        // Verificar se é o erro específico do modal.js linha 158
        if (message && message.includes('Cannot read properties of undefined (reading \'backdrop\')') && 
            source && source.includes('modal.js')) {
            
            console.warn('⚠️ Erro específico do Bootstrap Modal interceptado:', message);
            console.warn('📍 Arquivo:', source, 'Linha:', lineno);
            
            // Aplicar correções de emergência
            setTimeout(() => {
                console.log('🔄 Aplicando correções de emergência para erro de backdrop...');
                applyEmergencyModalFixes();
                patchBootstrapModalInternals();
            }, 100);
            
            // Prevenir propagação do erro
            return true;
        }
        
        // Chamar handler original se existir
        if (originalErrorHandler) {
            return originalErrorHandler(message, source, lineno, colno, error);
        }
        
        return false;
    };
    
    console.log('✅ Interceptação de erros específicos configurada');
}

// Função para corrigir internamente o Bootstrap Modal
function patchBootstrapModalInternals() {
    console.log('🔧 Aplicando patch interno ao Bootstrap Modal...');
    
    try {
        if (typeof bootstrap === 'undefined' || typeof bootstrap.Modal === 'undefined') {
            console.warn('⚠️ Bootstrap não disponível para patch interno');
            return;
        }
        
        // Sobrescrever a função _initializeBackDrop se existir
        const ModalPrototype = bootstrap.Modal.prototype;
        
        if (ModalPrototype && typeof ModalPrototype._initializeBackDrop === 'function') {
            const originalBackdropInit = ModalPrototype._initializeBackDrop;
            
            ModalPrototype._initializeBackDrop = function() {
                try {
                    // Garantir que as opções existam e tenham valores válidos
                    if (!this._config) {
                        this._config = {};
                    }
                    
                    // Definir valores padrão seguros
                    const safeConfig = {
                        backdrop: true,
                        keyboard: true,
                        focus: true,
                        show: false,
                        ...this._config
                    };
                    
                    // Atualizar configuração
                    this._config = safeConfig;
                    
                    console.log('🔧 Configuração segura aplicada ao modal:', safeConfig);
                    
                    // Chamar função original com configuração segura
                    return originalBackdropInit.call(this);
                    
                } catch (error) {
                    console.error('❌ Erro no patch de backdrop:', error);
                    
                    // Fallback: tentar inicializar com configuração mínima
                    try {
                        this._config = {
                            backdrop: true,
                            keyboard: true,
                            focus: true,
                            show: false
                        };
                        
                        return originalBackdropInit.call(this);
                    } catch (fallbackError) {
                        console.error('❌ Erro no fallback de backdrop:', fallbackError);
                        return false;
                    }
                }
            };
            
            console.log('✅ Função _initializeBackDrop corrigida');
        }
        
        // Sobrescrever o construtor para garantir configurações seguras
        const OriginalModal = bootstrap.Modal;
        
        bootstrap.Modal = function(element, options) {
            console.log('🔧 Modal sendo criado com patch interno...');
            
            // Garantir que element existe
            if (!element) {
                console.error('❌ Elemento não fornecido para Modal');
                throw new Error('Elemento é obrigatório para criar um Modal');
            }
            
            // Garantir que options existe e tem valores padrão
            if (!options) {
                options = {};
            }
            
            // Definir valores padrão para opções críticas
            const safeOptions = {
                backdrop: true,           // Sempre definir backdrop
                keyboard: true,           // Sempre definir keyboard
                focus: true,              // Sempre definir focus
                show: false,              // Não mostrar automaticamente
                ...options                // Sobrescrever com opções fornecidas
            };
            
            // Log das opções finais
            console.log('🔧 Opções seguras do modal (patch interno):', safeOptions);
            
            try {
                // Criar modal com opções seguras
                const modal = new OriginalModal(element, safeOptions);
                
                // Garantir que a configuração interna seja segura
                if (modal._config) {
                    modal._config = {
                        ...modal._config,
                        backdrop: true,
                        keyboard: true,
                        focus: true
                    };
                }
                
                console.log('✅ Modal criado com sucesso (patch interno)');
                return modal;
            } catch (error) {
                console.error('❌ Erro ao criar modal (patch interno):', error);
                
                // Tentar criar com configurações mínimas
                try {
                    const fallbackModal = new OriginalModal(element, {
                        backdrop: true,
                        keyboard: true,
                        focus: true
                    });
                    
                    // Garantir configuração segura
                    if (fallbackModal._config) {
                        fallbackModal._config = {
                            ...fallbackModal._config,
                            backdrop: true,
                            keyboard: true,
                            focus: true
                        };
                    } else {
                        // Se _config não existir, criar um
                        fallbackModal._config = {
                            backdrop: true,
                            keyboard: true,
                            focus: true
                        };
                    }
                    
                    console.log('✅ Modal criado com fallback (patch interno)');
                    return fallbackModal;
                } catch (fallbackError) {
                    console.error('❌ Erro no fallback (patch interno):', fallbackError);
                    
                    // Último recurso: criar modal básico
                    try {
                        const basicModal = new OriginalModal(element);
                        
                        // Forçar configuração segura
                        if (basicModal._config) {
                            basicModal._config.backdrop = true;
                            basicModal._config.keyboard = true;
                            basicModal._config.focus = true;
                        } else {
                            // Se _config não existir, criar um
                            basicModal._config = {
                                backdrop: true,
                                keyboard: true,
                                focus: true
                            };
                        }
                        
                        console.log('✅ Modal criado com configuração básica (patch interno)');
                        return basicModal;
                    } catch (basicError) {
                        console.error('❌ Erro na configuração básica (patch interno):', basicError);
                        throw basicError;
                    }
                }
            }
        };
        
        // Manter propriedades estáticas do construtor original
        bootstrap.Modal.Constructor = OriginalModal.Constructor;
        bootstrap.Modal.VERSION = OriginalModal.VERSION;
        bootstrap.Modal.Default = OriginalModal.Default;
        
        console.log('✅ Patch interno aplicado com sucesso');
        
    } catch (error) {
        console.error('❌ Erro ao aplicar patch interno:', error);
    }
}

// Função para aplicar correções de emergência
function applyEmergencyModalFixes() {
    console.log('🚨 Aplicando correções de emergência...');
    
    try {
        // Verificar se Bootstrap está disponível
        if (typeof bootstrap === 'undefined' || typeof bootstrap.Modal === 'undefined') {
            console.warn('⚠️ Bootstrap não disponível para correções de emergência');
            return;
        }
        
        // Sobrescrever o construtor do Modal com proteções extras
        const OriginalModal = bootstrap.Modal;
        
        bootstrap.Modal = function(element, options) {
            console.log('🔧 Modal sendo criado com proteções de emergência...');
            
            // Garantir que element existe
            if (!element) {
                console.error('❌ Elemento não fornecido para Modal');
                throw new Error('Elemento é obrigatório para criar um Modal');
            }
            
            // Garantir que options existe e tem valores padrão
            if (!options) {
                options = {};
            }
            
            // Definir valores padrão para opções críticas
            const safeOptions = {
                backdrop: true,           // Sempre definir backdrop
                keyboard: true,           // Sempre definir keyboard
                focus: true,              // Sempre definir focus
                show: false,              // Não mostrar automaticamente
                ...options                // Sobrescrever com opções fornecidas
            };
            
            // Log das opções finais
            console.log('🔧 Opções seguras do modal (emergência):', safeOptions);
            
            try {
                // Criar modal com opções seguras
                const modal = new OriginalModal(element, safeOptions);
                
                // Garantir configuração segura na instância
                if (modal._config) {
                    modal._config = {
                        ...modal._config,
                        backdrop: true,
                        keyboard: true,
                        focus: true
                    };
                }
                
                console.log('✅ Modal criado com sucesso (emergência)');
                return modal;
            } catch (error) {
                console.error('❌ Erro ao criar modal (emergência):', error);
                
                // Tentar criar com configurações mínimas
                try {
                    const fallbackModal = new OriginalModal(element, {
                        backdrop: true,
                        keyboard: true,
                        focus: true
                    });
                    
                    // Garantir configuração segura
                    if (fallbackModal._config) {
                        fallbackModal._config.backdrop = true;
                        fallbackModal._config.keyboard = true;
                        fallbackModal._config.focus = true;
                    }
                    
                    console.log('✅ Modal criado com fallback (emergência)');
                    return fallbackModal;
                } catch (fallbackError) {
                    console.error('❌ Erro no fallback (emergência):', fallbackError);
                    
                    // Último recurso: criar modal básico
                    try {
                        const basicModal = new OriginalModal(element);
                        
                        // Forçar configuração segura
                        if (basicModal._config) {
                            basicModal._config.backdrop = true;
                            basicModal._config.keyboard = true;
                            basicModal._config.focus = true;
                        }
                        
                        console.log('✅ Modal criado com configuração básica (emergência)');
                        return basicModal;
                    } catch (basicError) {
                        console.error('❌ Erro na configuração básica (emergência):', basicError);
                        throw basicError;
                    }
                }
            }
        };
        
        // Manter propriedades estáticas do construtor original
        bootstrap.Modal.Constructor = OriginalModal.Constructor;
        bootstrap.Modal.VERSION = OriginalModal.VERSION;
        bootstrap.Modal.Default = OriginalModal.Default;
        
        // Adicionar método para criar modal seguro
        bootstrap.Modal.createSafe = function(element, options = {}) {
            return new bootstrap.Modal(element, options);
        };
        
        console.log('✅ Construtor do Modal corrigido com proteções de emergência');
        
    } catch (error) {
        console.error('❌ Erro ao aplicar correções de emergência:', error);
    }
}

// Função para aplicar correções de modal
function applyModalFixes() {
    console.log('🔧 Aplicando correções de modal...');
    
    // Verificar se Bootstrap está disponível
    if (typeof bootstrap === 'undefined') {
        console.warn('⚠️ Bootstrap não está disponível');
        return false;
    }
    
    if (typeof bootstrap.Modal === 'undefined') {
        console.warn('⚠️ Bootstrap.Modal não está disponível');
        return false;
    }
    
    console.log('✅ Bootstrap e Modal disponíveis');
    
    // Salvar referência ao construtor original
    const OriginalModal = bootstrap.Modal;
    
    // Sobrescrever o construtor do Modal com proteções
    bootstrap.Modal = function(element, options) {
        console.log('🔧 Modal sendo criado com proteções...');
        
        // Garantir que element existe
        if (!element) {
            console.error('❌ Elemento não fornecido para Modal');
            throw new Error('Elemento é obrigatório para criar um Modal');
        }
        
        // Garantir que options existe e tem valores padrão
        if (!options) {
            options = {};
        }
        
        // Definir valores padrão para opções críticas
        const safeOptions = {
            backdrop: true,           // Sempre definir backdrop
            keyboard: true,           // Sempre definir keyboard
            focus: true,              // Sempre definir focus
            show: false,              // Não mostrar automaticamente
            ...options                // Sobrescrever com opções fornecidas
        };
        
        // Log das opções finais
        console.log('🔧 Opções seguras do modal:', safeOptions);
        
        try {
            // Criar modal com opções seguras
            const modal = new OriginalModal(element, safeOptions);
            
            // Garantir configuração segura na instância
            if (modal._config) {
                modal._config = {
                    ...modal._config,
                    backdrop: true,
                    keyboard: true,
                    focus: true
                };
            }
            
            console.log('✅ Modal criado com sucesso');
            return modal;
        } catch (error) {
            console.error('❌ Erro ao criar modal:', error);
            
            // Tentar criar com configurações mínimas
            try {
                const fallbackModal = new OriginalModal(element, {
                    backdrop: true,
                    keyboard: true,
                    focus: true
                });
                
                // Garantir configuração segura
                if (fallbackModal._config) {
                    fallbackModal._config.backdrop = true;
                    fallbackModal._config.keyboard = true;
                    fallbackModal._config.focus = true;
                }
                
                console.log('✅ Modal criado com fallback');
                return fallbackModal;
            } catch (fallbackError) {
                console.error('❌ Erro no fallback:', fallbackError);
                throw fallbackError;
            }
        }
    };
    
    // Manter propriedades estáticas do construtor original
    bootstrap.Modal.Constructor = OriginalModal.Constructor;
    bootstrap.Modal.VERSION = OriginalModal.VERSION;
    bootstrap.Modal.Default = OriginalModal.Default;
    
    // Adicionar método para criar modal seguro
    bootstrap.Modal.createSafe = function(element, options = {}) {
        return new bootstrap.Modal(element, options);
    };
    
    console.log('✅ Construtor do Modal corrigido com sucesso');
    return true;
}

// Função para corrigir modais existentes
function fixExistingModals() {
    console.log('🔧 Corrigindo modais existentes...');
    
    const modais = document.querySelectorAll('.modal');
    let fixedCount = 0;
    
    modais.forEach(function(modalElement, index) {
        try {
            // Verificar se o modal já foi inicializado
            if (modalElement && !modalElement._bsModal) {
                const modal = new bootstrap.Modal(modalElement, {
                    backdrop: true,
                    keyboard: true,
                    focus: true
                });
                fixedCount++;
                console.log(`✅ Modal ${index + 1} corrigido:`, modalElement.id || 'sem ID');
            }
        } catch (error) {
            console.warn(`⚠️ Erro ao corrigir modal ${index + 1}:`, error);
        }
    });
    
    console.log(`✅ ${fixedCount} modais corrigidos`);
}

// Função para interceptar erros de modal
function setupErrorInterception() {
    console.log('🔧 Configurando interceptação de erros...');
    
    window.addEventListener('error', function(event) {
        // Verificar se é um erro relacionado a modal
        if (event.message && (
            event.message.includes('backdrop') ||
            event.message.includes('modal') ||
            event.message.includes('Modal')
        )) {
            console.warn('⚠️ Erro de modal interceptado:', event.message);
            
            // Prevenir comportamento padrão
            event.preventDefault();
            
            // Aplicar correções se necessário
            if (event.filename && event.filename.includes('modal.js')) {
                console.log('🔄 Aplicando correções de emergência...');
                setTimeout(function() {
                    applyModalFixes();
                    fixExistingModals();
                    patchBootstrapModalInternals();
                }, 100);
            }
        }
        
        // Verificar se é erro de função não definida
        if (event.message && event.message.includes('openAdvogadoEditModal is not defined')) {
            console.warn('⚠️ Erro de openAdvogadoEditModal interceptado:', event.message);
            
            // Prevenir comportamento padrão
            event.preventDefault();
            
            // Tentar preservar as funções de modal
            setTimeout(preserveModalFunctions, 100);
        }
    });
    
    console.log('✅ Interceptação de erros configurada');
}

// Função para garantir que funções de modal não sejam perdidas
function preserveModalFunctions() {
    console.log('🔧 Preservando funções de modal...');
    
    // Garantir que openAdvogadoEditModal não seja perdida
    if (typeof window.openAdvogadoEditModal !== 'function') {
        console.log('⚠️ openAdvogadoEditModal não encontrada, verificando se deve ser restaurada...');
        
        // Aguardar um pouco para outros scripts carregarem
        setTimeout(() => {
            if (typeof window.openAdvogadoEditModal !== 'function') {
                console.warn('❌ openAdvogadoEditModal ainda não disponível após timeout');
                
                // Tentar definir uma função de fallback
                window.openAdvogadoEditModal = function(advogadoId) {
                    console.log('🔧 Função openAdvogadoEditModal de fallback chamada para ID:', advogadoId);
                    
                    // Verificar se a função real foi carregada enquanto isso
                    if (window.openAdvogadoEditModal !== arguments.callee) {
                        console.log('✅ Função real encontrada, redirecionando...');
                        return window.openAdvogadoEditModal(advogadoId);
                    }
                    
                                                   console.warn('⚠️ Função openAdvogadoEditModal não está disponível. Verifique se o arquivo modais_assejus.js foi carregado.');
                               if (typeof showErrorMessage === 'function') {
                                   showErrorMessage('Erro: Função de edição de advogado não está disponível. Recarregue a página e tente novamente.');
                               } else {
                                   console.error('❌ Função de edição de advogado não está disponível');
                               }
                };
                
                console.log('✅ Função de fallback para openAdvogadoEditModal criada');
            }
        }, 1000);
    } else {
        console.log('✅ openAdvogadoEditModal já está disponível');
    }
}

// Função principal de inicialização
function initializeModalFixes() {
    console.log('🚀 Inicializando correções de modal...');
    
    // Configurar interceptação de erros específicos primeiro
    interceptBootstrapModalErrors();
    
    // Aplicar patch interno
    patchBootstrapModalInternals();
    
    // Aplicar correções
    const fixesApplied = applyModalFixes();
    
    if (fixesApplied) {
        // Corrigir modais existentes
        setTimeout(fixExistingModals, 100);
        
        // Configurar interceptação de erros
        setupErrorInterception();
        
        // Preservar funções de modal
        setTimeout(preserveModalFunctions, 500);
        
        console.log('✅ Correções de modal inicializadas com sucesso');
    } else {
        console.warn('⚠️ Não foi possível aplicar correções de modal');
    }
}

// Aguardar o DOM estar carregado
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeModalFixes);
} else {
    // DOM já está carregado
    initializeModalFixes();
}

// Exportar funções para uso global
window.ModalFix = {
    apply: applyModalFixes,
    fixExisting: fixExistingModals,
    initialize: initializeModalFixes,
    createSafe: function(element, options = {}) {
        if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
            return new bootstrap.Modal(element, options);
        }
        return null;
    },
    emergencyFix: applyEmergencyModalFixes,
    patchInternals: patchBootstrapModalInternals
};

console.log('🔧 Modal Fix JavaScript carregado e configurado');

// Registrar no Modal Loader se disponível
if (typeof window.ModalLoader !== 'undefined') {
    window.ModalLoader.register('fix');
}
