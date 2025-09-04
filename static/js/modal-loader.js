/**
 * MODAL LOADER - Gerenciador de carregamento de modais
 * Este arquivo garante que os modais sejam carregados na ordem correta e resolve dependências
 */

console.log('📂 Modal Loader carregado');

// Objeto para rastrear o estado dos modais
window.ModalLoader = {
    loaded: {
        bootstrap: false,
        patterns: false,
        fix: false,
        assejus: false,
        associados: false,
        psicologia: false
    },
    functions: {},
    
    // Registrar que um módulo foi carregado
    register: function(module) {
        console.log('📝 Registrando módulo:', module);
        this.loaded[module] = true;
        this.checkDependencies();
    },
    
    // Verificar se todas as dependências foram carregadas
    checkDependencies: function() {
        console.log('🔍 Verificando dependências dos modais...');
        console.log('📊 Status dos módulos:', this.loaded);
        
        // Se todos os módulos principais estão carregados
        if (this.loaded.bootstrap && this.loaded.patterns && this.loaded.fix) {
            console.log('✅ Módulos principais carregados, inicializando sistema...');
            this.initializeModalSystem();
        }
    },
    
    // Inicializar sistema de modais
    initializeModalSystem: function() {
        console.log('🚀 Inicializando sistema de modais...');
        
        try {
            // Verificar se as funções principais estão disponíveis
            const requiredFunctions = [
                'openFormModal',
                'createFallbackModal',
                'closeModal'
            ];
            
            requiredFunctions.forEach(funcName => {
                if (typeof window[funcName] === 'function') {
                    console.log(`✅ ${funcName} disponível`);
                } else {
                    console.warn(`⚠️ ${funcName} não disponível`);
                }
            });
            
            // Verificar se openAdvogadoEditModal está disponível
            this.ensureAdvogadoFunctions();
            
            console.log('✅ Sistema de modais inicializado');
            
        } catch (error) {
            console.error('❌ Erro ao inicializar sistema de modais:', error);
        }
    },
    
    // Garantir que as funções de advogado estejam disponíveis
    ensureAdvogadoFunctions: function() {
        console.log('🔍 Verificando funções de advogado...');
        
        const advogadoFunctions = [
            'openAdvogadoEditModal',
            'openAdvogadoDetailModal',
            'openAdvogadoModal'
        ];
        
        advogadoFunctions.forEach(funcName => {
            if (typeof window[funcName] === 'function') {
                console.log(`✅ ${funcName} disponível`);
            } else {
                console.warn(`⚠️ ${funcName} não disponível`);
                
                // Criar função de fallback
                this.createFallbackFunction(funcName);
            }
        });
    },
    
    // Criar função de fallback
    createFallbackFunction: function(funcName) {
        console.log('🔧 Criando função de fallback para:', funcName);
        
        if (funcName === 'openAdvogadoEditModal') {
            window.openAdvogadoEditModal = function(advogadoId) {
                console.log('🔧 Fallback openAdvogadoEditModal chamada para ID:', advogadoId);
                
                // Tentar carregar a função real novamente
                if (typeof window.openAdvogadoEditModal !== arguments.callee) {
                    console.log('✅ Função real encontrada, redirecionando...');
                    return window.openAdvogadoEditModal(advogadoId);
                }
                
                // Se ainda não encontrou, mostrar erro informativo
                console.error('❌ Função openAdvogadoEditModal não encontrada');
                if (typeof showErrorMessage === 'function') {
                    showErrorMessage('Erro: Função de edição não está disponível. Por favor, recarregue a página.');
                } else {
                    console.error('❌ Função de edição não está disponível');
                }
            };
        } else if (funcName === 'openAdvogadoDetailModal') {
            window.openAdvogadoDetailModal = function(advogadoId) {
                console.log('🔧 Fallback openAdvogadoDetailModal chamada para ID:', advogadoId);
                console.error('❌ Função openAdvogadoDetailModal não encontrada');
                if (typeof showErrorMessage === 'function') {
                    showErrorMessage('Erro: Função de detalhes não está disponível. Por favor, recarregue a página.');
                } else {
                    console.error('❌ Função de detalhes não está disponível');
                }
            };
        } else if (funcName === 'openAdvogadoModal') {
            window.openAdvogadoModal = function() {
                console.log('🔧 Fallback openAdvogadoModal chamada');
                console.error('❌ Função openAdvogadoModal não encontrada');
                if (typeof showErrorMessage === 'function') {
                    showErrorMessage('Erro: Função de criação não está disponível. Por favor, recarregue a página.');
                } else {
                    console.error('❌ Função de criação não está disponível');
                }
            };
        }
        
        console.log(`✅ Função de fallback criada para ${funcName}`);
    },
    
    // Função para debug
    debug: function() {
        console.log('🐛 DEBUG Modal Loader:');
        console.log('📊 Módulos carregados:', this.loaded);
        console.log('🔧 Funções disponíveis:', {
            openFormModal: typeof window.openFormModal,
            createFallbackModal: typeof window.createFallbackModal,
            closeModal: typeof window.closeModal,
            openAdvogadoEditModal: typeof window.openAdvogadoEditModal,
            openAdvogadoDetailModal: typeof window.openAdvogadoDetailModal,
            openAdvogadoModal: typeof window.openAdvogadoModal
        });
    }
};

// Verificar se Bootstrap já está disponível
if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined') {
    console.log('✅ Bootstrap Modal já disponível');
    window.ModalLoader.register('bootstrap');
}

// Aguardar DOM carregar para verificar dependências
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM carregado, verificando modais...');
    
    // Verificar se Bootstrap está disponível
    if (typeof bootstrap !== 'undefined' && typeof bootstrap.Modal !== 'undefined') {
        window.ModalLoader.register('bootstrap');
    }
    
    // Aguardar um pouco e verificar novamente
    setTimeout(() => {
        window.ModalLoader.checkDependencies();
    }, 500);
});

// Aguardar página completamente carregada
window.addEventListener('load', function() {
    console.log('🌐 Página completamente carregada, verificação final...');
    
    setTimeout(() => {
        window.ModalLoader.ensureAdvogadoFunctions();
        window.ModalLoader.debug();
    }, 1000);
});

console.log('📂 Modal Loader configurado e pronto');
