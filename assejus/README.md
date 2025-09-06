# App ASEJUS - Assistência Jurídica

Este app gerencia a assistência jurídica para associados da ABMEPI.

## Funcionalidades

### Tipos de Demandas
O sistema suporta os seguintes tipos de demandas jurídicas:

- **Civil**: Questões civis gerais
- **Trabalhista**: Direito do trabalho
- **Previdenciário**: Previdência social
- **Penal**: Direito penal
- **Administrativo**: Direito administrativo
- **Tributário**: Direito tributário
- **Ambiental**: Direito ambiental
- **Consumidor**: Direito do consumidor
- **Família**: Direito de família
- **Sucessões**: Heranças e sucessões
- **Contratos**: Contratos em geral
- **Propriedade**: Direito de propriedade
- **Outros**: Outros tipos de demandas

### Status dos Atendimentos
Os atendimentos podem ter os seguintes status:

- **Aberto**: Atendimento recém-criado
- **Em Análise**: Em análise pelo advogado
- **Em Andamento**: Processo em andamento
- **Aguardando Documentos**: Aguardando documentos do associado
- **Aguardando Decisão**: Aguardando decisão judicial
- **Suspenso**: Temporariamente suspenso
- **Concluído**: Atendimento finalizado
- **Arquivado**: Atendimento arquivado
- **Cancelado**: Atendimento cancelado

### Prioridades
Os atendimentos são classificados por prioridade:

- **Baixa**: Baixa urgência
- **Média**: Urgência moderada
- **Alta**: Alta urgência
- **Urgente**: Muito urgente
- **Crítica**: Extremamente urgente

### Tipos de Documentos
O sistema suporta os seguintes tipos de documentos:

- **Petição**: Petições judiciais
- **Contrato**: Contratos diversos
- **Procuração**: Procurações
- **Documento de Identidade**: Documentos pessoais
- **Comprovante**: Comprovantes diversos
- **Laudo**: Laudos técnicos
- **Parecer**: Pareceres jurídicos
- **Sentença**: Sentenças judiciais
- **Acórdão**: Acórdãos
- **Outros**: Outros tipos de documentos

### Tipos de Consultas
As consultas jurídicas podem ser dos seguintes tipos:

- **Dúvida Jurídica**: Dúvidas gerais sobre direito
- **Orientação Legal**: Orientação jurídica
- **Análise de Documento**: Análise de documentos
- **Consulta de Processo**: Consultas sobre processos
- **Orientação Trabalhista**: Orientação sobre direito do trabalho
- **Orientação Previdenciária**: Orientação sobre previdência
- **Orientação Civil**: Orientação sobre direito civil
- **Outros**: Outros tipos de consultas

## Modelos

### AtendimentoJuridico
- Gerencia os casos jurídicos dos associados
- Inclui tipo de demanda, status, prioridade e responsáveis
- Permite acompanhamento do progresso dos casos

### ConsultaJuridica
- Gerencia consultas rápidas dos associados
- Inclui pergunta, resposta e status de resolução
- Permite orientação jurídica sem abertura de processo

### DocumentoJuridico
- Gerencia documentos relacionados aos casos
- Inclui upload de arquivos e categorização por tipo
- Permite organização documental dos processos

### Andamento
- Registra o progresso dos casos
- Inclui descrição das atividades realizadas
- Permite histórico completo dos atendimentos

## Formulários

Todos os formulários incluem:
- Validação de dados
- Choices para campos de seleção
- Filtros automáticos (ex: apenas advogados ativos)
- Interface responsiva com Bootstrap

## Admin

O admin do Django inclui:
- Listas organizadas por campos relevantes
- Filtros para facilitar a busca
- Ações em lote para operações comuns
- Campos de busca otimizados

## Migrações

As migrações incluem:
- Alteração do campo `associado` de CharField para ForeignKey
- Adição de choices para todos os campos de tipo
- Ajuste de tamanhos de campos para acomodar as choices
- Manutenção da integridade dos dados existentes
