from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from associados.models import PreCadastroAssociado, Associado
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Testa a funcionalidade de pré-cadastro e conversão para associado'

    def handle(self, *args, **options):
        self.stdout.write('Testando funcionalidade de pré-cadastro...')
        
        # Verificar se existe um usuário admin
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                self.stdout.write(self.style.ERROR('Nenhum usuário admin encontrado. Crie um superusuário primeiro.'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao buscar usuário admin: {e}'))
            return
        
        # Criar um pré-cadastro de teste
        try:
            pre_cadastro = PreCadastroAssociado.objects.create(
                nome='João Silva Teste',
                cpf='123.456.789-00',
                rg='12.345.678-9',
                data_nascimento='1990-01-01',
                sexo='M',
                estado_civil='solteiro',
                email='joao.teste@email.com',
                telefone='(11) 1234-5678',
                celular='(11) 98765-4321',
                cep='01234-567',
                rua='Rua Teste',
                numero='123',
                bairro='Centro',
                cidade='São Paulo',
                estado='SP',
                tipo_profissao='bombeiro',
                posto_graduacao='soldado_bm',
                orgao='Corpo de Bombeiros',
                matricula='BM123456',
                status='pendente',
                observacoes='Pré-cadastro de teste criado pelo comando de gerenciamento'
            )
            
            self.stdout.write(self.style.SUCCESS(f'Pré-cadastro criado com sucesso: {pre_cadastro}'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao criar pré-cadastro: {e}'))
            return
        
        # Testar conversão para associado
        try:
            associado = pre_cadastro.converter_para_associado(admin_user)
            self.stdout.write(self.style.SUCCESS(f'Pré-cadastro convertido para associado com sucesso: {associado}'))
            
            # Verificar se o associado foi criado
            associado_criado = Associado.objects.filter(id=associado.id).first()
            if associado_criado:
                self.stdout.write(self.style.SUCCESS(f'Associado encontrado na base: {associado_criado.nome} - {associado_criado.cpf}'))
            else:
                self.stdout.write(self.style.ERROR('Associado não foi encontrado na base após a conversão'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erro ao converter pré-cadastro: {e}'))
            return
        
        # Verificar status do pré-cadastro
        pre_cadastro.refresh_from_db()
        self.stdout.write(f'Status do pré-cadastro após conversão: {pre_cadastro.get_status_display()}')
        
        # Limpar dados de teste
        try:
            associado.delete()
            pre_cadastro.delete()
            self.stdout.write(self.style.SUCCESS('Dados de teste removidos com sucesso'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Erro ao remover dados de teste: {e}'))
        
        self.stdout.write(self.style.SUCCESS('Teste concluído com sucesso!'))
