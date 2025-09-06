"""
URL configuration for abmepi project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import DashboardView, login_view, InstitucionalView, logout_view, primeiro_acesso_view
from django.views.generic import RedirectView

urlpatterns = [
    # Página institucional como página inicial
    path('', InstitucionalView.as_view(), name='institucional'),
    # Dashboard principal (requer login)
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    # Mover admin do Django para evitar conflito visual/semântico
    path('djadmin/', admin.site.urls),
    # Redirecionar /admin/ para o módulo administrativo customizado
    path('admin/', RedirectView.as_view(url='/administrativo/', permanent=False)),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('primeiro-acesso/', primeiro_acesso_view, name='primeiro_acesso'),
    
    # URLs para modais e notificações (acessíveis diretamente)
    # path('marcar-modal-como-exibido/', marcar_modal_como_exibido, name='marcar_modal_como_exibido'),
    # path('limpar-notificacoes-sessao/', limpar_notificacoes_sessao, name='limpar_notificacoes_sessao'),
    
    path('core/', include('core.urls')),
    path('associados/', include('associados.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('assejus/', include('assejus.urls')),
    path('administrativo/', include('administrativo.urls')),
    path('beneficios/', include('beneficios.urls')),
    path('psicologia/', include('psicologia.urls')),
    path('hotel-transito/', include('hotel_transito.urls')),
    path('diretoria/', include('diretoria.urls')),
    path('app/', include('app.urls')),
    # path('tinymce/', include('tinymce.urls')),  # Comentado temporariamente
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Servir arquivos estáticos dos apps em modo DEBUG
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    
    # Adicionar URLs específicas para arquivos estáticos dos apps
    from django.views.static import serve
    from django.urls import re_path
    
    # URLs para arquivos estáticos dos apps
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
        }),
    ]
