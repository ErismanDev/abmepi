# ABMEPI - Sistema de Gestão para Associação de Bombeiros e Policiais Militares

Sistema web completo desenvolvido em Django para gerenciar associados, finanças, assessoria jurídica e atividades administrativas da associação.

## 🚀 Funcionalidades

### Módulo de Cadastro de Associados
- ✅ Cadastro completo com dados pessoais, endereço e funcionais
- ✅ Upload e exibição de fotos
- ✅ Anexação de documentos digitalizados
- ✅ Gestão de dependentes
- ✅ Controle de situação (ativo, reserva, reformado, pensionista)

### Módulo Financeiro
- ✅ Controle de mensalidades e taxas
- ✅ Geração de boletos (integração futura com PIX)
- ✅ Relatórios de inadimplência e receitas
- ✅ Histórico de pagamentos
- ✅ Controle de despesas

### Módulo ASSEJUS (Assessoria Jurídica)
- ✅ Cadastro de atendimentos jurídicos
- ✅ Classificação por tipo de demanda
- ✅ Controle de andamento e resultados
- ✅ Upload de documentos relacionados
- ✅ Consultas jurídicas

### Módulo Administrativo
- ✅ Gestão de eventos da associação
- ✅ Lista de presença e participantes
- ✅ Comunicados e circulares
- ✅ Controle de atividades

### Módulo de Benefícios e Convênios
- ✅ Cadastro de empresas parceiras
- ✅ Gestão de convênios e descontos
- ✅ Registro de benefícios utilizados
- ✅ Relatórios de utilização

## 🛠️ Tecnologias Utilizadas

- **Backend**: Django 5.0+
- **Banco de Dados**: PostgreSQL
- **Frontend**: Bootstrap 5 + FontAwesome
- **Autenticação**: Sistema nativo Django com login por CPF
- **Uploads**: django-storages para arquivos e imagens
- **Relatórios**: ReportLab (PDF) + OpenPyXL (Excel)
- **API**: Django REST Framework

## 📋 Pré-requisitos

- Python 3.8+
- PostgreSQL 12+
- pip (gerenciador de pacotes Python)

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd abmepi
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados PostgreSQL
```sql
CREATE DATABASE abmepi_db;
CREATE USER abmepi_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE abmepi_db TO abmepi_user;
```

### 5. Configure as variáveis de ambiente
Copie o arquivo `env.example` para `.env` e configure:
```bash
cp env.example .env
```

Edite o arquivo `.env` com suas configurações:
```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=abmepi_db
DB_USER=abmepi_user
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
```

### 6. Execute as migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crie um superusuário
```bash
python manage.py createsuperuser
```

### 8. Execute o servidor
```bash
python manage.py runserver
```

Acesse o sistema em: http://localhost:8000

## 🏗️ Estrutura do Projeto

```
abmepi/
├── abmepi/                 # Configurações principais
│   ├── settings.py        # Configurações do Django
│   ├── urls.py           # URLs principais
│   └── wsgi.py           # Configuração WSGI
├── core/                  # Módulo central
│   ├── models.py         # Usuários e configurações
│   ├── views.py          # Views principais
│   └── forms.py          # Formulários de autenticação
├── associados/            # Gestão de associados
│   ├── models.py         # Modelos de associados
│   ├── views.py          # Views de associados
│   └── admin.py          # Interface administrativa
├── financeiro/            # Gestão financeira
│   ├── models.py         # Modelos financeiros
│   ├── views.py          # Views financeiras
│   └── admin.py          # Interface administrativa
├── assejus/              # Assessoria jurídica
│   ├── models.py         # Modelos jurídicos
│   ├── views.py          # Views jurídicas
│   └── admin.py          # Interface administrativa
├── administrativo/        # Gestão administrativa
│   ├── models.py         # Modelos administrativos
│   ├── views.py          # Views administrativas
│   └── admin.py          # Interface administrativa
├── beneficios/            # Benefícios e convênios
│   ├── models.py         # Modelos de benefícios
│   ├── views.py          # Views de benefícios
│   └── admin.py          # Interface administrativa
├── templates/             # Templates HTML
│   ├── base.html         # Template base
│   └── core/             # Templates do módulo core
├── static/                # Arquivos estáticos
├── media/                 # Uploads de arquivos
├── requirements.txt       # Dependências Python
└── README.md             # Este arquivo
```

## 👥 Grupos de Usuários

O sistema possui 4 tipos de usuários com diferentes permissões:

1. **Administrador**: Acesso total ao sistema
2. **Associado**: Acesso limitado ao próprio perfil e benefícios
3. **Financeiro**: Acesso aos módulos financeiros
4. **Jurídico**: Acesso aos módulos jurídicos

## 🔐 Autenticação

- **Login**: Utiliza CPF como username
- **Senha**: Senha personalizada para cada usuário
- **Sessões**: Configuradas para expirar em 1 hora
- **Logs**: Todas as atividades são registradas para auditoria

## 📊 Relatórios

O sistema gera relatórios em:
- **PDF**: Utilizando ReportLab
- **Excel**: Utilizando OpenPyXL
- **Formato**: Personalizáveis por módulo

## 🎨 Interface

- **Design**: Responsivo com Bootstrap 5
- **Ícones**: FontAwesome para melhor experiência visual
- **Cores**: Tema azul militar profissional
- **Layout**: Sidebar colapsável para melhor organização

## 🚀 Deploy

### Produção
Para deploy em produção:

1. Configure `DEBUG=False` no `.env`
2. Configure um servidor web (Nginx/Apache)
3. Configure um servidor WSGI (Gunicorn/uWSGI)
4. Configure HTTPS
5. Configure backup automático do banco

### Docker (Futuro)
```bash
# Comando para build da imagem (quando implementado)
docker build -t abmepi .
docker run -p 8000:8000 abmepi
```

## 📝 Licença

Este projeto é desenvolvido para uso interno da ABMEPI.

## 🤝 Contribuição

Para contribuir com o projeto:

1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📞 Suporte

Para suporte técnico ou dúvidas:
- Entre em contato com a equipe de desenvolvimento
- Consulte a documentação técnica
- Verifique os logs do sistema

## 🔄 Atualizações

### Versão 1.0.0
- ✅ Sistema base completo
- ✅ Módulos principais implementados
- ✅ Interface responsiva
- ✅ Autenticação por CPF
- ✅ Controle de permissões

### Próximas Versões
- 🔄 Integração com PIX para pagamentos
- 🔄 API REST completa
- 🔄 Notificações por email/SMS
- 🔄 Dashboard avançado com mais gráficos
- 🔄 Sistema de backup automático

## 📚 Documentação Adicional

- [Manual do Usuário](docs/manual-usuario.md)
- [Manual Técnico](docs/manual-tecnico.md)
- [API Documentation](docs/api.md)
- [Deploy Guide](docs/deploy.md)

---

**Desenvolvido com ❤️ para a ABMEPI**
