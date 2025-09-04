# Criação Automática de Usuários para Advogados

## 📋 Visão Geral

O sistema agora cria automaticamente usuários do sistema quando um novo advogado é cadastrado. Isso permite que os advogados acessem o sistema imediatamente após o cadastro.

## 🚀 Funcionalidades Implementadas

### 1. Criação Automática de Usuário
- ✅ **Usuário criado automaticamente** quando um advogado é salvo
- ✅ **Username**: CPF do advogado (formato: XXX.XXX.XXX-XX)
- ✅ **Senha padrão**: 12345678 (senha padrão fixa)
- ✅ **Tipo de usuário**: 'advogado'
- ✅ **Status**: Ativo/Inativo baseado no status do advogado
- ✅ **Primeiro acesso**: Força alteração da senha padrão

### 2. Interface de Usuário
- ✅ **Modal informativo** com dados de acesso
- ✅ **Botão de preenchimento automático** dos campos de login
- ✅ **Botão de imprimir** informações em formato profissional
- ✅ **Design responsivo** com cards informativos
- ✅ **Destaque visual** nos campos preenchidos automaticamente
- ✅ **Página de primeiro acesso** para alteração obrigatória de senha

### 3. Comando de Gerenciamento
- ✅ **Comando Django** para criar usuários para advogados existentes
- ✅ **Modo dry-run** para simular sem alterar dados
- ✅ **Modo force** para recriar usuários existentes

### 4. Middleware de Segurança
- ✅ **Verificação automática** de primeiro acesso
- ✅ **Redirecionamento obrigatório** para alteração de senha
- ✅ **Bloqueio de acesso** até alteração da senha padrão
- ✅ **Log de auditoria** para todas as alterações

## 🛠️ Como Usar

### Criação de Novo Advogado

1. **Acesse** o sistema como administrador
2. **Clique** em "Novo Advogado"
3. **Preencha** o formulário com os dados do advogado
4. **Salve** o formulário
5. **Visualize** as informações de acesso no modal
6. **Clique** em "Preencher Campos de Login" para preencher automaticamente os campos de usuário e senha

### Primeiro Acesso do Advogado

1. **Faça login** com as credenciais padrão (CPF e senha 12345678)
2. **Sistema redireciona** automaticamente para a página de primeiro acesso
3. **Senha padrão pré-preenchida** nos campos (12345678)
4. **Digite** uma nova senha diferente da padrão (mínimo 8 caracteres, não apenas números)
5. **Confirme** a nova senha
6. **Clique** em "Alterar Senha"
7. **Acesse** o sistema normalmente com a nova senha

### Comando para Advogados Existentes

```bash
# Verificar quantos usuários seriam criados (sem alterar dados)
python manage.py criar_usuarios_advogados --dry-run

# Criar usuários para advogados sem usuário
python manage.py criar_usuarios_advogados

# Forçar recriação de todos os usuários
python manage.py criar_usuarios_advogados --force
```

## 🔐 Informações de Acesso

### Credenciais Padrão
- **Usuário**: CPF do advogado (ex: 123.456.789-00)
- **Senha**: 12345678 (senha padrão fixa)
- **Tipo**: Advogado
- **Status**: Ativo

### Exemplo
```
Advogado: João Silva
CPF: 123.456.789-00
Usuário: 123.456.789-00
Senha: 12345678
```

## ⚠️ Importante

### Segurança
- 🔒 **Altere a senha padrão** no primeiro acesso (obrigatório)
- 🔒 **Guarde as informações** em local seguro
- 🔒 **Não compartilhe** as credenciais
- 🔒 **Use HTTPS** para acesso remoto
- 🔒 **Validação de força** da nova senha
- 🔒 **Log de auditoria** para todas as alterações

### Primeiro Acesso
1. **Faça login** com as credenciais padrão
2. **Altere a senha** imediatamente (obrigatório)
3. **Configure** informações de perfil
4. **Verifique** permissões e acessos
5. **Sistema bloqueia** acesso até alteração da senha
6. **Validação** de força da nova senha

## 🔧 Configuração Técnica

### Modelo Advogado
```python
class Advogado(models.Model):
    user = models.OneToOneField('core.Usuario', ...)
    
    def criar_usuario_sistema(self):
        # Cria usuário automaticamente com primeiro_acesso=True
        
    def save(self, *args, **kwargs):
        # Chama criação automática se necessário
```

### View de Criação
```python
def advogado_modal_create(request):
    if form.is_valid():
        advogado = form.save()
        # Retorna informações de login se usuário foi criado
        if advogado.user:
            return JsonResponse({
                'success': True,
                'login_info': {
                    'username': advogado.user.username,
                    'senha_padrao': '12345678',
                    'tipo_usuario': advogado.user.tipo_usuario
                }
            })
```

### Middleware de Primeiro Acesso
```python
class PrimeiroAcessoMiddleware:
    def __call__(self, request):
        if (request.user.is_authenticated and 
            request.user.primeiro_acesso):
            # Redireciona para alteração de senha
            return redirect('primeiro_acesso')
```

### JavaScript
```javascript
// Exibe modal com informações de login
if (data.login_info) {
    showDetailModal('Informações de Acesso', loginMessage);
    return; // Não fecha modal automaticamente
}
```

## 📱 Interface do Usuário

### Modal de Informações
- 🎨 **Design moderno** com Bootstrap 5
- 📱 **Responsivo** para todos os dispositivos
- 🎯 **Foco** nas informações importantes
- 🔄 **Botões de ação** para copiar e imprimir

### Funcionalidades
- 🖱️ **Preenchimento automático** dos campos de login
- 🖨️ **Imprimir** em formato profissional
- 💾 **Salvar** informações localmente
- 🔒 **Segurança** com avisos importantes
- ✨ **Destaque visual** nos campos preenchidos
- 🎯 **Foco automático** no campo de senha
- 🚨 **Primeiro acesso obrigatório** para alteração de senha
- 🔐 **Validação de força** da nova senha
- 📝 **Log de atividades** para auditoria

## 🚨 Solução de Problemas

### Usuário não foi criado
1. **Verifique** se o CPF está no formato correto
2. **Confirme** se o email é válido
3. **Execute** o comando de gerenciamento
4. **Verifique** logs do sistema

### Erro de permissão
1. **Confirme** que você é administrador
2. **Verifique** permissões do usuário
3. **Execute** migrações se necessário
4. **Reinicie** o servidor

### Problemas de interface
1. **Limpe** cache do navegador
2. **Verifique** console JavaScript
3. **Confirme** versão do Bootstrap
4. **Teste** em navegador diferente

## 📈 Próximas Melhorias

### Planejadas
- 🔐 **Envio de email** com credenciais
- 📱 **Notificação push** para administradores
- 🔄 **Sincronização** com sistemas externos
- 📊 **Relatórios** de usuários criados

### Sugestões
- 🎨 **Temas personalizáveis** para modais
- 📧 **Templates de email** configuráveis
- 🔐 **Políticas de senha** configuráveis
- 📱 **App mobile** para gerenciamento

## 📞 Suporte

### Contato
- **Email**: suporte@abmepi.org.br
- **Telefone**: (11) 1234-5678
- **Documentação**: [Wiki do Sistema](https://wiki.abmepi.org.br)

### Links Úteis
- [Manual do Usuário](https://manual.abmepi.org.br)
- [FAQ](https://faq.abmepi.org.br)
- [Vídeos Tutoriais](https://tutoriais.abmepi.org.br)

---

**Desenvolvido por** Equipe ABMEPI ASEJUS  
**Versão** 1.0.0  
**Data** Dezembro 2024
