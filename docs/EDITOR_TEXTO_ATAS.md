# Editor de Texto para Atas de Reunião

## Visão Geral

O sistema de atas de reunião agora inclui um editor de texto rico e moderno baseado no TinyMCE, permitindo criar atas profissionais diretamente no sistema.

## Funcionalidades do Editor

### Recursos Principais

- **Formatação de Texto**: Negrito, itálico, sublinhado, cores de texto e fundo
- **Estruturação**: Títulos (H1-H6), listas numeradas e com marcadores
- **Tabelas**: Criação e edição de tabelas com formatação
- **Links e Imagens**: Inserção de elementos multimídia
- **Templates**: Modelo pré-definido para atas de reunião
- **Código**: Suporte a código e snippets
- **Emojis**: Biblioteca de emojis integrada

### Recursos Avançados

- **Cópia/Colagem Inteligente**: Remove formatação desnecessária automaticamente
- **Busca e Substituição**: Ferramentas de edição avançadas
- **Contagem de Palavras**: Acompanhamento do conteúdo em tempo real
- **Modo Tela Cheia**: Para edição focada e sem distrações
- **Desfazer/Refazer**: Múltiplos níveis de histórico de edição

## Como Usar

### 1. Acessando o Editor

1. Navegue para **Diretoria > Atas de Reunião**
2. Clique em **Nova Ata**
3. Preencha os campos básicos (título, data, local, etc.)
4. Use o editor nos campos:
   - **Pauta da Reunião**
   - **Deliberações** (obrigatório)
   - **Observações**

### 2. Usando o Template Pré-definido

1. No editor, clique no ícone de **Templates** (📄)
2. Selecione **"Ata de Reunião - Estrutura Básica"**
3. O template será inserido automaticamente
4. Substitua os campos entre colchetes pelos dados reais

### 3. Formatação Básica

- **Títulos**: Use os botões H1, H2, H3 para criar seções
- **Listas**: Use os botões de lista numerada ou com marcadores
- **Negrito/Itálico**: Use os botões B e I na barra de ferramentas
- **Alinhamento**: Use os botões de alinhamento à esquerda, centro, direita

### 4. Inserindo Elementos

- **Tabelas**: Clique no ícone de tabela para inserir
- **Links**: Selecione o texto e clique no ícone de link
- **Imagens**: Use o ícone de imagem (suporte a upload)
- **Emojis**: Use o ícone de emoji para inserir símbolos

## Template Pré-definido

O sistema inclui um template estruturado que contém:

```html
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
```

## Dicas de Uso

### Para Pautas
- Use listas numeradas para organizar os itens
- Adicione subtítulos para agrupar assuntos relacionados
- Use negrito para destacar pontos importantes

### Para Deliberações
- Use listas para organizar as decisões
- Destaque em negrito as decisões principais
- Inclua prazos e responsáveis quando aplicável

### Para Observações
- Use itálico para observações gerais
- Adicione links para documentos relacionados
- Inclua informações de contato se necessário

## Visualização e Impressão

### Visualizando Atas
- As atas são exibidas com formatação completa
- Layout profissional otimizado para impressão
- Metadados organizados e fáceis de ler

### Imprimindo Atas
- Use o botão **Imprimir** na página de visualização
- O layout é otimizado automaticamente para impressão
- Elementos desnecessários são ocultados na impressão

## Solução de Problemas

### Editor não carrega
- Verifique se o JavaScript está habilitado no navegador
- Limpe o cache do navegador
- Verifique se não há bloqueadores de script ativos

### Formatação não salva
- Certifique-se de clicar em **Salvar** antes de sair da página
- Verifique se todos os campos obrigatórios estão preenchidos
- Recarregue a página se necessário

### Problemas de cópia/colagem
- Use Ctrl+Shift+V para colar sem formatação
- O editor limpa automaticamente formatação desnecessária
- Para manter formatação, use Ctrl+V normalmente

## Suporte Técnico

Para problemas técnicos ou dúvidas sobre o editor:
- Verifique a documentação do TinyMCE
- Consulte o administrador do sistema
- Reporte bugs através do sistema de suporte

---

**Versão**: 1.0  
**Última atualização**: Janeiro 2025  
**Compatibilidade**: Navegadores modernos (Chrome, Firefox, Safari, Edge)
