# Módulo de Benefícios - ABMEPI

## Visão Geral

O módulo de Benefícios é responsável por gerenciar convênios, empresas parceiras e benefícios oferecidos aos associados da ABMEPI. Este sistema permite o cadastro de empresas parceiras, criação de convênios com diferentes categorias e controle de benefícios solicitados pelos associados.

## Funcionalidades Principais

### 1. Empresas Parceiras
- **Cadastro completo**: Nome, CNPJ, razão social, endereço, contatos
- **Gestão de status**: Ativa/Inativa
- **Filtros e busca**: Por estado, cidade, nome ou razão social
- **Histórico**: Data de cadastro e atualização

### 2. Convênios
- **Categorias**: Saúde, Educação, Lazer, Comércio, Serviços, Outros
- **Status**: Ativo, Inativo, Pendente, Expirado
- **Período de validade**: Data de início e fim
- **Descontos e condições**: Descrição detalhada dos benefícios
- **Documentos necessários**: Lista de documentos para utilização
- **Arquivos anexados**: Suporte a documentos e materiais

### 3. Benefícios
- **Solicitação**: Associados podem solicitar benefícios
- **Status de aprovação**: Pendente, Aprovado, Rejeitado, Utilizado, Cancelado
- **Controle de valores**: Valor do benefício e desconto aplicado
- **Comprovantes**: Upload de documentos comprobatórios
- **Aprovação**: Sistema de aprovação por usuários autorizados

### 4. Categorias de Benefícios
- **Organização**: Categorias personalizáveis com ícones e cores
- **Ordem de exibição**: Controle da apresentação visual
- **Status ativo/inativo**: Controle de visibilidade

### 5. Relatórios
- **Geração automática**: Relatórios por categoria, associado, empresa
- **Períodos personalizáveis**: Filtros por data
- **Arquivos exportáveis**: Suporte a diferentes formatos

## Estrutura do Sistema

### Modelos (Models)

#### EmpresaParceira
- Informações básicas da empresa
- Endereço completo
- Contatos principais e secundários
- Status ativo/inativo

#### Convenio
- Vinculação com empresa parceira
- Categoria e status
- Período de validade
- Descontos e condições
- Documentos necessários

#### Beneficio
- Vinculação com associado e convênio
- Status de aprovação
- Valores e descontos
- Comprovantes
- Controle de datas

#### CategoriaBeneficio
- Organização visual dos benefícios
- Ícones e cores personalizáveis
- Ordem de exibição

#### RelatorioBeneficios
- Geração de relatórios
- Controle de períodos
- Arquivos exportáveis

### Views (Visualizações)

#### Dashboard
- Estatísticas gerais
- Gráficos de convênios por categoria
- Benefícios recentes
- Convênios expirando em breve

#### Gestão de Empresas
- Lista com filtros
- Cadastro e edição
- Visualização detalhada
- Exclusão com confirmação

#### Gestão de Convênios
- Lista com filtros avançados
- Cadastro e edição
- Visualização detalhada
- Controle de status

#### Gestão de Benefícios
- Lista com filtros
- Aprovação/rejeição
- Controle de status
- Upload de comprovantes

#### Solicitação de Benefícios
- Interface para associados
- Seleção de convênios ativos
- Formulário de solicitação
- Acompanhamento de status

### Formulários (Forms)

- **EmpresaParceiraForm**: Cadastro completo de empresas
- **ConvenioForm**: Criação e edição de convênios
- **BeneficioForm**: Gestão de benefícios
- **CategoriaBeneficioForm**: Configuração de categorias
- **BeneficioSolicitacaoForm**: Solicitação por associados
- **ConvenioBuscaForm**: Busca avançada de convênios

## URLs e Rotas

### Dashboard
- `/beneficios/` - Dashboard principal

### Empresas Parceiras
- `/beneficios/empresas/` - Lista de empresas
- `/beneficios/empresas/novo/` - Nova empresa
- `/beneficios/empresas/<id>/` - Detalhes da empresa
- `/beneficios/empresas/<id>/editar/` - Editar empresa
- `/beneficios/empresas/<id>/excluir/` - Excluir empresa

### Convênios
- `/beneficios/convenios/` - Lista de convênios
- `/beneficios/convenios/novo/` - Novo convênio
- `/beneficios/convenios/<id>/` - Detalhes do convênio
- `/beneficios/convenios/<id>/editar/` - Editar convênio
- `/beneficios/convenios/<id>/excluir/` - Excluir convênio

