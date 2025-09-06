# Módulo Hotel de Trânsito - ABMEPI

## Descrição

O módulo Hotel de Trânsito é uma solução completa para gerenciamento de hospedagem temporária, permitindo o cadastro e controle de hóspedes (associados e não associados), quartos, reservas e hospedagens efetivas.

## Funcionalidades Principais

### 1. Gestão de Quartos
- Cadastro de quartos com diferentes tipos (Individual, Duplo, Triplo, Suíte)
- Controle de status (Disponível, Ocupado, Em Manutenção, Reservado)
- Características dos quartos (Ar condicionado, TV, Wi-Fi, Banheiro privativo, Frigobar)
- Definição de valores de diária
- Controle de capacidade

### 2. Gestão de Hóspedes
- **Hóspedes Associados**: Integração com o sistema de associados existente
- **Hóspedes Não Associados**: Cadastro completo com dados pessoais e profissionais
- Documentos de identificação (CPF, RG, Passaporte, CNH)
- Informações de contato e endereço
- Histórico de hospedagens

### 3. Sistema de Reservas
- Criação de reservas com datas de entrada e saída
- Códigos únicos para cada reserva
- Controle de status (Pendente, Confirmada, Cancelada, Finalizada)
- Verificação automática de disponibilidade
- Cálculo automático de valores

### 4. Controle de Hospedagens
- Check-in e check-out de hóspedes
- Registro de datas e horários reais
- Controle de status (Ativa, Finalizada, Cancelada)
- Cálculo automático de diárias e valores
- Integração com reservas

### 5. Serviços Adicionais
- Cadastro de serviços oferecidos (Alimentação, Transporte, Lavanderia, etc.)
- Controle de valores
- Registro de serviços utilizados pelos hóspedes
- Cálculo de custos adicionais

### 6. Relatórios e Estatísticas
- Dashboard com visão geral do sistema
- Relatórios de ocupação por período
- Estatísticas de receita
- Controle de hóspedes por tipo
- Exportação de dados

## Estrutura do Módulo

### Models
- `Quarto`: Cadastro e características dos quartos
- `Hospede`: Dados dos hóspedes (associados e não associados)
- `Reserva`: Sistema de reservas
- `Hospedagem`: Controle de hospedagens efetivas
- `ServicoAdicional`: Catálogo de serviços
- `ServicoUtilizado`: Registro de serviços utilizados

### Views
- **Dashboard**: Visão geral do sistema
- **CRUD Completo**: Para todos os modelos
- **Funcionalidades Especiais**: Confirmação/cancelamento de reservas, check-in/out
- **Busca e Relatórios**: Quartos disponíveis e relatórios de hospedagem
- **Views AJAX**: Para operações rápidas e busca

### Forms
- Formulários para todos os modelos
- Validações personalizadas
- Campos dependentes (tipo de hóspede → associado)
- Máscaras para campos específicos (telefone, CEP, CPF)

### Admin
- Interface administrativa completa
- Filtros e busca avançada
- Campos editáveis em lista
- Relacionamentos visuais

## Instalação e Configuração

### 1. Adicionar ao INSTALLED_APPS
```python
INSTALLED_APPS = [
    # ... outros apps
    'hotel_transito.apps.HotelTransitoConfig',
]
```

### 2. Incluir URLs
```python
# abmepi/urls.py
urlpatterns = [
    # ... outras URLs
    path('hotel-transito/', include('hotel_transito.urls')),
]
```

### 3. Executar Migrações
```bash
python manage.py makemigrations hotel_transito
python manage.py migrate
```

### 4. Criar Superusuário (se necessário)
```bash
python manage.py createsuperuser
```

## Uso do Sistema

### 1. Cadastro de Quartos
1. Acesse **Hotel de Trânsito > Quartos > Novo**
2. Preencha as informações básicas (número, tipo, capacidade, valor)
3. Configure as características do quarto
4. Salve o quarto

### 2. Cadastro de Hóspedes
1. Acesse **Hotel de Trânsito > Hóspedes > Novo**
2. Escolha o tipo de hóspede (Associado ou Não Associado)
3. Se for associado, selecione na lista
4. Se for não associado, preencha todos os dados
5. Salve o hóspede

### 3. Criação de Reservas
1. Acesse **Hotel de Trânsito > Reservas > Novo**
2. Selecione o hóspede e quarto
3. Defina as datas de entrada e saída
4. Confirme a reserva
5. O sistema gerará um código único

### 4. Check-in de Hóspedes
1. Acesse **Hotel de Trânsito > Hospedagens > Novo**
2. Selecione a reserva (opcional) ou crie direto
3. Confirme o check-in
4. O quarto será marcado como ocupado

### 5. Check-out de Hóspedes
1. Acesse a hospedagem ativa
2. Clique em **Finalizar Hospedagem**
3. Confirme o check-out
4. O quarto será liberado

## Funcionalidades Avançadas

### Busca de Quartos Disponíveis
- Filtro por período
- Filtro por tipo de quarto
- Filtro por capacidade mínima
- Verificação automática de conflitos

### Relatórios
- Períodos predefinidos (hoje, semana, mês, trimestre, ano)
- Filtros por tipo de hóspede e status
- Estatísticas de ocupação e receita
- Exportação de dados

### Operações Rápidas
- Check-in rápido via AJAX
- Check-out rápido via AJAX
- Busca de hóspedes em tempo real
- Verificação de disponibilidade

## Integração com Outros Módulos

### Módulo de Associados
- Hóspedes podem ser associados existentes
- Dados são sincronizados automaticamente
- Histórico de hospedagens vinculado ao associado

### Módulo Financeiro (Futuro)
- Integração com sistema de pagamentos
- Controle de receitas do hotel
- Relatórios financeiros

## Personalizações

### Estilos CSS
- Arquivo `static/hotel_transito/css/modais.css`
- Classes específicas para formulários
- Responsividade para dispositivos móveis

### JavaScript
- Arquivo `static/hotel_transito/js/modais.js`
- Validações personalizadas
- Máscaras de campos
- Operações AJAX

## Manutenção

### Backup de Dados
- Backup regular do banco de dados
- Exportação de relatórios importantes
- Controle de versões do código

### Atualizações
- Verificar compatibilidade com versões do Django
- Testar funcionalidades após atualizações
- Manter dependências atualizadas

## Suporte e Documentação

### Logs
- Verificar logs do Django para erros
- Monitorar operações críticas
- Rastrear problemas de performance

### Documentação
- Este README para uso geral
- Comentários no código para desenvolvedores
- Documentação da API (se aplicável)

## Considerações de Segurança

### Permissões
- Todas as views requerem login
- Verificação de permissões específicas (futuro)
- Controle de acesso por usuário

### Validação de Dados
- Validação no frontend e backend
- Sanitização de entradas
- Proteção contra ataques comuns

### Auditoria
- Log de todas as operações
- Rastreamento de mudanças
- Histórico de usuários

## Roadmap Futuro

### Funcionalidades Planejadas
- Sistema de notificações
- Integração com APIs externas
- App móvel para hóspedes
- Sistema de avaliações
- Gestão de eventos e conferências

### Melhorias Técnicas
- Cache para consultas frequentes
- Otimização de queries
- Testes automatizados
- CI/CD pipeline

---

**Desenvolvido para ABMEPI**  
**Versão**: 1.0.0  
**Data**: 2024  
**Desenvolvedor**: Sistema ABMEPI
