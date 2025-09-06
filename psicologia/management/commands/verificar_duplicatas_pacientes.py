from django.core.management.base import BaseCommand
from django.db import transaction
from psicologia.models import Paciente
from associados.models import Associado
from collections import defaultdict


class Command(BaseCommand):
    help = 'Verifica e limpa duplicatas de pacientes no sistema'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Corrigir automaticamente as duplicatas encontradas',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostrar o que seria feito, sem executar',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Verificando duplicatas de pacientes...'))
        
        # Encontrar duplicatas baseadas no associado
        associados_duplicados = defaultdict(list)
        
        for paciente in Paciente.objects.all():
            associados_duplicados[paciente.associado_id].append(paciente)
        
        duplicatas_encontradas = {
            associado_id: pacientes 
            for associado_id, pacientes in associados_duplicados.items() 
            if len(pacientes) > 1
        }
        
        if not duplicatas_encontradas:
            self.stdout.write(self.style.SUCCESS('Nenhuma duplicata encontrada!'))
            return
        
        self.stdout.write(
            self.style.WARNING(
                f'Encontradas {len(duplicatas_encontradas)} duplicatas de pacientes:'
            )
        )
        
        for associado_id, pacientes in duplicatas_encontradas.items():
            try:
                associado = Associado.objects.get(id=associado_id)
                self.stdout.write(f'\nAssociado: {associado.nome} (ID: {associado_id})')
                self.stdout.write(f'Pacientes encontrados: {len(pacientes)}')
                
                for i, paciente in enumerate(pacientes, 1):
                    self.stdout.write(
                        f'  {i}. ID: {paciente.id}, '
                        f'Psicólogo: {paciente.psicologo_responsavel.nome_completo if paciente.psicologo_responsavel else "Nenhum"}, '
                        f'Ativo: {paciente.ativo}, '
                        f'Data Cadastro: {paciente.data_cadastro}'
                    )
                
                if options['fix'] and not options['dry_run']:
                    self.corrigir_duplicatas(associado, pacientes)
                elif options['dry_run']:
                    self.stdout.write('  [DRY RUN] Seria corrigido automaticamente')
                    
            except Associado.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Associado com ID {associado_id} não encontrado!')
                )
        
        if options['fix'] and not options['dry_run']:
            self.stdout.write(self.style.SUCCESS('\nDuplicatas corrigidas com sucesso!'))
        elif options['dry_run']:
            self.stdout.write(
                self.style.WARNING('\nUse --fix para corrigir as duplicatas automaticamente')
            )
    
    def corrigir_duplicatas(self, associado, pacientes):
        """Corrige duplicatas mantendo apenas o paciente mais antigo e ativo"""
        with transaction.atomic():
            # Ordenar por data de cadastro (mais antigo primeiro) e status ativo
            pacientes_ordenados = sorted(
                pacientes, 
                key=lambda p: (not p.ativo, p.data_cadastro)
            )
            
            # Manter o primeiro (mais antigo e ativo)
            paciente_principal = pacientes_ordenados[0]
            pacientes_para_remover = pacientes_ordenados[1:]
            
            self.stdout.write(f'  Mantendo paciente ID: {paciente_principal.id}')
            
            # Remover os outros
            for paciente in pacientes_para_remover:
                self.stdout.write(f'  Removendo paciente ID: {paciente.id}')
                paciente.delete()
            
            self.stdout.write(
                self.style.SUCCESS(f'  ✓ Duplicatas corrigidas para {associado.nome}')
            )
