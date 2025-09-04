/**
 * JavaScript para modais do módulo Hotel de Trânsito
 */

// Função para inicializar todos os modais
function inicializarModaisHotelTransito() {
    // Inicializar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Inicializar popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Configurar validação de formulários
    configurarValidacaoFormularios();
    
    // Configurar máscaras de campos
    configurarMascarasCampos();
    
    // Configurar eventos de campos dependentes
    configurarCamposDependentes();
}

// Função para configurar validação de formulários
function configurarValidacaoFormularios() {
    // Adicionar validação personalizada para campos de data
    document.querySelectorAll('input[type="date"]').forEach(function(input) {
        input.addEventListener('change', function() {
            validarDatas(this);
        });
    });

    // Adicionar validação para campos de valor monetário
    document.querySelectorAll('input[type="number"]').forEach(function(input) {
        if (input.step === '0.01') {
            input.addEventListener('blur', function() {
                formatarValorMonetario(this);
            });
        }
    });
}

// Função para validar datas
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

// Função para formatar valor monetário
function formatarValorMonetario(input) {
    if (input.value) {
        const valor = parseFloat(input.value);
        if (!isNaN(valor)) {
            input.value = valor.toFixed(2);
        }
    }
}

// Função para configurar máscaras de campos
function configurarMascarasCampos() {
    // Máscara para telefone
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

    // Máscara para CEP
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

    // Máscara para CPF
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
}

