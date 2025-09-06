from django.db import migrations


def convert_tipo_usuario(apps, schema_editor):
    """
    Converte os tipos de usuário antigos para os novos tipos
    """
    Usuario = apps.get_model('core', 'Usuario')
    
    # Mapeamento dos tipos antigos para os novos
    tipo_mapping = {
        'administrador': 'administrador_sistema',
        'financeiro': 'atendente_geral',
        'juridico': 'advogado',
    }
    
    # Atualizar usuários existentes
    for usuario in Usuario.objects.all():
        if usuario.tipo_usuario in tipo_mapping:
            usuario.tipo_usuario = tipo_mapping[usuario.tipo_usuario]
            usuario.save()


def reverse_convert_tipo_usuario(apps, schema_editor):
    """
    Reverte a conversão dos tipos de usuário
    """
    Usuario = apps.get_model('core', 'Usuario')
    
    # Mapeamento reverso
    tipo_mapping_reverse = {
        'administrador_sistema': 'administrador',
        'atendente_geral': 'financeiro',
        'advogado': 'juridico',
    }
    
    # Reverter usuários
    for usuario in Usuario.objects.all():
        if usuario.tipo_usuario in tipo_mapping_reverse:
            usuario.tipo_usuario = tipo_mapping_reverse[usuario.tipo_usuario]
            usuario.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(convert_tipo_usuario, reverse_convert_tipo_usuario),
    ]