### Benefícios
- `/beneficios/beneficios/` - Lista de benefícios
- `/beneficios/beneficios/novo/` - Novo benefício
- `/beneficios/beneficios/<id>/` - Detalhes do benefício
- `/beneficios/beneficios/<id>/editar/` - Editar benefício
- `/beneficios/beneficios/<id>/excluir/` - Excluir benefício

### Categorias
- `/beneficios/categorias/` - Lista de categorias
- `/beneficios/categorias/novo/` - Nova categoria
- `/beneficios/categorias/<id>/editar/` - Editar categoria
- `/beneficios/categorias/<id>/excluir/` - Excluir categoria

### Funcionalidades Especiais
- `/beneficios/solicitar/` - Solicitar benefício
- `/beneficios/meus-beneficios/` - Benefícios do usuário
- `/beneficios/buscar-convenios/` - Busca de convênios
- `/beneficios/beneficios/<id>/aprovar/` - Aprovar benefício
- `/beneficios/beneficios/<id>/rejeitar/` - Rejeitar benefício

### APIs
- `/beneficios/api/convenios-por-categoria/` - Dados para gráficos
- `/beneficios/api/beneficios-por-status/` - Estatísticas de status

## Configuração e Instalação

### 1. Migrações
```bash
python manage.py makemigrations beneficios
python manage.py migrate
```

### 2. Admin do Django
O módulo já está configurado no admin do Django com:
- Filtros avançados
- Ações em lote
- Campos organizados em fieldsets
- Validações automáticas

### 3. Permissões
- Todas as views requerem login (`@login_required`)
- Controle de acesso baseado em usuário
- Aprovação de benefícios por usuários autorizados

## Características Técnicas

### Frontend
- **Bootstrap 5**: Interface responsiva e moderna
- **FontAwesome**: Ícones consistentes
- **Chart.js**: Gráficos interativos
- **Máscaras JavaScript**: Formatação automática de campos

### Backend
- **Django 5.0**: Framework web robusto
- **SQLite**: Banco de dados padrão
- **Sistema de migrações**: Controle de versão do banco
- **Validações**: Formulários com validação automática

### Segurança
- **CSRF Protection**: Proteção contra ataques CSRF
- **Login Required**: Acesso restrito a usuários autenticados
- **Validação de dados**: Sanitização de entrada
- **Upload seguro**: Controle de arquivos enviados

## Uso e Operação

### Para Administradores
1. **Cadastrar Empresas**: Adicionar empresas parceiras
2. **Criar Convênios**: Definir benefícios e condições
3. **Gerenciar Benefícios**: Aprovar/rejeitar solicitações
4. **Gerar Relatórios**: Acompanhar estatísticas

### Para Associados
1. **Buscar Convênios**: Encontrar benefícios disponíveis
2. **Solicitar Benefícios**: Fazer pedidos de aprovação
3. **Acompanhar Status**: Verificar aprovação/rejeição
4. **Enviar Comprovantes**: Documentar utilização

## Manutenção e Suporte

### Logs
- Todas as operações são registradas
- Controle de usuários e datas
- Histórico de alterações

### Backup
- Banco de dados com migrações
- Arquivos de mídia organizados
- Controle de versão com Git

### Atualizações
- Sistema de migrações automático
- Compatibilidade com Django 5.0
- Documentação atualizada

## Contribuição e Desenvolvimento

### Padrões de Código
- **PEP 8**: Estilo Python consistente
- **Docstrings**: Documentação de funções
- **Type Hints**: Tipagem opcional
- **Testes**: Cobertura de funcionalidades

### Estrutura de Arquivos
```
beneficios/
├── models.py          # Modelos de dados
├── views.py           # Lógica de negócio
├── forms.py           # Formulários
├── admin.py           # Interface administrativa
├── urls.py            # Configuração de rotas
├── apps.py            # Configuração do app
└── migrations/        # Migrações do banco
```

### Próximas Funcionalidades
- **Notificações**: E-mail e SMS automáticos
- **API REST**: Integração com sistemas externos
- **Dashboard Avançado**: Mais gráficos e estatísticas
- **Relatórios PDF**: Exportação em formato profissional
- **Integração Mobile**: Aplicativo para associados

## Suporte e Contato

Para dúvidas, sugestões ou problemas:
- **Documentação**: Este arquivo README
- **Issues**: Sistema de controle de problemas
- **Desenvolvedor**: Equipe de TI da ABMEPI

---

**Versão**: 1.0.0  
**Última Atualização**: Agosto 2025  
**Django**: 5.0.2  
**Python**: 3.11+