// Função para configurar campos dependentes
function configurarCamposDependentes() {
    // Campo tipo de hóspede
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

// Função para abrir modal de criação rápida
function abrirModalCriacaoRapida(tipo, titulo) {
    const modal = document.getElementById('modalCriacaoRapida');
    const modalTitle = modal.querySelector('.modal-title');
    const modalBody = modal.querySelector('.modal-body');
    
    modalTitle.textContent = `Novo ${titulo}`;
    
    // Carregar formulário específico via AJAX
    fetch(`/hotel_transito/ajax/form/${tipo}/`)
        .then(response => response.text())
        .then(html => {
            modalBody.innerHTML = html;
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
        })
        .catch(error => {
            console.error('Erro ao carregar formulário:', error);
            modalBody.innerHTML = '<p class="text-danger">Erro ao carregar formulário</p>';
        });
}

// Função para buscar hóspedes
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

// Função para exibir resultados da busca
function exibirResultadosBusca(hospedes) {
    const container = document.getElementById('resultadosBuscaHospedes');
    if (!container) return;
    
    if (hospedes.length === 0) {
        container.innerHTML = '<p class="text-muted">Nenhum hóspede encontrado</p>';
        return;
    }
    
    let html = '<div class="list-group">';
    hospedes.forEach(hospede => {
        html += `
            <a href="#" class="list-group-item list-group-item-action" 
               onclick="selecionarHospede(${hospede.id}, '${hospede.nome_completo}')">
                <div class="d-flex w-100 justify-content-between">
                    <h6 class="mb-1">${hospede.nome_completo}</h6>
                    <small class="text-muted">${hospede.tipo_hospede}</small>
                </div>
                <small>${hospede.telefone || 'Sem telefone'} - ${hospede.cidade || 'Sem cidade'}</small>
            </a>
        `;
    });
    html += '</div>';
    
    container.innerHTML = html;
}

// Função para selecionar hóspede
function selecionarHospede(id, nome) {
    const campoHospede = document.querySelector('select[name="hospede"]');
    if (campoHospede) {
        // Adicionar opção se não existir
        let option = campoHospede.querySelector(`option[value="${id}"]`);
        if (!option) {
            option = document.createElement('option');
            option.value = id;
            option.textContent = nome;
            campoHospede.appendChild(option);
        }
        campoHospede.value = id;
    }
    
    // Limpar resultados da busca
    const container = document.getElementById('resultadosBuscaHospedes');
    if (container) {
        container.innerHTML = '';
    }
}

// Função para calcular valor total da reserva
function calcularValorTotalReserva() {
    const dataEntrada = document.querySelector('input[name="data_entrada"]');
    const dataSaida = document.querySelector('input[name="data_saida"]');
    const valorDiaria = document.querySelector('input[name="valor_diaria"]');
    const campoTotal = document.querySelector('input[name="valor_total"]');
    
    if (dataEntrada && dataSaida && valorDiaria && campoTotal) {
        if (dataEntrada.value && dataSaida.value && valorDiaria.value) {
            const entrada = new Date(dataEntrada.value);
            const saida = new Date(dataSaida.value);
            const diaria = parseFloat(valorDiaria.value);
            
            if (entrada < saida && !isNaN(diaria)) {
                const diffTime = Math.abs(saida - entrada);
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
                const total = diffDays * diaria;
                campoTotal.value = total.toFixed(2);
            }
        }
    }
}

// Função para verificar disponibilidade do quarto
function verificarDisponibilidadeQuarto(quartoId, dataEntrada, dataSaida) {
    if (!quartoId || !dataEntrada || !dataSaida) return;
    
    fetch(`/hotel_transito/ajax/verificar-disponibilidade/?quarto=${quartoId}&entrada=${dataEntrada}&saida=${dataSaida}`)
        .then(response => response.json())
        .then(data => {
            if (data.disponivel) {
                mostrarMensagemDisponibilidade('Quarto disponível para o período selecionado', 'success');
            } else {
                mostrarMensagemDisponibilidade('Quarto não disponível para o período selecionado', 'danger');
            }
        })
        .catch(error => {
            console.error('Erro ao verificar disponibilidade:', error);
        });
}

// Função para mostrar mensagem de disponibilidade
function mostrarMensagemDisponibilidade(mensagem, tipo) {
    const container = document.getElementById('mensagemDisponibilidade');
    if (container) {
        container.innerHTML = `
            <div class="alert alert-${tipo} alert-dismissible fade show" role="alert">
                ${mensagem}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
    }
}

// Função para limpar formulário
function limparFormulario(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        
        // Limpar mensagens de erro
        form.querySelectorAll('.is-invalid').forEach(function(field) {
            field.classList.remove('is-invalid');
        });
        
        // Limpar mensagens de sucesso
        const alerts = form.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            alert.remove();
        });
    }
}

// Função para confirmar exclusão
function confirmarExclusao(mensagem, url) {
    if (confirm(mensagem)) {
        window.location.href = url;
    }
}

// Função para exportar dados
function exportarDados(formato, tipo) {
    const form = document.getElementById('formRelatorio');
    if (!form) return;
    
    const formData = new FormData(form);
    formData.append('formato', formato);
    formData.append('tipo', tipo);
    
    fetch('/hotel_transito/ajax/exportar/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `relatorio_${tipo}_${new Date().toISOString().split('T')[0]}.${formato}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('Erro ao exportar:', error);
        alert('Erro ao exportar dados');
    });
}

// Inicializar quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', function() {
    inicializarModaisHotelTransito();
    
    // Adicionar eventos para campos de data
    document.querySelectorAll('input[name="data_entrada"], input[name="data_saida"]').forEach(function(input) {
        input.addEventListener('change', calcularValorTotalReserva);
    });
    
    // Adicionar eventos para campo de valor da diária
    document.querySelectorAll('input[name="valor_diaria"]').forEach(function(input) {
        input.addEventListener('input', calcularValorTotalReserva);
    });
    
    // Adicionar eventos para busca de hóspedes
    const campoBuscaHospede = document.querySelector('input[name="busca_hospede"]');
    if (campoBuscaHospede) {
        let timeout;
        campoBuscaHospede.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                buscarHospedes(this.value);
            }, 300);
        });
    }
});

// Exportar funções para uso global
window.HotelTransitoModais = {
    abrirModalCriacaoRapida,
    buscarHospedes,
    selecionarHospede,
    calcularValorTotalReserva,
    verificarDisponibilidadeQuarto,
    limparFormulario,
    confirmarExclusao,
    exportarDados
};
