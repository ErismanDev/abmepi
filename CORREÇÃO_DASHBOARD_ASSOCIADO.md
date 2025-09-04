# Correção do AttributeError no Dashboard do Usuário

## Problema
- **Erro**: `AttributeError: Objeto 'Associado' não possui atributo 'mensalidade_set'`
- **Localização**: `C:\projetos\abmepi\core\views.py`, linha 662, função `usuario_dashboard`
- **URL**: `http://127.0.0.1:8000/core/dashboard/usuario/`

## Causa
O erro ocorreu porque o código estava tentando acessar `mensalidade_set` no modelo `Associado`, mas o modelo `Mensalidade` foi definido com um `related_name='mensalidades'` no campo `ForeignKey` para `Associado`.

```python
# Modelo Mensalidade (financeiro/models.py)
associado = models.ForeignKey(
    Associado,
    on_delete=models.CASCADE,
    related_name='mensalidades',  # Define o nome da relação reversa
    verbose_name=_('Associado')
)
```

## Correções Realizadas

### 1. Correção no arquivo `core/views.py`
- **Linha 662**: Alterado `associado.mensalidade_set.all()` para `associado.mensalidades.all()`
- **Linha 668**: Alterado `associado.mensalidade_set.all()` para `associado.mensalidades.all()`
- **Linha 691**: Alterado `advogado.atendimentojuridico_set.all()` para `advogado.casos_responsavel.all()`
- **Linha 699**: Alterado `psicologo.atendimentopsicologico_set.all()` para `psicologo.sessao_set.all()`

### 2. Correção no template `templates/financeiro/tipo_recebimento_confirm_delete.html`
- **Linha 102-103**: Alterado `object.mensalidade_set` para `object.mensalidades`

## Detalhes das Correções

### Mensalidades do Associado
```python
# ANTES (incorreto)
context['mensalidades'] = associado.mensalidade_set.all()[:5]

# DEPOIS (correto)
context['mensalidades'] = associado.mensalidades.all()[:5]
```

### Casos Jurídicos do Advogado
```python
# ANTES (incorreto)
context['casos_recentes'] = advogado.atendimentojuridico_set.all()[:5]

# DEPOIS (correto)
context['casos_recentes'] = advogado.casos_responsavel.all()[:5]
```

### Sessões do Psicólogo
```python
# ANTES (incorreto)
context['atendimentos_recentes'] = psicologo.atendimentopsicologico_set.all()[:5]

# DEPOIS (correto)
context['atendimentos_recentes'] = psicologo.sessao_set.all()[:5]
```

## Modelos Relacionados

### Mensalidade (financeiro/models.py)
- `related_name='mensalidades'` no campo `associado`
- Acesso correto: `associado.mensalidades.all()`

### AtendimentoJuridico (assejus/models.py)
- `related_name='casos_responsavel'` no campo `advogado_responsavel`
- Acesso correto: `advogado.casos_responsavel.all()`

### Sessao (psicologia/models.py)
- Sem `related_name` personalizado no campo `psicologo`
- Acesso correto: `psicologo.sessao_set.all()` (nome padrão do Django)

## Teste de Validação
Criado e executado script de teste que validou:
- ✅ Acesso às mensalidades do associado funciona
- ✅ Não há mais AttributeError
- ✅ Dashboard do usuário agora funciona corretamente

## Status
- ✅ **CORRIGIDO**: O AttributeError foi resolvido
- ✅ **TESTADO**: Script de validação confirmou as correções
- ✅ **FUNCIONAL**: Dashboard do usuário agora carrega sem erros

Data da correção: 01/09/2025
