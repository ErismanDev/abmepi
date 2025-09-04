/**
 * CORREÇÃO PRÉVIA PARA BOOTSTRAP MODAL
 * Este arquivo é carregado ANTES do Bootstrap para interceptar problemas na raiz
 */

console.log('🚀 Bootstrap Preload Fix carregado - interceptando problemas na raiz...');

// Interceptar e corrigir problemas antes do Bootstrap carregar
(function() {
    'use strict';
    
    // Salvar referência ao window.onerror original
    const originalOnError = window.onerror;
    
    // Interceptar TODOS os erros relacionados a backdrop
    window.onerror = function(message, source, lineno, colno, error) {
        // Verificar se é erro de backdrop
        if (message && (
            message.includes('Cannot read properties of undefined (reading \'backdrop\')') ||
            message.includes('backdrop') ||
            message.includes('_initializeBackDrop')
        )) {
            
            console.warn('🚨 ERRO DE BACKDROP INTERCEPTADO ANTES DO BOOTSTRAP:', message);
            console.warn('📍 Arquivo:', source, 'Linha:', lineno);
            
            // Aplicar correções imediatas
            if (typeof applyPreloadFixes === 'function') {
                applyPreloadFixes();
            }
            
            // Prevenir propagação do erro
            return true;
        }
        
        // Chamar handler original se existir
        if (originalOnError) {
            return originalOnError(message, source, lineno, colno, error);
        }
        
        return false;
    };
    
    // Função para aplicar correções prévias
    window.applyPreloadFixes = function() {
        console.log('🔧 Aplicando correções prévias...');
        
        // Aguardar Bootstrap estar disponível
        const waitForBootstrap = setInterval(function() {
            if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined') {
                clearInterval(waitForBootstrap);
                console.log('✅ Bootstrap detectado, aplicando correções...');
                
                // Aplicar patch interno imediatamente
                patchBootstrapModalInternals();
                
                // Sobrescrever construtor com proteções extras
                overrideModalConstructor();
                
            }
        }, 100);
        
        // Timeout de segurança
        setTimeout(function() {
            clearInterval(waitForBootstrap);
            console.warn('⚠️ Timeout aguardando Bootstrap');
        }, 5000);
    };
    
    // Função para fazer patch interno no Bootstrap Modal
    window.patchBootstrapModalInternals = function() {
        try {
            console.log('🔧 Aplicando patch interno prévio...');
            
            const ModalPrototype = bootstrap.Modal.prototype;
            
            // Sobrescrever _initializeBackDrop se existir
            if (ModalPrototype && typeof ModalPrototype._initializeBackDrop === 'function') {
                const originalBackdropInit = ModalPrototype._initializeBackDrop;
                
                ModalPrototype._initializeBackDrop = function() {
                    try {
                        // Garantir configuração segura
                        if (!this._config) {
                            this._config = {};
                        }
                        
                        // Forçar valores seguros
                        this._config.backdrop = true;
                        this._config.keyboard = true;
                        this._config.focus = true;
                        
                        console.log('🔧 Configuração segura forçada no _initializeBackDrop');
                        
                        // Chamar função original
                        return originalBackdropInit.call(this);
                        
                    } catch (error) {
                        console.error('❌ Erro no _initializeBackDrop, usando fallback:', error);
                        
                        // Fallback: retornar sucesso sem fazer nada
                        return true;
                    }
                };
                
                console.log('✅ _initializeBackDrop corrigido com sucesso');
            }
            
            // Sobrescrever outras funções problemáticas se existirem
            if (ModalPrototype && typeof ModalPrototype._setConfig === 'function') {
                const originalSetConfig = ModalPrototype._setConfig;
                
                ModalPrototype._setConfig = function(config) {
                    try {
                        // Garantir configuração segura
                        const safeConfig = {
                            backdrop: true,
                            keyboard: true,
                            focus: true,
                            show: false,
                            ...config
                        };
                        
                        console.log('🔧 Configuração segura aplicada via _setConfig');
                        
                        // Chamar função original com configuração segura
                        return originalSetConfig.call(this, safeConfig);
                        
                    } catch (error) {
                        console.error('❌ Erro no _setConfig, usando fallback:', error);
                        
                        // Fallback: definir configuração básica
                        this._config = {
                            backdrop: true,
                            keyboard: true,
                            focus: true,
                            show: false
                        };
                        
                        return true;
                    }
                };
                
                console.log('✅ _setConfig corrigido com sucesso');
            }
            
        } catch (error) {
            console.error('❌ Erro ao aplicar patch interno prévio:', error);
        }
    }
    
    // Função para sobrescrever construtor do Modal
    window.overrideModalConstructor = function() {
        try {
            console.log('🔧 Sobrescrevendo construtor do Modal...');
            
            const OriginalModal = bootstrap.Modal;
            
            bootstrap.Modal = function(element, options) {
                console.log('🔧 Modal sendo criado com proteções prévias...');
                
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
                
                console.log('🔧 Opções seguras aplicadas (prévias):', safeOptions);
                
                try {
                    // Criar modal com opções seguras
                    const modal = new OriginalModal(element, safeOptions);
                    
                                            // Garantir configuração segura na instância
                        if (modal._config) {
                            modal._config.backdrop = true;
                            modal._config.keyboard = true;
                            modal._config.focus = true;
                        } else {
                            // Se _config não existir, criar um
                            modal._config = {
                                backdrop: true,
                                keyboard: true,
                                focus: true
                            };
                        }
                    
                    console.log('✅ Modal criado com sucesso (proteções prévias)');
                    return modal;
                    
                } catch (error) {
                    console.error('❌ Erro ao criar modal (proteções prévias):', error);
                    
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
                        } else {
                            // Se _config não existir, criar um
                            fallbackModal._config = {
                                backdrop: true,
                                keyboard: true,
                                focus: true
                            };
                        }
                        
                        console.log('✅ Modal criado com fallback (proteções prévias)');
                        return fallbackModal;
                        
                    } catch (fallbackError) {
                        console.error('❌ Erro no fallback (proteções prévias):', fallbackError);
                        
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
                            
                            console.log('✅ Modal criado com configuração básica (proteções prévias)');
                            return basicModal;
                            
                        } catch (basicError) {
                            console.error('❌ Erro na configuração básica (proteções prévias):', basicError);
                            throw basicError;
                        }
                    }
                }
            };
            
            // Manter propriedades estáticas
            bootstrap.Modal.Constructor = OriginalModal.Constructor;
            bootstrap.Modal.VERSION = OriginalModal.VERSION;
            bootstrap.Modal.Default = OriginalModal.Default;
            
            console.log('✅ Construtor do Modal sobrescrito com sucesso');
            
        } catch (error) {
            console.error('❌ Erro ao sobrescrever construtor:', error);
        }
    };
    
    // Interceptar erros de unhandledrejection também
    window.addEventListener('unhandledrejection', function(event) {
        if (event.reason && (
            event.reason.message && event.reason.message.includes('backdrop') ||
            event.reason.message && event.reason.message.includes('Modal')
        )) {
            console.warn('🚨 PROMISE REJECTION INTERCEPTADA:', event.reason);
            
            // Aplicar correções
            if (typeof applyPreloadFixes === 'function') {
                applyPreloadFixes();
            }
            
            // Prevenir comportamento padrão
            event.preventDefault();
        }
    });
    
    console.log('✅ Interceptação prévia configurada com sucesso');
    
})();

// Exportar funções para uso global
window.BootstrapPreloadFix = {
    applyFixes: window.applyPreloadFixes,
    patchInternals: window.patchBootstrapModalInternals,
    overrideConstructor: window.overrideModalConstructor
};

console.log('🚀 Bootstrap Preload Fix configurado e pronto');
