#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'abmepi.settings')
django.setup()

from django.test import RequestFactory
from core.views import InstitucionalConfigEditView
from core.models import InstitucionalConfig
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.contrib.messages.storage.fallback import FallbackStorage

User = get_user_model()

def test_form_submission():
    print("=== Teste de Envio do Formulário ===")
    
    # Obter configuração atual
    config_antes = InstitucionalConfig.get_config()
    print(f"Config ANTES - Telefone: {config_antes.telefone}")
    
    # Criar uma requisição fake POST
    factory = RequestFactory()
    
    # Dados do formulário - simular o que o usuário digitou
    form_data = {
        'titulo_principal': config_antes.titulo_principal,
        'subtitulo_hero': config_antes.subtitulo_hero,
        'titulo_sobre': config_antes.titulo_sobre,
        'texto_sobre_1': config_antes.texto_sobre_1,
        'texto_sobre_2': config_antes.texto_sobre_2,
        'texto_sobre_3': config_antes.texto_sobre_3,
        'titulo_cta': config_antes.titulo_cta,
        'texto_cta': config_antes.texto_cta,
        'telefone': '(85) 3456-7890',  # NOVO TELEFONE QUE O USUÁRIO DIGITOU
        'email': config_antes.email,
        'endereco': config_antes.endereco,
        'mostrar_estatisticas': config_antes.mostrar_estatisticas,
        'mostrar_servicos': config_antes.mostrar_servicos,
        'mostrar_sobre': config_antes.mostrar_sobre,
        'mostrar_cta': config_antes.mostrar_cta,
        'meta_description': config_antes.meta_description or '',
        'meta_keywords': config_antes.meta_keywords or '',
    }
    
    # Se há campos URL que podem estar vazios
    for field in ['facebook_url', 'instagram_url', 'linkedin_url', 'youtube_url']:
        value = getattr(config_antes, field)
        form_data[field] = value or ''
    
    request = factory.post('/editar/', data=form_data)
    
    # Criar um usuário fake para o teste
    user, created = User.objects.get_or_create(
        username='111.111.111-11',
        defaults={
            'first_name': 'Teste',
            'last_name': 'Usuário',
            'email': 'teste@teste.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # Simular usuário autenticado
    request.user = user
    
    # Simular sessão e messages
    request.session = {}
    setattr(request, '_messages', FallbackStorage(request))
    
    # Criar a view e processar
    view = InstitucionalConfigEditView()
    view.request = request
    view.object = config_antes
    
    try:
        # Simular o processo de POST
        form = view.get_form()
        
        print(f"Formulário criado com dados:")
        print(f"  - Telefone no form: {form.data.get('telefone')}")
        print(f"  - Formulário válido? {form.is_valid()}")
        
        if not form.is_valid():
            print(f"  - Erros: {form.errors}")
            return
        
        # Salvar
        response = view.form_valid(form)
        
        # Verificar se foi salvo
        config_depois = InstitucionalConfig.get_config()
        print(f"\nConfig DEPOIS - Telefone: {config_depois.telefone}")
        
        if config_depois.telefone == '(85) 3456-7890':
            print("✅ Telefone foi atualizado com sucesso!")
        else:
            print("❌ Telefone NÃO foi atualizado!")
            
        # Verificar mensagens
        messages = list(get_messages(request))
        if messages:
            print(f"Mensagens: {[str(m) for m in messages]}")
        
    except Exception as e:
        print(f"❌ Erro durante o processamento: {e}")
        import traceback
        traceback.print_exc()
    
    print("=== Fim do Teste ===")

if __name__ == '__main__':
    test_form_submission()
