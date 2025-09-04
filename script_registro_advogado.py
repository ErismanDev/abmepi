#!/usr/bin/env python
"""
Script completo para registro de advogados
Inclui validação, tratamento de erros e correções automáticas
"""

import os
import sys
import django
from datetime import date
import re

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from assejus.models import Advogado
from assejus.forms import AdvogadoForm

class RegistradorAdvogados:
    """Classe para gerenciar o registro de advogados"""
    
    def __init__(self):
        self.erros_encontrados = []
        self.advogados_criados = []
    
    def validar_cpf(self, cpf):
        """Valida CPF usando algoritmo oficial"""
        # Remove caracteres não numéricos
        cpf = ''.join(filter(str.isdigit, cpf))
        
        if len(cpf) != 11:
            return False
        
        # Verifica se todos os dígitos são iguais
        if cpf == cpf[0] * 11:
            return False
        
        # Validação do primeiro dígito verificador
        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        resto = soma % 11
        if resto < 2:
            digito1 = 0
        else:
            digito1 = 11 - resto
        
        if int(cpf[9]) != digito1:
            return False
        
        # Validação do segundo dígito verificador
        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        resto = soma % 11
        if resto < 2:
            digito2 = 0
        else:
            digito2 = 11 - resto
        
        if int(cpf[10]) != digito2:
            return False
        
        return True
    
    def validar_oab(self, oab):
        """Valida formato da OAB"""
        # Padrão: número/UF (ex: 123456/SP)
        padrao = r'^\d{1,6}/[A-Z]{2}$'
        return bool(re.match(padrao, oab))
    
    def validar_cep(self, cep):
        """Valida formato do CEP"""
        # Remove formatação
        cep_limpo = ''.join(filter(str.isdigit, cep))
        return len(cep_limpo) == 8
    
    def validar_telefone(self, telefone):
        """Valida formato do telefone"""
        # Remove formatação
        tel_limpo = ''.join(filter(str.isdigit, telefone))
        return len(tel_limpo) >= 10 and len(tel_limpo) <= 11
    
    def formatar_cpf(self, cpf):
        """Formata CPF para exibição"""
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        if len(cpf_limpo) == 11:
            return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return cpf
    
    def formatar_cep(self, cep):
        """Formata CEP para exibição"""
        cep_limpo = ''.join(filter(str.isdigit, cep))
        if len(cep_limpo) == 8:
            return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        return cep
    
    def formatar_telefone(self, telefone):
        """Formata telefone para exibição"""
        tel_limpo = ''.join(filter(str.isdigit, telefone))
        if len(tel_limpo) == 11:
            return f"({tel_limpo[:2]}) {tel_limpo[2:7]}-{tel_limpo[7:]}"
        elif len(tel_limpo) == 10:
            return f"({tel_limpo[:2]}) {tel_limpo[2:6]}-{tel_limpo[6:]}"
        return telefone
    
    def corrigir_dados(self, dados):
        """Corrige dados comuns do advogado"""
        dados_corrigidos = dados.copy()
        correcoes = []
        
        # Corrigir CPF
        if 'cpf' in dados:
            cpf_limpo = ''.join(filter(str.isdigit, dados['cpf']))
            if len(cpf_limpo) == 11:
                dados_corrigidos['cpf'] = cpf_limpo
                correcoes.append(f"CPF: {dados['cpf']} -> {self.formatar_cpf(cpf_limpo)}")
        
        # Corrigir CEP
        if 'cep' in dados:
            cep_limpo = ''.join(filter(str.isdigit, dados['cep']))
            if len(cep_limpo) == 8:
                dados_corrigidos['cep'] = cep_limpo
                correcoes.append(f"CEP: {dados['cep']} -> {self.formatar_cep(cep_limpo)}")
        
        # Corrigir telefone
        if 'telefone' in dados:
            tel_limpo = ''.join(filter(str.isdigit, dados['telefone']))
            if len(tel_limpo) >= 10:
                dados_corrigidos['telefone'] = tel_limpo
                correcoes.append(f"Telefone: {dados['telefone']} -> {self.formatar_telefone(tel_limpo)}")
        
        # Corrigir celular
        if 'celular' in dados:
            cel_limpo = ''.join(filter(str.isdigit, dados['celular']))
            if len(cel_limpo) >= 10:
                dados_corrigidos['celular'] = cel_limpo
                correcoes.append(f"Celular: {dados['celular']} -> {self.formatar_telefone(cel_limpo)}")
        
        return dados_corrigidos, correcoes
    
    def validar_dados_completos(self, dados):
        """Valida todos os dados antes de criar o advogado"""
        erros = []
        
        # Validações básicas
        if not dados.get('nome', '').strip():
            erros.append("Nome é obrigatório")
        
        if not dados.get('cpf'):
            erros.append("CPF é obrigatório")
        elif not self.validar_cpf(dados['cpf']):
            erros.append("CPF inválido")
        
        if not dados.get('oab'):
            erros.append("OAB é obrigatória")
        elif not self.validar_oab(dados['oab']):
            erros.append("Formato de OAB inválido (deve ser: número/UF)")
        
        if not dados.get('email'):
            erros.append("Email é obrigatório")
        elif '@' not in dados['email']:
            erros.append("Email inválido")
        
        if not dados.get('telefone'):
            erros.append("Telefone é obrigatório")
        elif not self.validar_telefone(dados['telefone']):
            erros.append("Telefone inválido")
        
        if not dados.get('endereco', '').strip():
            erros.append("Endereço é obrigatório")
        
        if not dados.get('cidade', '').strip():
            erros.append("Cidade é obrigatória")
        
        if not dados.get('estado'):
            erros.append("Estado é obrigatório")
        
        if not dados.get('cep'):
            erros.append("CEP é obrigatório")
        elif not self.validar_cep(dados['cep']):
            erros.append("CEP inválido")
        
        if not dados.get('data_inscricao_oab'):
            erros.append("Data de inscrição na OAB é obrigatória")
        
        if not dados.get('experiencia_anos'):
            erros.append("Anos de experiência é obrigatório")
        
        # Verificar duplicatas
        if dados.get('cpf'):
            if Advogado.objects.filter(cpf=dados['cpf']).exists():
                erros.append("Já existe advogado com este CPF")
        
        if dados.get('oab'):
            if Advogado.objects.filter(oab=dados['oab']).exists():
                erros.append("Já existe advogado com esta OAB")
        
        return erros
    
    def criar_advogado(self, dados):
        """Cria um novo advogado"""
        try:
            # Validar dados
            erros_validacao = self.validar_dados_completos(dados)
            if erros_validacao:
                return False, f"Erros de validação: {'; '.join(erros_validacao)}"
            
            # Corrigir dados
            dados_corrigidos, correcoes = self.corrigir_dados(dados)
            
            # Criar formulário
            form = AdvogadoForm(data=dados_corrigidos)
            if not form.is_valid():
                return False, f"Erros no formulário: {form.errors}"
            
            # Salvar advogado
            advogado = form.save()
            self.advogados_criados.append(advogado)
            
            return True, {
                'advogado': advogado,
                'correcoes': correcoes,
                'id': advogado.id
            }
            
        except Exception as e:
            return False, f"Erro ao criar advogado: {str(e)}"
    
    def listar_advogados(self):
        """Lista todos os advogados cadastrados"""
        advogados = Advogado.objects.all().order_by('nome')
        print(f"\n=== ADVOGADOS CADASTRADOS ({advogados.count()}) ===")
        
        for adv in advogados:
            print(f"ID: {adv.id} | Nome: {adv.nome} | OAB: {adv.oab} | CPF: {self.formatar_cpf(adv.cpf)}")
            print(f"     Email: {adv.email} | Situação: {adv.situacao}")
            print(f"     Especialidades: {adv.especialidades or 'Não informado'}")
            print("-" * 60)
    
    def buscar_advogado(self, termo):
        """Busca advogado por nome, CPF ou OAB"""
        try:
            # Buscar por CPF
            if re.match(r'\d{3}\.\d{3}\.\d{3}-\d{2}', termo) or len(''.join(filter(str.isdigit, termo))) == 11:
                cpf_limpo = ''.join(filter(str.isdigit, termo))
                advogado = Advogado.objects.filter(cpf=cpf_limpo).first()
                if advogado:
                    return advogado
            
            # Buscar por OAB
            if '/' in termo:
                advogado = Advogado.objects.filter(oab=termo).first()
                if advogado:
                    return advogado
            
            # Buscar por nome
            advogado = Advogado.objects.filter(nome__icontains=termo).first()
            if advogado:
                return advogado
            
            return None
            
        except Exception as e:
            print(f"Erro na busca: {e}")
            return None
    
    def limpar_dados_teste(self):
        """Remove advogados criados durante os testes"""
        for advogado in self.advogados_criados:
            try:
                advogado.delete()
                print(f"✅ Advogado de teste removido: {advogado.nome}")
            except Exception as e:
                print(f"❌ Erro ao remover advogado de teste: {e}")

