from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class AssejusAdminSite(AdminSite):
    """Site admin personalizado para o ASSEJUS"""
    
    site_header = _('Administração ASSEJUS')
    site_title = _('Portal ASSEJUS')
    index_title = _('Bem-vindo ao Portal de Administração ASSEJUS')
    
    # Configurações de permissões
    def has_permission(self, request):
        """Verifica se o usuário tem permissão para acessar o admin"""
        return request.user.is_active and request.user.is_staff
    
    # Personalização do menu
    def get_app_list(self, request):
        """Personaliza a lista de aplicativos no admin"""
        app_list = super().get_app_list(request)
        
        # Reorganiza os aplicativos para dar destaque ao ASSEJUS
        for app in app_list:
            if app['app_label'] == 'assejus':
                app['name'] = 'Assessoria Jurídica'
                app['models'].sort(key=lambda x: x['name'])
        
        return app_list


# Instância personalizada do admin site
assejus_admin_site = AssejusAdminSite(name='assejus_admin')
