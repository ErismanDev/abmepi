"""
Django settings for abmepi project.
"""

from pathlib import Path
import os
<<<<<<< HEAD
from decouple import config
=======
import dj_database_url
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
<<<<<<< HEAD
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')
=======
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070

# Application definition
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
<<<<<<< HEAD
    # 'tinymce',  # Comentado temporariamente para debug
=======
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
    
    # Local apps
    'core.apps.CoreConfig',
    'assejus.apps.AssejusConfig',
    'associados.apps.AssociadosConfig',
    'financeiro.apps.FinanceiroConfig',
    'administrativo.apps.AdministrativoConfig',
    'beneficios.apps.BeneficiosConfig',
    'psicologia.apps.PsicologiaConfig',
    'hotel_transito.apps.HotelTransitoConfig',
<<<<<<< HEAD
    'diretoria.apps.DiretoriaConfig',
=======
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
    'app.apps.AppConfig',
]

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

ROOT_URLCONF = 'abmepi.urls'

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
        },
    },
]

WSGI_APPLICATION = 'abmepi.wsgi.application'

# Database
<<<<<<< HEAD
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='abmepi'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='11322361'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
=======
# Configuração para DigitalOcean App Platform
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    # Fallback para configuração manual
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'abmepi'),
            'USER': os.getenv('DB_USER', 'postgres'),
            'PASSWORD': os.getenv('DB_PASSWORD', '11322361'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432'),
        }
    }
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    # Comentado para permitir senha padrão
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # Comentado temporariamente para permitir senha padrão numérica
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

# Internationalization
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Date and time formats
DATE_FORMAT = 'd/m/Y'
DATE_INPUT_FORMATS = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
DATETIME_FORMAT = 'd/m/Y H:i'
DATETIME_INPUT_FORMATS = ['%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M', '%Y-%m-%d %H:%M:%S.%f']
SHORT_DATE_FORMAT = 'd/m/Y'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# Custom user model
AUTH_USER_MODEL = 'core.Usuario'

# Configurações de usuário padrão
SENHA_PADRAO_USUARIO = 'Abmepi2024!'
SENHA_PADRAO_GERAR_AUTOMATICA = True   # Gerar senha automática única por usuário

# Login/Logout URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10MB

# Session settings
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'abmepi.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Create logs directory if it doesn't exist
os.makedirs(BASE_DIR / 'logs', exist_ok=True)

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
<<<<<<< HEAD
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'siteabmepi@gmail.com'
EMAIL_HOST_PASSWORD = 'tlvt twcz livv zetu'
DEFAULT_FROM_EMAIL = 'siteabmepi@gmail.com'
SERVER_EMAIL = 'siteabmepi@gmail.com'
=======
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'siteabmepi@gmail.com')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'tlvt twcz livv zetu')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'siteabmepi@gmail.com')
SERVER_EMAIL = os.getenv('SERVER_EMAIL', 'siteabmepi@gmail.com')
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070

# Configurações de fallback (comentadas - descomente se necessário)
# EMAIL_HOST = 'smtp.outlook.com'  # Outlook como alternativa
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'seu-email@outlook.com'
# EMAIL_HOST_PASSWORD = 'sua-senha'

# Email batch settings
EMAIL_BATCH_SIZE = 50  # Número de emails por lote
EMAIL_BATCH_DELAY = 2  # Delay entre lotes em segundos
EMAIL_DAILY_LIMIT = 400  # Limite diário conservador
EMAIL_FALLBACK_ENABLED = True  # Habilita fila de emails
ADMIN_EMAILS = ['siteabmepi@gmail.com']  # Emails dos administradores

<<<<<<< HEAD
# TinyMCE Configuration
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
=======
# Security settings for production
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_REDIRECT_EXEMPT = []
    SECURE_SSL_REDIRECT = os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('true', '1', 'yes')
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'True').lower() in ('true', '1', 'yes')
    CSRF_COOKIE_SECURE = os.getenv('CSRF_COOKIE_SECURE', 'True').lower() in ('true', '1', 'yes')
    X_FRAME_OPTIONS = 'DENY'

# Configurações específicas para DigitalOcean App Platform
if os.getenv('DIGITALOCEAN_APP_PLATFORM'):
    # Desabilitar SSL redirect se estiver atrás de um load balancer
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
>>>>>>> c00fe10f4bf493986d435556591fabb7aae9e070
