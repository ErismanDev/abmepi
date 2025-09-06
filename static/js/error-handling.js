/**
 * Sistema de Visualização de Erros para Modais
 * Reutilizável em todos os sistemas da ABMEPI
 */

// ============================================================================
// FUNÇÕES DE VISUALIZAÇÃO DE ERROS PARA MODAIS
// ============================================================================

// Função para exibir resumo de erros no topo do modal
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
    `;
    
    // Inserir no topo do modal
    modalBody.insertBefore(errorAlert, modalBody.firstChild);
    console.log('✅ Resumo de erros inserido no modal');
    
    // Adicionar botão para fechar o alerta
    const closeButton = document.createElement('button');
    closeButton.type = 'button';
    closeButton.className = 'btn-close position-absolute top-0 end-0 m-3';
    closeButton.setAttribute('aria-label', 'Fechar');
    closeButton.onclick = () => errorAlert.remove();
    errorAlert.style.position = 'relative';
    errorAlert.appendChild(closeButton);
}

// Função para aplicar estilos de erro aos campos
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

// Função para criar mensagem de erro para um campo específico
function createFieldErrorMessage(field, errorMessages) {
    if (!field || !errorMessages) return;
    
    // Remover mensagens de erro anteriores
    const existingError = field.parentNode.querySelector('.invalid-feedback');
    if (existingError) {
        existingError.remove();
    }
    
    // Criar nova mensagem de erro
    const errorDiv = document.createElement('div');
    errorDiv.className = 'invalid-feedback';
    errorDiv.innerHTML = `
        <i class="fas fa-exclamation-circle me-1"></i>
        ${Array.isArray(errorMessages) ? errorMessages.join(', ') : errorMessages}
    `;
    
    // Inserir após o campo
    field.parentNode.insertBefore(errorDiv, field.nextSibling);
    console.log(`✅ Mensagem de erro criada para ${field.name}:`, errorMessages);
}

// Função para rolar para o primeiro campo com erro
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

// Função para limpar todos os erros de validação
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

// Função para processar resposta de erro do servidor
function handleServerErrorResponse(data, modalId = null) {
    console.log('❌ Processando resposta de erro do servidor:', data);
    
    if (data.errors && Object.keys(data.errors).length > 0) {
        console.log('❌ Erros de validação detectados:', data.errors);
        
        // Exibir resumo dos erros no topo do modal
        showErrorSummaryInModal(data.errors, Object.keys(data.errors).length, data.message);
        
        // Aplicar estilos de erro aos campos
        setTimeout(() => {
            applyErrorStylesToFields(data.errors);
            scrollToFirstError();
        }, 100);
        
        return true; // Indica que erros foram processados
    } else {
        console.warn('⚠️ Resposta de erro sem detalhes específicos');
        return false; // Indica que não há erros para processar
    }
}

// Função para validar formulário antes do envio
function validateFormBeforeSubmit(form) {
    console.log('🔍 Validando formulário antes do envio...');
    
    // Limpar erros anteriores
    clearValidationErrors();
    
    let isValid = true;
    const errors = {};
    
    // Verificar campos obrigatórios
    const requiredFields = form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
        if (!field.value || field.value.trim() === '') {
            const fieldName = field.name || field.id || 'Campo obrigatório';
            errors[fieldName] = ['Este campo é obrigatório'];
            isValid = false;
        }
    });
    
    // Se houver erros, aplicá-los
    if (!isValid) {
        console.log('❌ Formulário inválido, aplicando erros:', errors);
        showErrorSummaryInModal(errors, Object.keys(errors).length, 'Formulário com campos obrigatórios não preenchidos');
        setTimeout(() => {
            applyErrorStylesToFields(errors);
            scrollToFirstError();
        }, 100);
    } else {
        console.log('✅ Formulário válido');
    }
    
    return isValid;
}

// Exportar funções para uso global
window.showErrorSummaryInModal = showErrorSummaryInModal;
window.applyErrorStylesToFields = applyErrorStylesToFields;
window.createFieldErrorMessage = createFieldErrorMessage;
window.scrollToFirstError = scrollToFirstError;
window.clearValidationErrors = clearValidationErrors;
window.handleServerErrorResponse = handleServerErrorResponse;
window.validateFormBeforeSubmit = validateFormBeforeSubmit;

console.log('🚀 Sistema de visualização de erros carregado com sucesso!');
