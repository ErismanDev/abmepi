/**
 * Visualizador de Senhas Global para ABMEPI
 * Adiciona botões de mostrar/ocultar senha em todos os campos de senha
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 Inicializando visualizador de senhas global...');
    
    // Função para adicionar visualizador a um campo de senha
    function addPasswordViewer(passwordField) {
        if (!passwordField || passwordField.type !== 'password') {
            return;
        }
        
        // Verificar se já tem visualizador
        if (passwordField.nextElementSibling && passwordField.nextElementSibling.classList.contains('password-viewer-btn')) {
            return;
        }
        
        // Criar botão de visualização
        const viewerBtn = document.createElement('button');
        viewerBtn.type = 'button';
        viewerBtn.className = 'btn btn-outline-secondary btn-sm ms-2 password-viewer-btn';
        viewerBtn.innerHTML = '<i class="fas fa-eye"></i>';
        viewerBtn.title = 'Mostrar senha';
        
        // Adicionar evento de clique
        viewerBtn.addEventListener('click', function() {
            togglePasswordVisibility(passwordField, viewerBtn);
        });
        
        // Inserir botão após o campo
        passwordField.parentNode.insertBefore(viewerBtn, passwordField.nextSibling);
        
        console.log('✅ Visualizador adicionado ao campo:', passwordField.name);
    }
    
    // Função para alternar visibilidade da senha
    function togglePasswordVisibility(passwordField, button) {
        const icon = button.querySelector('i');
        
        if (passwordField.type === 'password') {
            passwordField.type = 'text';
            icon.className = 'fas fa-eye-slash';
            button.title = 'Ocultar senha';
            button.classList.remove('btn-outline-secondary');
            button.classList.add('btn-outline-danger');
        } else {
            passwordField.type = 'password';
            icon.className = 'fas fa-eye';
            button.title = 'Mostrar senha';
            button.classList.remove('btn-outline-danger');
            button.classList.add('btn-outline-secondary');
        }
    }
    
    // Função para adicionar visualizadores a todos os campos de senha
    function addPasswordViewersToAllFields() {
        const passwordFields = document.querySelectorAll('input[type="password"]');
        console.log(`🔍 Encontrados ${passwordFields.length} campos de senha`);
        
        passwordFields.forEach(function(field) {
            addPasswordViewer(field);
        });
    }
    
    // Adicionar visualizadores inicialmente
    addPasswordViewersToAllFields();
    
    // Observar mudanças no DOM para campos adicionados dinamicamente
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // Verificar se o nó adicionado é um campo de senha
                        if (node.tagName === 'INPUT' && node.type === 'password') {
                            addPasswordViewer(node);
                        }
                        
                        // Verificar campos de senha dentro do nó adicionado
                        const passwordFields = node.querySelectorAll ? node.querySelectorAll('input[type="password"]') : [];
                        passwordFields.forEach(function(field) {
                            addPasswordViewer(field);
                        });
                    }
                });
            }
        });
    });
    
    // Iniciar observação
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
    
    console.log('✅ Visualizador de senhas global inicializado com sucesso!');
});

// Função global para alternar visibilidade (pode ser chamada de outros scripts)
window.togglePasswordVisibility = function(fieldId) {
    const field = document.getElementById(fieldId);
    const button = field.nextElementSibling;
    
    if (field && button && button.classList.contains('password-viewer-btn')) {
        if (field.type === 'password') {
            field.type = 'text';
            button.querySelector('i').className = 'fas fa-eye-slash';
            button.title = 'Ocultar senha';
            button.classList.remove('btn-outline-secondary');
            button.classList.add('btn-outline-danger');
        } else {
            field.type = 'password';
            button.querySelector('i').className = 'fas fa-eye';
            button.title = 'Mostrar senha';
            button.classList.remove('btn-outline-danger');
            button.classList.add('btn-outline-secondary');
        }
    }
};