def main():
    """Função principal"""
    print("=== SISTEMA DE REGISTRO DE ADVOGADOS ===\n")
    
    registrador = RegistradorAdvogados()
    
    # Dados de exemplo para teste
    dados_exemplo = {
        'nome': 'Dr. Maria Silva Costa',
        'cpf': '987.654.321-00',
        'oab': '654321/RJ',
        'uf_oab': 'RJ',
        'email': 'maria.costa@exemplo.com',
        'telefone': '(21) 2222-3333',
        'celular': '(21) 98888-7777',
        'endereco': 'Av. Rio Branco, 456 - Centro',
        'cidade': 'Rio de Janeiro',
        'estado': 'RJ',
        'cep': '20040-007',
        'especialidades': 'Direito Penal, Direito Administrativo',
        'data_inscricao_oab': date(2018, 3, 20),
        'experiencia_anos': 5,
        'situacao': 'ativo',
        'ativo': True,
        'observacoes': 'Advogada especialista em direito penal e administrativo'
    }
    
    print("1. Testando criação de advogado...")
    sucesso, resultado = registrador.criar_advogado(dados_exemplo)
    
    if sucesso:
        print("✅ Advogado criado com sucesso!")
        print(f"   ID: {resultado['id']}")
        print(f"   Nome: {resultado['advogado'].nome}")
        print(f"   OAB: {resultado['advogado'].oab}")
        
        if resultado['correcoes']:
            print("   Correções aplicadas:")
            for correcao in resultado['correcoes']:
                print(f"     - {correcao}")
    else:
        print(f"❌ Erro ao criar advogado: {resultado}")
    
    print("\n2. Listando advogados cadastrados...")
    registrador.listar_advogados()
    
    print("\n3. Testando busca...")
    termo_busca = "Maria"
    advogado_encontrado = registrador.buscar_advogado(termo_busca)
    
    if advogado_encontrado:
        print(f"✅ Advogado encontrado: {advogado_encontrado.nome}")
    else:
        print(f"❌ Nenhum advogado encontrado para: {termo_busca}")
    
    print("\n4. Limpando dados de teste...")
    registrador.limpar_dados_teste()
    
    print("\n=== FIM DO SISTEMA ===")

if __name__ == '__main__':
    main()
