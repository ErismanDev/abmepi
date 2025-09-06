from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from assejus.models import Advogado
from core.models import Usuario


class Command(BaseCommand):
    help = 'Cria usuários do sistema para advogados que ainda não possuem usuário'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa sem fazer alterações no banco de dados',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a criação mesmo para advogados que já possuem usuário',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando criação de usuários para advogados...')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('🔍 MODO DRY-RUN: Nenhuma alteração será feita no banco de dados')
            )
        
        # Buscar advogados
        if force:
            advogados = Advogado.objects.all()
            self.stdout.write('🔍 Verificando todos os advogados (modo force)...')
        else:
            advogados = Advogado.objects.filter(user__isnull=True)
            self.stdout.write('🔍 Verificando advogados sem usuário...')
        
        total_advogados = advogados.count()
        self.stdout.write(f'📊 Total de advogados encontrados: {total_advogados}')
        
        if total_advogados == 0:
            self.stdout.write(
                self.style.SUCCESS('✅ Todos os advogados já possuem usuário do sistema!')
            )
            return
        
        # Contadores
        criados = 0
        erros = 0
        ja_existem = 0
        
        for advogado in advogados:
            try:
                if advogado.user and not force:
                    self.stdout.write(f'ℹ️  Advogado {advogado.nome} já possui usuário')
                    ja_existem += 1
                    continue
                
                if advogado.user and force:
                    # Remover usuário existente se estiver no modo force
                    self.stdout.write(f'🔄 Removendo usuário existente para {advogado.nome}...')
                    if not dry_run:
                        advogado.user.delete()
                        advogado.user = None
                        advogado.save(update_fields=['user'])
                
                # Gerar senha padrão fixa
                senha_padrao = "12345678"
                
                if not dry_run:
                    # Criar usuário
                    usuario = Usuario.objects.create(
                        username=advogado.cpf,
                        first_name=advogado.nome.split()[0] if advogado.nome else '',
                        last_name=' '.join(advogado.nome.split()[1:]) if len(advogado.nome.split()) > 1 else '',
                        email=advogado.email,
                        password=make_password(senha_padrao),
                        tipo_usuario='advogado',
                        ativo=advogado.ativo,
                        primeiro_acesso=True
                    )
                    
                    # Associar usuário ao advogado
                    advogado.user = usuario
                    advogado.save(update_fields=['user'])
                    
                    criados += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ Usuário criado para {advogado.nome} - '
                            f'Username: {usuario.username}, Senha: {senha_padrao}'
                        )
                    )
                else:
                    # Modo dry-run
                    criados += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'🔍 DRY-RUN: Usuário seria criado para {advogado.nome} - '
                            f'Username: {advogado.cpf}, Senha: {senha_padrao}'
                        )
                    )
                    
            except Exception as e:
                erros += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Erro ao criar usuário para {advogado.nome}: {e}'
                    )
                )
        
        # Resumo final
        self.stdout.write('\n' + '='*50)
        self.stdout.write('📊 RESUMO DA EXECUÇÃO')
        self.stdout.write('='*50)
        
        if dry_run:
            self.stdout.write(f'🔍 DRY-RUN: {criados} usuários seriam criados')
        else:
            self.stdout.write(f'✅ Usuários criados com sucesso: {criados}')
        
        if ja_existem > 0:
            self.stdout.write(f'ℹ️  Advogados que já possuem usuário: {ja_existem}')
        
        if erros > 0:
            self.stdout.write(f'❌ Erros encontrados: {erros}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Processo concluído! Total processado: {total_advogados}'
            )
        )
        
        if not dry_run and criados > 0:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  IMPORTANTE: Informe aos advogados suas credenciais de acesso!'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '📋 Usuário: CPF do advogado'
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    '🔑 Senha: Últimos 4 dígitos do CPF'
                )
            )
