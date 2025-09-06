#!/usr/bin/env python
"""
Script interativo para registro de advogados
Interface de linha de comando para facilitar o cadastro
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

class InterfaceRegistroAdvogado:
    """Interface interativa para registro de advogados"""
    
    def __init__(self):
        self.registrador = RegistradorAdvogados()
    
    def exibir_menu_principal(self):
        """Exibe o menu principal"""
        while True:
            print("\n" + "="*60)
            print("           SISTEMA DE REGISTRO DE ADVOGADOS")
            print("="*60)
            print("1. Cadastrar novo advogado")
            print("2. Listar advogados cadastrados")
            print("3. Buscar advogado")
            print("4. Editar advogado")
            print("5. Excluir advogado")
            print("6. Sair")
            print("="*60)
            
            opcao = input("Escolha uma opção (1-6): ").strip()
            
            if opcao == '1':
                self.cadastrar_advogado()
            elif opcao == '2':
                self.listar_advogados()
            elif opcao == '3':
                self.buscar_advogado()
            elif opcao == '4':
                self.editar_advogado()
            elif opcao == '5':
                self.excluir_advogado()
            elif opcao == '6':
                print("Saindo do sistema...")
                break
            else:
                print("❌ Opção inválida! Tente novamente.")
    
    def cadastrar_advogado(self):
        """Interface para cadastro de novo advogado"""
        print("\n" + "="*50)
        print("           CADASTRO DE NOVO ADVOGADO")
        print("="*50)
        
        dados = {}
        
        # Nome
        while True:
            nome = input("Nome completo: ").strip()
            if len(nome) >= 3:
                dados['nome'] = nome
                break
            else:
                print("❌ Nome deve ter pelo menos 3 caracteres.")
        
        # CPF
        while True:
            cpf = input("CPF (XXX.XXX.XXX-XX): ").strip()
            if self.registrador.validar_cpf(cpf):
                dados['cpf'] = cpf
                break
            else:
                print("❌ CPF inválido! Use o formato XXX.XXX.XXX-XX")
                print("   Exemplo: 123.456.789-00")
        
        # OAB
        while True:
            oab = input("OAB (número/UF): ").strip()
            if self.registrador.validar_oab(oab):
                dados['oab'] = oab
                dados['uf_oab'] = oab.split('/')[1]
                break
            else:
                print("❌ Formato de OAB inválido! Use: número/UF (ex: 123456/SP)")
        
        # Email
        while True:
            email = input("Email: ").strip()
            if '@' in email and '.' in email:
                dados['email'] = email
                break
            else:
                print("❌ Email inválido!")
        
        # Telefone
        while True:
            telefone = input("Telefone ((XX) XXXX-XXXX): ").strip()
            if self.registrador.validar_telefone(telefone):
                dados['telefone'] = telefone
                break
            else:
                print("❌ Telefone inválido!")
        
        # Celular (opcional)
        celular = input("Celular ((XX) XXXXX-XXXX) - Enter para pular: ").strip()
        if celular:
            dados['celular'] = celular
        
        # Endereço
        while True:
            endereco = input("Endereço completo: ").strip()
            if len(endereco) >= 10:
                dados['endereco'] = endereco
                break
            else:
                print("❌ Endereço deve ter pelo menos 10 caracteres.")
        
        # Cidade
        while True:
            cidade = input("Cidade: ").strip()
            if len(cidade) >= 2:
                dados['cidade'] = cidade
                break
            else:
                print("❌ Cidade deve ter pelo menos 2 caracteres.")
        
        # Estado
        print("\nEstados disponíveis:")
        estados = ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO']
        for i, estado in enumerate(estados, 1):
            print(f"{i:2d}. {estado}", end="  ")
            if i % 5 == 0:
                print()
        
        while True:
            try:
                opcao = int(input(f"\nEscolha o estado (1-{len(estados)}): "))
                if 1 <= opcao <= len(estados):
                    dados['estado'] = estados[opcao - 1]
                    break
                else:
                    print("❌ Opção inválida!")
            except ValueError:
                print("❌ Digite um número válido!")
        
        # CEP
        while True:
            cep = input("CEP (XXXXX-XXX): ").strip()
            if self.registrador.validar_cep(cep):
                dados['cep'] = cep
                break
            else:
                print("❌ CEP inválido! Use o formato XXXXX-XXX")
        
        # Especialidades
        especialidades = input("Especialidades (separadas por vírgula) - Enter para pular: ").strip()
        if especialidades:
            dados['especialidades'] = especialidades
        
        # Data de inscrição na OAB
        while True:
            try:
                data_str = input("Data de inscrição na OAB (DD/MM/AAAA): ").strip()
                dia, mes, ano = map(int, data_str.split('/'))
                dados['data_inscricao_oab'] = date(ano, mes, dia)
                break
            except (ValueError, IndexError):
                print("❌ Data inválida! Use o formato DD/MM/AAAA")
        
        # Anos de experiência
        while True:
            try:
                experiencia = int(input("Anos de experiência: "))
                if 0 <= experiencia <= 100:
                    dados['experiencia_anos'] = experiencia
                    break
                else:
                    print("❌ Anos de experiência deve ser entre 0 e 100")
            except ValueError:
                print("❌ Digite um número válido!")
        
        # Situação
        print("\nSituações disponíveis:")
        situacoes = [
            ('ativo', 'Ativo'),
            ('inativo', 'Inativo'),
            ('suspenso', 'Suspenso'),
            ('aposentado', 'Aposentado')
        ]
        for i, (valor, descricao) in enumerate(situacoes, 1):
            print(f"{i}. {descricao}")
        
        while True:
            try:
                opcao = int(input(f"Escolha a situação (1-{len(situacoes)}): "))
                if 1 <= opcao <= len(situacoes):
                    dados['situacao'] = situacoes[opcao - 1][0]
                    break
                else:
                    print("❌ Opção inválida!")
            except ValueError:
                print("❌ Digite um número válido!")
        
        # Ativo
        ativo = input("Advogado está ativo? (s/n): ").strip().lower()
        dados['ativo'] = ativo in ['s', 'sim', 'y', 'yes']
        
        # Observações
        observacoes = input("Observações adicionais - Enter para pular: ").strip()
        if observacoes:
            dados['observacoes'] = observacoes
        
        # Confirmar dados
        print("\n" + "="*50)
        print("           DADOS PARA CONFIRMAÇÃO")
        print("="*50)
        
        for campo, valor in dados.items():
            if campo == 'data_inscricao_oab':
                print(f"{campo.replace('_', ' ').title()}: {valor.strftime('%d/%m/%Y')}")
            elif campo == 'ativo':
                print(f"{campo.replace('_', ' ').title()}: {'Sim' if valor else 'Não'}")
            else:
                print(f"{campo.replace('_', ' ').title()}: {valor}")
        
        confirmar = input("\nConfirmar cadastro? (s/n): ").strip().lower()
        
        if confirmar in ['s', 'sim', 'y', 'yes']:
            sucesso, resultado = self.registrador.criar_advogado(dados)
            
            if sucesso:
                print("✅ Advogado cadastrado com sucesso!")
                print(f"   ID: {resultado['id']}")
                print(f"   Nome: {resultado['advogado'].nome}")
                print(f"   OAB: {resultado['advogado'].oab}")
                
                if resultado['correcoes']:
                    print("   Correções aplicadas:")
                    for correcao in resultado['correcoes']:
                        print(f"     - {correcao}")
            else:
                print(f"❌ Erro ao cadastrar: {resultado}")
        else:
            print("❌ Cadastro cancelado.")
    
    def listar_advogados(self):
        """Lista todos os advogados"""
        self.registrador.listar_advogados()
        input("\nPressione Enter para continuar...")
    
    def buscar_advogado(self):
        """Busca um advogado específico"""
        print("\n" + "="*50)
        print("           BUSCA DE ADVOGADO")
        print("="*50)
        
        termo = input("Digite o nome, CPF ou OAB: ").strip()
        
        if termo:
            advogado = self.registrador.buscar_advogado(termo)
            
            if advogado:
                print(f"\n✅ Advogado encontrado:")
                print(f"   ID: {advogado.id}")
                print(f"   Nome: {advogado.nome}")
                print(f"   CPF: {self.registrador.formatar_cpf(advogado.cpf)}")
                print(f"   OAB: {advogado.oab}")
                print(f"   Email: {advogado.email}")
                print(f"   Telefone: {advogado.telefone}")
                print(f"   Cidade: {advogado.cidade}/{advogado.estado}")
                print(f"   Situação: {advogado.situacao}")
                print(f"   Especialidades: {advogado.especialidades or 'Não informado'}")
            else:
                print(f"❌ Nenhum advogado encontrado para: {termo}")
        else:
            print("❌ Termo de busca não pode estar vazio.")
        
        input("\nPressione Enter para continuar...")
    
    def editar_advogado(self):
        """Interface para edição de advogado"""
        print("\n" + "="*50)
        print("           EDIÇÃO DE ADVOGADO")
        print("="*50)
        
        termo = input("Digite o nome, CPF ou OAB do advogado: ").strip()
        
        if termo:
            advogado = self.registrador.buscar_advogado(termo)
            
            if advogado:
                print(f"\nEditando advogado: {advogado.nome}")
                # Aqui você pode implementar a lógica de edição
                print("⚠️  Funcionalidade de edição será implementada em breve.")
            else:
                print(f"❌ Nenhum advogado encontrado para: {termo}")
        else:
            print("❌ Termo de busca não pode estar vazio.")
        
        input("\nPressione Enter para continuar...")
    
    def excluir_advogado(self):
        """Interface para exclusão de advogado"""
        print("\n" + "="*50)
        print("           EXCLUSÃO DE ADVOGADO")
        print("="*50)
        
        termo = input("Digite o nome, CPF ou OAB do advogado: ").strip()
        
        if termo:
            advogado = self.registrador.buscar_advogado(termo)
            
            if advogado:
                print(f"\nAdvogado encontrado: {advogado.nome}")
                confirmar = input("Tem certeza que deseja excluir? (s/n): ").strip().lower()
                
                if confirmar in ['s', 'sim', 'y', 'yes']:
                    try:
                        nome = advogado.nome
                        advogado.delete()
                        print(f"✅ Advogado {nome} excluído com sucesso!")
                    except Exception as e:
                        print(f"❌ Erro ao excluir: {e}")
                else:
                    print("❌ Exclusão cancelada.")
            else:
                print(f"❌ Nenhum advogado encontrado para: {termo}")
        else:
            print("❌ Termo de busca não pode estar vazio.")
        
        input("\nPressione Enter para continuar...")

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
        
        if advogados.count() == 0:
            print("Nenhum advogado cadastrado.")
            return
        
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

def main():
    """Função principal"""
    print("Iniciando Sistema de Registro de Advogados...")
    
    try:
        interface = InterfaceRegistroAdvogado()
        interface.exibir_menu_principal()
    except KeyboardInterrupt:
        print("\n\nSistema interrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro inesperado: {e}")
    
    print("Sistema finalizado.")

if __name__ == '__main__':
    main()
