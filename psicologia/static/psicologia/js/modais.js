/**
 * SISTEMA DE MODAIS PARA PSICOLOGIA
 * Funções específicas para o módulo de psicologia
 */

console.log('🧠 Modais Psicologia JavaScript carregado');

// Função para abrir modal de criação de psicólogo
window.openPsicologoModal = function() {
    console.log('🚀 Abrindo modal de criação de psicólogo');
    
    fetch('/psicologia/psicologos/modal/novo/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-user-md me-2"></i>Novo Psicólogo';
                const conteudo = data.html;
                const formId = 'psicologoForm';
                const actionUrl = '/psicologia/psicologos/modal/novo/';
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Função para abrir modal de edição de psicólogo
window.openPsicologoEditModal = function(psicologoId) {
    console.log('🚀 Abrindo modal de edição de psicólogo:', psicologoId);
    
    if (!psicologoId) {
        console.error('❌ ID do psicólogo não fornecido');
        alert('Erro: ID do psicólogo não fornecido');
        return;
    }
    
    fetch(`/psicologia/psicologos/modal/${psicologoId}/editar/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-edit me-2"></i>Editar Psicólogo';
                const conteudo = data.html;
                const formId = 'psicologoForm';
                const actionUrl = `/psicologia/psicologos/modal/${psicologoId}/editar/`;
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Função para abrir modal de criação de paciente
window.openPacienteModal = function() {
    console.log('🚀 Abrindo modal de criação de paciente');
    
    fetch('/psicologia/pacientes/modal/novo/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-user me-2"></i>Novo Paciente';
                const conteudo = data.html;
                const formId = 'pacienteForm';
                const actionUrl = '/psicologia/pacientes/modal/novo/';
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Função para abrir modal de edição de paciente
window.openPacienteEditModal = function(pacienteId) {
    console.log('🚀 Abrindo modal de edição de paciente:', pacienteId);
    
    if (!pacienteId) {
        console.error('❌ ID do paciente não fornecido');
        alert('Erro: ID do paciente não fornecido');
        return;
    }
    
    fetch(`/psicologia/pacientes/modal/${pacienteId}/editar/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-edit me-2"></i>Editar Paciente';
                const conteudo = data.html;
                const formId = 'pacienteForm';
                const actionUrl = `/psicologia/pacientes/modal/${pacienteId}/editar/`;
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Função para abrir modal de criação de sessão
window.openSessaoModal = function() {
    console.log('🚀 Abrindo modal de criação de sessão');
    
    fetch('/psicologia/sessoes/modal/nova/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-calendar-plus me-2"></i>Nova Sessão';
                const conteudo = data.html;
                const formId = 'sessaoForm';
                const actionUrl = '/psicologia/sessoes/modal/nova/';
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Função para abrir modal de edição de sessão
window.openSessaoEditModal = function(sessaoId) {
    console.log('🚀 Abrindo modal de edição de sessão:', sessaoId);
    
    if (!sessaoId) {
        console.error('❌ ID da sessão não fornecido');
        alert('Erro: ID da sessão não fornecido');
        return;
    }
    
    fetch(`/psicologia/sessoes/modal/${sessaoId}/editar/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-edit me-2"></i>Editar Sessão';
                const conteudo = data.html;
                const formId = 'sessaoForm';
                const actionUrl = `/psicologia/sessoes/modal/${sessaoId}/editar/`;
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Função para abrir modal de criação de prontuário
window.openProntuarioModal = function() {
    console.log('🚀 Abrindo modal de criação de prontuário');
    
    fetch('/psicologia/prontuarios/modal/novo/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-file-medical me-2"></i>Novo Prontuário';
                const conteudo = data.html;
                const formId = 'prontuarioForm';
                const actionUrl = '/psicologia/prontuarios/modal/novo/';
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Função para abrir modal de edição de prontuário
window.openProntuarioEditModal = function(prontuarioId) {
    console.log('🚀 Abrindo modal de edição de prontuário:', prontuarioId);
    
    if (!prontuarioId) {
        console.error('❌ ID do prontuário não fornecido');
        alert('Erro: ID do prontuário não fornecido');
        return;
    }
    
    fetch(`/psicologia/prontuarios/modal/${prontuarioId}/editar/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-edit me-2"></i>Editar Prontuário';
                const conteudo = data.html;
                const formId = 'prontuarioForm';
                const actionUrl = `/psicologia/prontuarios/modal/${prontuarioId}/editar/`;
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Função para abrir modal de criação de evolução
window.openEvolucaoModal = function() {
    console.log('🚀 Abrindo modal de criação de evolução');
    
    fetch('/psicologia/evolucoes/modal/nova/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-chart-line me-2"></i>Nova Evolução';
                const conteudo = data.html;
                const formId = 'evolucaoForm';
                const actionUrl = '/psicologia/evolucoes/modal/nova/';
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Função para abrir modal de edição de evolução
window.openEvolucaoEditModal = function(evolucaoId) {
    console.log('🚀 Abrindo modal de edição de evolução:', evolucaoId);
    
    if (!evolucaoId) {
        console.error('❌ ID da evolução não fornecido');
        alert('Erro: ID da evolução não fornecido');
        return;
    }
    
    fetch(`/psicologia/evolucoes/modal/${evolucaoId}/editar/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-edit me-2"></i>Editar Evolução';
                const conteudo = data.html;
                const formId = 'evolucaoForm';
                const actionUrl = `/psicologia/evolucoes/modal/${evolucaoId}/editar/`;
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Função para abrir modal de criação de documento
window.openDocumentoModal = function() {
    console.log('🚀 Abrindo modal de criação de documento');
    
    fetch('/psicologia/documentos/modal/novo/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-file-alt me-2"></i>Novo Documento';
                const conteudo = data.html;
                const formId = 'documentoForm';
                const actionUrl = '/psicologia/documentos/modal/novo/';
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Função para abrir modal de edição de documento
window.openDocumentoEditModal = function(documentoId) {
    console.log('🚀 Abrindo modal de edição de documento:', documentoId);
    
    if (!documentoId) {
        console.error('❌ ID do documento não fornecido');
        alert('Erro: ID do documento não fornecido');
        return;
    }
    
    fetch(`/psicologia/documentos/modal/${documentoId}/editar/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-edit me-2"></i>Editar Documento';
                const conteudo = data.html;
                const formId = 'documentoForm';
                const actionUrl = `/psicologia/documentos/modal/${documentoId}/editar/`;
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Função para abrir modal de criação de agenda
window.openAgendaModal = function() {
    console.log('🚀 Abrindo modal de criação de agenda');
    
    fetch('/psicologia/agenda/modal/nova/')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-calendar-alt me-2"></i>Nova Agenda';
                const conteudo = data.html;
                const formId = 'agendaForm';
                const actionUrl = '/psicologia/agenda/modal/nova/';
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Função para abrir modal de edição de agenda
window.openAgendaEditModal = function(agendaId) {
    console.log('🚀 Abrindo modal de edição de agenda:', agendaId);
    
    if (!agendaId) {
        console.error('❌ ID da agenda não fornecido');
        alert('Erro: ID da agenda não fornecido');
        return;
    }
    
    fetch(`/psicologia/agenda/modal/${agendaId}/editar/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const titulo = '<i class="fas fa-edit me-2"></i>Editar Agenda';
                const conteudo = data.html;
                const formId = 'agendaForm';
                const actionUrl = `/psicologia/agenda/modal/${agendaId}/editar/`;
                
                // Usar a função openFormModal se disponível, senão criar modal diretamente
                if (typeof window.openFormModal === 'function') {
                    window.openFormModal(titulo, conteudo, formId, actionUrl);
                } else {
                    console.warn('⚠️ openFormModal não disponível, criando modal diretamente');
                    createModalDirectly(titulo, conteudo, formId, actionUrl);
                }
            } else {
                console.error('❌ Erro ao carregar formulário:', data.message);
                alert('Erro ao carregar formulário: ' + data.message);
            }
        })
        .catch(error => {
            console.error('❌ Erro na requisição:', error);
            alert('Erro ao carregar formulário. Tente novamente.');
        });
};

// Verificar se as funções foram carregadas corretamente
document.addEventListener('DOMContentLoaded', function() {
    console.log('🧠 Verificando funções dos modais de psicologia...');
    
    const functions = [
        'openPsicologoModal', 'openPsicologoEditModal',
        'openPacienteModal', 'openPacienteEditModal',
        'openSessaoModal', 'openSessaoEditModal',
        'openProntuarioModal', 'openProntuarioEditModal',
        'openEvolucaoModal', 'openEvolucaoEditModal',
        'openDocumentoModal', 'openDocumentoEditModal',
        'openAgendaModal', 'openAgendaEditModal'
    ];
    
    functions.forEach(funcName => {
        if (typeof window[funcName] === 'function') {
            console.log(`✅ ${funcName} disponível`);
        } else {
            console.error(`❌ ${funcName} não disponível`);
        }
    });
    
    // Verificar se a função base openFormModal está disponível
    if (typeof window.openFormModal === 'function') {
        console.log('✅ openFormModal disponível (função base)');
    } else {
        console.error('❌ openFormModal não disponível (função base)');
    }
});

// Função para criar modal diretamente quando openFormModal não estiver disponível
function createModalDirectly(titulo, conteudo, formId, actionUrl) {
    console.log('🔧 Criando modal diretamente:', titulo);
    
    try {
        // Remover modal existente se houver
        const existingModal = document.getElementById('formModal');
        if (existingModal) {
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
        
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Configurar formulário
        setTimeout(() => {
            const form = document.getElementById(formId);
            if (form && actionUrl) {
                form.action = actionUrl;
                
                // Configurar botão de submit
                const submitBtn = document.getElementById('modalSubmitBtn');
                if (submitBtn) {
                    submitBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        submitFormDirectly(form, actionUrl);
                    });
                }
                
                // Configurar submit do formulário
                form.addEventListener('submit', function(e) {
                    e.preventDefault();
                    submitFormDirectly(form, actionUrl);
                });
            }
        }, 100);
        
        // Mostrar modal
        const modalElement = document.getElementById('formModal');
        if (modalElement) {
            try {
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
                console.log('✅ Modal criado e exibido com sucesso');
            } catch (modalError) {
                console.error('❌ Erro ao criar modal Bootstrap:', modalError);
                modalElement.style.display = 'block';
                modalElement.classList.add('show');
            }
        }
        
    } catch (error) {
        console.error('❌ Erro ao criar modal diretamente:', error);
        alert('Erro ao criar modal. Tente novamente.');
    }
}

// Função para submeter formulário diretamente
function submitFormDirectly(form, actionUrl) {
    console.log('📝 Submetendo formulário diretamente:', actionUrl);
    
    const formData = new FormData(form);
    const submitBtn = document.getElementById('modalSubmitBtn');
    const originalText = submitBtn ? submitBtn.innerHTML : 'Salvar';
    
    if (submitBtn) {
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Salvando...';
        submitBtn.disabled = true;
    }
    
    fetch(actionUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('✅ Sucesso! Fechando modal...');
            alert(data.message || 'Operação realizada com sucesso!');
            
            // Fechar modal
            const modalElement = document.getElementById('formModal');
            if (modalElement) {
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {
                    modal.hide();
                } else {
                    modalElement.style.display = 'none';
                    modalElement.classList.remove('show');
                }
            }
            
            if (data.reload) {
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
        } else {
            console.log('❌ Erro na operação:', data.message);
            alert(data.message || 'Erro na operação');
            
            // Exibir erros de validação se houver
            if (data.errors) {
                displayFormErrors(data.errors);
            }
        }
    })
    .catch(error => {
        console.error('❌ Erro no submit:', error);
        alert('Erro ao processar formulário. Tente novamente.');
    })
    .finally(() => {
        if (submitBtn) {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }
    });
}

// Função para obter token CSRF
function getCSRFToken() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    return csrfToken ? csrfToken.value : '';
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
    
    // Marcar campos com erro
    Object.keys(errors).forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.classList.add('is-invalid');
            
            const errorDiv = document.createElement('div');
            errorDiv.className = 'invalid-feedback';
            errorDiv.textContent = Array.isArray(errors[fieldName]) ? errors[fieldName].join(', ') : errors[fieldName];
            
            field.parentNode.appendChild(errorDiv);
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
// FUNÇÕES DE CONFIRMAÇÃO DE EXCLUSÃO
// ============================================================================

/**
 * Confirmar exclusão de psicólogo
 */
window.confirmarExclusaoPsicologo = function(psicologoId, nomePsicologo) {
    console.log('🗑️ Confirmando exclusão de psicólogo:', psicologoId, nomePsicologo);
    
    const mensagem = `Tem certeza que deseja excluir o psicólogo <strong>${nomePsicologo}</strong>?<br><br>
                     <div class="alert alert-warning mt-2">
                         <i class="fas fa-exclamation-triangle me-2"></i>
                         <strong>Atenção:</strong> Esta ação não pode ser desfeita.
                     </div>`;
    
    // Usar a função showConfirmMessage se disponível, senão usar confirm nativo
    if (typeof showConfirmMessage === 'function') {
        showConfirmMessage(mensagem, () => {
            window.location.href = `/psicologia/psicologos/${psicologoId}/excluir/`;
        });
    } else {
        if (confirm(`Tem certeza que deseja excluir o psicólogo ${nomePsicologo}?`)) {
            window.location.href = `/psicologia/psicologos/${psicologoId}/excluir/`;
        }
    }
};

/**
 * Confirmar exclusão de paciente
 */
window.confirmarExclusaoPaciente = function(pacienteId, nomePaciente) {
    console.log('🗑️ Confirmando exclusão de paciente:', pacienteId, nomePaciente);
    
    const mensagem = `Tem certeza que deseja excluir o paciente <strong>${nomePaciente}</strong>?<br><br>
                     <div class="alert alert-warning mt-2">
                         <i class="fas fa-exclamation-triangle me-2"></i>
                         <strong>Atenção:</strong> Esta ação não pode ser desfeita.
                     </div>`;
    
    // Usar a função showConfirmMessage se disponível, senão usar confirm nativo
    if (typeof showConfirmMessage === 'function') {
        showConfirmMessage(mensagem, () => {
            window.location.href = `/psicologia/pacientes/${pacienteId}/excluir/`;
        });
    } else {
        if (confirm(`Tem certeza que deseja excluir o paciente ${nomePaciente}?`)) {
            window.location.href = `/psicologia/pacientes/${pacienteId}/excluir/`;
        }
    }
};

console.log('🧠 Modais Psicologia JavaScript configurado e pronto');
