from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class PrimeiroAcessoMiddleware:
    """
    Middleware para verificar se o usuário precisa alterar a senha no primeiro acesso
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Lista de URLs que não precisam de verificação de primeiro acesso
        urls_excluidas = [
            '/logout/',
            '/primeiro-acesso/',
            '/admin/',
            '/djadmin/',
            '/static/',
            '/media/',
        ]
        
        # Verificar se o usuário está logado e se é primeiro acesso
        if (request.user.is_authenticated and 
            hasattr(request.user, 'primeiro_acesso') and
            request.user.primeiro_acesso and 
            not any(request.path.startswith(url) for url in urls_excluidas)):
            
            # Se é primeiro acesso e não está na página de primeiro acesso, redirecionar
            if request.path != '/primeiro-acesso/':
                messages.warning(
                    request, 
                    'Por segurança, você deve alterar sua senha padrão no primeiro acesso.'
                )
                return redirect('/primeiro-acesso/')
        
        response = self.get_response(request)
        return response
