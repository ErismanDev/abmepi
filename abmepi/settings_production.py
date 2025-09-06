"""
Configurações de produção para o projeto ABMEPI.
"""

from .settings import *
import os
from pathlib import Path

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

# Configuração de hosts permitidos para produção
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '.digitalocean.com',
    '.ondigitalocean.app',
    # Adicione seu domínio aqui quando configurar
    # 'seu-dominio.com',
    # 'www.seu-dominio.com',
]

# Configurações de banco de dados para produção
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'abmepi_prod'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Configurações de arquivos estáticos para produção
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Configurações de arquivos de mídia para produção
MEDIA_ROOT = BASE_DIR / 'media'

# Configurações de segurança
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Configurações de HTTPS (descomente quando configurar SSL)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# Configurações de email para produção
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@abmepi.org.br')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', 'noreply@abmepi.org.br')

# Configurações de logging para produção
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'abmepi_production.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
        'abmepi': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Configurações de cache para produção (usando Redis se disponível)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Configurações de sessão para produção
SESSION_COOKIE_AGE = 3600  # 1 hora
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SAVE_EVERY_REQUEST = True

# Configurações de upload de arquivos
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
FILE_UPLOAD_PERMISSIONS = 0o644

# Configurações de email em lote para produção
EMAIL_BATCH_SIZE = 100
EMAIL_BATCH_DELAY = 1
EMAIL_DAILY_LIMIT = 1000
EMAIL_FALLBACK_ENABLED = True

# Configurações de administradores
ADMINS = [
    ('Admin ABMEPI', os.environ.get('ADMIN_EMAIL', 'admin@abmepi.org.br')),
]

# Configurações de managers
MANAGERS = ADMINS

# Configurações de servidor de arquivos estáticos
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# Configurações de internacionalização para produção
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Configurações de timezone
TIME_ZONE = 'America/Sao_Paulo'

# Configurações de idioma
LANGUAGE_CODE = 'pt-br'

# Configurações de formato de data
DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

# Configurações de middleware para produção
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.PrimeiroAcessoMiddleware',
]

# Configurações de aplicações instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party apps
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_filters',
    'django_tables2',
    'django_bootstrap5',
    'django_extensions',
    'tinymce',
    
    # Local apps
    'core.apps.CoreConfig',
    'assejus.apps.AssejusConfig',
    'associados.apps.AssociadosConfig',
    'financeiro.apps.FinanceiroConfig',
    'administrativo.apps.AdministrativoConfig',
    'beneficios.apps.BeneficiosConfig',
    'psicologia.apps.PsicologiaConfig',
    'hotel_transito.apps.HotelTransitoConfig',
    'diretoria.apps.DiretoriaConfig',
    'app.apps.AppConfig',
]

# Configurações de templates para produção
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.notificacoes_context',
            ],
            'debug': False,  # Desabilitado em produção
        },
    },
]

# Configurações de validação de senha para produção
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Configurações de usuário personalizado
AUTH_USER_MODEL = 'core.Usuario'

# Configurações de senha padrão para produção
SENHA_PADRAO_USUARIO = os.environ.get('SENHA_PADRAO_USUARIO', 'Abmepi2024!')
SENHA_PADRAO_GERAR_AUTOMATICA = True

# Configurações de URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# Configurações de mensagens
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Configurações do Django REST Framework para produção
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Configurações do Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Configurações do TinyMCE para produção
TINYMCE_DEFAULT_CONFIG = {
    'height': 400,
    'width': '100%',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'silver',
    'plugins': [
        'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
        'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
        'insertdatetime', 'media', 'table', 'help', 'wordcount', 'emoticons',
        'template', 'codesample', 'hr', 'pagebreak', 'nonbreaking', 'toc',
        'imagetools', 'textpattern', 'noneditable', 'quickbars', 'accordion'
    ],
    'toolbar': 'undo redo | blocks | ' +
               'bold italic backcolor | alignleft aligncenter ' +
               'alignright alignjustify | bullist numlist outdent indent | ' +
               'removeformat | help | table | image | link | code | fullscreen | ' +
               'emoticons | template | codesample | hr | pagebreak | toc',
    'content_style': 'body { font-family: -apple-system, BlinkMacSystemFont, San Francisco, Segoe UI, Roboto, Helvetica Neue, sans-serif; font-size: 14px; }',
    'menubar': 'file edit view insert format tools table help',
    'toolbar_mode': 'sliding',
    'contextmenu': 'formats | link image',
    'branding': False,
    'resize': 'both',
    'statusbar': True,
    'elementpath': True,
    'paste_data_images': True,
    'paste_as_text': False,
    'paste_auto_cleanup_on_paste': True,
    'paste_remove_styles': True,
    'paste_remove_styles_if_webkit': True,
    'paste_merge_formats': True,
    'paste_convert_word_fake_lists': True,
    'paste_enable_default_filters': True,
    'templates': [
        {
            'title': 'Ata de Reunião - Estrutura Básica',
            'description': 'Template básico para atas de reunião',
            'content': '''
                <h2>ATA DE REUNIÃO</h2>
                <p><strong>Tipo:</strong> [Tipo da Reunião]</p>
                <p><strong>Data:</strong> [Data e Hora]</p>
                <p><strong>Local:</strong> [Local da Reunião]</p>
                <p><strong>Presidente:</strong> [Nome do Presidente]</p>
                <p><strong>Secretário:</strong> [Nome do Secretário]</p>
                
                <h3>PRESENTES:</h3>
                <ul>
                    <li>[Lista de membros presentes]</li>
                </ul>
                
                <h3>AUSENTES:</h3>
                <ul>
                    <li>[Lista de membros ausentes]</li>
                </ul>
                
                <h3>PAUTA:</h3>
                <ol>
                    <li>[Item 1]</li>
                    <li>[Item 2]</li>
                    <li>[Item 3]</li>
                </ol>
                
                <h3>DELIBERAÇÕES:</h3>
                <p>[Decisões tomadas na reunião]</p>
                
                <h3>OBSERVAÇÕES:</h3>
                <p>[Observações adicionais]</p>
                
                <p><em>Esta ata foi aprovada pelos presentes.</em></p>
            '''
        }
    ],
    'quickbars_selection_toolbar': 'bold italic | quicklink h2 h3 blockquote quickimage quicktable',
    'quickbars_insert_toolbar': 'quickimage quicktable',
    'file_picker_callback': 'function (callback, value, meta) { /* Implementar se necessário */ }',
    'setup': 'function (editor) { editor.on("change", function () { editor.save(); }); }'
}

# Criar diretório de logs se não existir
os.makedirs(BASE_DIR / 'logs', exist_ok=True)
