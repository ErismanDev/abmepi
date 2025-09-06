from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.core.validators import RegexValidator
from django.conf import settings
from .models import Usuario, InstitucionalConfig, FeedPost, AssejurNews, AssejurInformativo
import secrets
import string


class LoginForm(AuthenticationForm):
    """
    Formulário de login personalizado para CPF
    """
    username = forms.CharField(
        label='CPF',
        max_length=14,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'XXX.XXX.XXX-XX',
            'autocomplete': 'username'
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='CPF deve estar no formato XXX.XXX.XXX-XX'
            )
        ]
    )
    
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha',
            'autocomplete': 'current-password'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})


class UsuarioCreationForm(UserCreationForm):
    """
    Formulário para criação de usuários com senha padrão
    """
    first_name = forms.CharField(
        label='Nome',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome'
        })
    )
    
    last_name = forms.CharField(
        label='Sobrenome',
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o sobrenome'
        })
    )
    
    email = forms.EmailField(
        label='E-mail',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o e-mail'
        })
    )
    
    tipo_usuario = forms.ChoiceField(
        label='Tipo de Usuário',
        choices=Usuario.TIPO_USUARIO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    ativo = forms.BooleanField(
        label='Usuário Ativo',
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'tipo_usuario', 'ativo')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remover campos de senha do formulário
        if 'password1' in self.fields:
            del self.fields['password1']
        if 'password2' in self.fields:
            del self.fields['password2']
        
        # Configurar widgets com classes CSS
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'XXX.XXX.XXX-XX'
        })
    
    def save(self, commit=True):
        # Criar usuário sem chamar super().save() para evitar dependência dos campos de senha
        user = self.instance
        if not user.pk:
            user = self.Meta.model()
        
        # Preencher os campos do usuário
        user.username = self.cleaned_data['username']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.tipo_usuario = self.cleaned_data['tipo_usuario']
        user.is_active = self.cleaned_data['ativo']
        
        # Definir senha padrão
        senha_padrao = 'abmepi2025'
        user.set_password(senha_padrao)
        
        # Marcar como primeiro acesso (deve alterar senha)
        user.primeiro_acesso = True
        
        # Armazenar senha temporária para visualização de administradores
        from django.utils import timezone
        from datetime import timedelta
        
        user.senha_temporaria = senha_padrao
        user.senha_temporaria_expira = timezone.now() + timedelta(hours=24)  # Expira em 24 horas
        
        if commit:
            user.save()
            
            # VINCULAÇÃO AUTOMÁTICA BASEADA NO TIPO DE USUÁRIO
            self._vincular_usuario_automaticamente(user)
            
        return user
    
    def _vincular_usuario_automaticamente(self, user):
        """
        Vincula automaticamente o usuário ao registro correspondente baseado no tipo
        """
        try:
            print(f"🔗 Iniciando vinculação automática para usuário {user.username} (tipo: {user.tipo_usuario})")
            
            if user.tipo_usuario == 'associado':
                self._vincular_associado(user)
            elif user.tipo_usuario == 'advogado':
                self._vincular_advogado(user)
            elif user.tipo_usuario == 'psicologo':
                self._vincular_psicologo(user)
            else:
                print(f"ℹ️ Tipo de usuário '{user.tipo_usuario}' não requer vinculação automática")
                
        except Exception as e:
            print(f"❌ Erro na vinculação automática: {e}")
            import traceback
            traceback.print_exc()
    
    def _vincular_associado(self, user):
        """Vincula usuário a um associado existente"""
        try:
            from associados.models import Associado
            
            # Buscar associado pelo CPF
            associado = Associado.objects.get(cpf=user.username)
            
            if associado.usuario:
                print(f"⚠️ Associado {associado.nome} já tem usuário vinculado: {associado.usuario.username}")
                if associado.usuario != user:
                    print(f"🔄 Substituindo usuário de {associado.usuario.username} para {user.username}")
            else:
                print(f"✅ Associado {associado.nome} não tem usuário - vinculando")
            
            # Vincular usuário ao associado
            associado.usuario = user
            associado.save()
            
            print(f"✅ VINCULAÇÃO ASSOCIADO CONCLUÍDA: {associado.nome}")
            
        except Associado.DoesNotExist:
            print(f"⚠️ Nenhum associado encontrado com CPF {user.username}")
            print(f"💡 Criando registro básico de associado...")
            
            # Criar registro básico de associado
            try:
                from associados.models import Associado
                from datetime import date
                
                associado = Associado.objects.create(
                    usuario=user,
                    nome=f"{user.first_name} {user.last_name}".strip(),
                    cpf=user.username,
                    rg="000000000",  # RG temporário
                    data_nascimento=date(1990, 1, 1),  # Data padrão
                    sexo='M',  # Padrão masculino
                    estado_civil='solteiro',  # Padrão solteiro
                    nacionalidade='Brasileira',
                    email=user.email,
                    telefone="(00) 00000-0000",
                    celular="(00) 00000-0000",
                    cep="00000-000",
                    rua="Rua não informada",
                    numero="000",
                    bairro="Bairro não informado",
                    cidade="Cidade não informada",
                    estado="XX",
                    tipo_socio='efetivo',  # Padrão efetivo
                    tipo_profissional='militar',  # Padrão militar
                    matricula_militar="000000000",
                    posto_graduacao="Soldado",
                    nome_civil=f"{user.first_name} {user.last_name}".strip(),
                    unidade_lotacao="Unidade não informada",
                    data_ingresso=date.today(),
                    situacao='ativo',
                    ativo=True,
                    observacoes="Registro criado automaticamente - dados precisam ser atualizados"
                )
                print(f"✅ REGISTRO DE ASSOCIADO CRIADO: {associado.nome}")
                
            except Exception as e:
                print(f"❌ Erro ao criar associado: {e}")
                import traceback
                traceback.print_exc()
        except Exception as e:
            print(f"❌ Erro ao vincular associado: {e}")
            import traceback
            traceback.print_exc()
    
    def _vincular_advogado(self, user):
        """Vincula usuário a um advogado existente"""
        try:
            from assejus.models import Advogado
            
            # Buscar advogado pelo CPF
            advogado = Advogado.objects.get(cpf=user.username)
            
            if advogado.user:
                print(f"⚠️ Advogado {advogado.nome} já tem usuário vinculado: {advogado.user.username}")
                if advogado.user != user:
                    print(f"🔄 Substituindo usuário de {advogado.user.username} para {user.username}")
            else:
                print(f"✅ Advogado {advogado.nome} não tem usuário - vinculando")
            
            # Vincular usuário ao advogado
            advogado.user = user
            advogado.save()
            
            print(f"✅ VINCULAÇÃO ADVOGADO CONCLUÍDA: {advogado.nome}")
            
        except Advogado.DoesNotExist:
            print(f"⚠️ Nenhum advogado encontrado com CPF {user.username}")
            print(f"💡 Criando registro básico de advogado...")
            
            # Criar registro básico de advogado
            try:
                from assejus.models import Advogado
                from datetime import date
                
                advogado = Advogado.objects.create(
                    user=user,
                    nome=f"{user.first_name} {user.last_name}".strip(),
                    cpf=user.username,
                    oab="000000/XX",  # OAB temporário
                    uf_oab="XX",
                    email=user.email,
                    telefone="(00) 00000-0000",
                    endereco="Endereço não informado",
                    cidade="Cidade não informada",
                    estado="XX",
                    cep="00000-000",
                    data_inscricao_oab=date(2024, 1, 1),
                    experiencia_anos=0,
                    ativo=True,
                    observacoes="Registro criado automaticamente - dados precisam ser atualizados"
                )
                print(f"✅ REGISTRO DE ADVOGADO CRIADO: {advogado.nome}")
                
            except Exception as e:
                print(f"❌ Erro ao criar advogado: {e}")
        except Exception as e:
            print(f"❌ Erro ao vincular advogado: {e}")
    
    def _vincular_psicologo(self, user):
        """Vincula usuário a um psicólogo existente"""
        try:
            from psicologia.models import Psicologo
            
            # Buscar psicólogo pelo CPF
            psicologo = Psicologo.objects.get(cpf=user.username)
            
            if psicologo.user:
                print(f"⚠️ Psicólogo {psicologo.nome_completo} já tem usuário vinculado: {psicologo.user.username}")
                if psicologo.user != user:
                    print(f"🔄 Substituindo usuário de {psicologo.user.username} para {user.username}")
            else:
                print(f"✅ Psicólogo {psicologo.nome_completo} não tem usuário - vinculando")
            
            # Vincular usuário ao psicólogo
            psicologo.user = user
            psicologo.save()
            
            print(f"✅ VINCULAÇÃO PSICÓLOGO CONCLUÍDA: {psicologo.nome_completo}")
            
        except Psicologo.DoesNotExist:
            print(f"⚠️ Nenhum psicólogo encontrado com CPF {user.username}")
            print(f"💡 Criando registro básico de psicólogo...")
            
            # Criar registro básico de psicólogo
            try:
                from psicologia.models import Psicologo
                from datetime import date
                
                psicologo = Psicologo.objects.create(
                    user=user,
                    nome_completo=f"{user.first_name} {user.last_name}".strip(),
                    cpf=user.username,
                    crp="000000/XX",  # CRP temporário
                    uf_crp="XX",
                    email=user.email,
                    telefone="(00) 00000-0000",
                    endereco="Endereço não informado",
                    cidade="Cidade não informada",
                    estado="XX",
                    cep="00000-000",
                    data_nascimento=date(1990, 1, 1),
                    ativo=True,
                    observacoes="Registro criado automaticamente - dados precisam ser atualizados"
                )
                print(f"✅ REGISTRO DE PSICÓLOGO CRIADO: {psicologo.nome_completo}")
                
            except Exception as e:
                print(f"❌ Erro ao criar psicólogo: {e}")
                import traceback
                traceback.print_exc()
        except Exception as e:
            print(f"❌ Erro ao vincular psicólogo: {e}")
            import traceback
            traceback.print_exc()


class UsuarioChangeForm(UserChangeForm):
    """
    Formulário para edição de usuários
    """
    password1 = forms.CharField(
        label='Nova Senha',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Deixe em branco para manter a senha atual'
        })
    )
    
    password2 = forms.CharField(
        label='Confirmar Nova Senha',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        })
    )
    
    gerar_nova_senha = forms.BooleanField(
        label='Gerar Nova Senha Automaticamente',
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'onclick': 'togglePasswordFields()'
        })
    )
    
    senha_atual_info = forms.CharField(
        label='Senha Atual',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'placeholder': 'Senha temporária visível apenas para administradores'
        })
    )
    
    class Meta:
        model = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'tipo_usuario', 'ativo')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'tipo_usuario': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Se é uma edição (tem instance), mostrar informações da senha atual
        if self.instance and self.instance.pk:
            # Verificar se a senha temporária ainda é válida
            from django.utils import timezone
            if (hasattr(self.instance, 'senha_temporaria') and 
                self.instance.senha_temporaria and 
                hasattr(self.instance, 'senha_temporaria_expira') and
                self.instance.senha_temporaria_expira and
                self.instance.senha_temporaria_expira > timezone.now()):
                
                self.fields['senha_atual_info'].initial = self.instance.senha_temporaria
                self.fields['senha_atual_info'].help_text = f"Expira em: {self.instance.senha_temporaria_expira.strftime('%d/%m/%Y %H:%M')}"
            else:
                self.fields['senha_atual_info'].initial = "Senha temporária expirada ou não disponível"
                self.fields['senha_atual_info'].help_text = "Use 'Redefinir Senha' para gerar uma nova senha visível"
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não coincidem.')
        
        return password2


class UsuarioProfileForm(forms.ModelForm):
    """
    Formulário para perfil do usuário (primeiro acesso)
    """
    nova_senha = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a nova senha'
        })
    )
    
    confirmar_senha = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        })
    )
    
    class Meta:
        model = Usuario
        fields = ('first_name', 'last_name', 'email', 'nova_senha', 'confirmar_senha')
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
        }
    
    def clean_confirmar_senha(self):
        nova_senha = self.cleaned_data.get('nova_senha')
        confirmar_senha = self.cleaned_data.get('confirmar_senha')
        
        if nova_senha and confirmar_senha and nova_senha != confirmar_senha:
            raise forms.ValidationError('As senhas não coincidem.')
        
        return confirmar_senha
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['nova_senha']:
            user.set_password(self.cleaned_data['nova_senha'])
            user.primeiro_acesso = False
        if commit:
            user.save()
        return user


class InstitucionalConfigForm(forms.ModelForm):
    """
    Formulário para configurações institucionais
    """
    class Meta:
        model = InstitucionalConfig
        fields = '__all__'
        widgets = {
            'nome_instituicao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome da instituição'
            }),
            'slogan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Slogan da instituição'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Endereço completo'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '(XX) XXXX-XXXX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contato@instituicao.com'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.instituicao.com'
            }),
            'cnpj': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'XX.XXX.XXX/XXXX-XX'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'favicon': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'cor_primaria': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'width: 60px; height: 38px;'
            }),
            'cor_secundaria': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'width: 60px; height: 38px;'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            # Widgets para campos de serviços
            'servicos_juridicos': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'servicos_psicologicos': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'servicos_medicos': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'servicos_odontologicos': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'servicos_financeiros': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'servicos_educacionais': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'servicos_recreativos': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'servicos_sociais': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'servicos_esportivos': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'servicos_culturais': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'servicos_hotel_transito': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_estatisticas': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_servicos': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_sobre': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'mostrar_cta': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS para campos específicos
        for field_name, field in self.fields.items():
            if field_name in ['ativo', 'mostrar_estatisticas', 'mostrar_servicos', 'mostrar_sobre', 'mostrar_cta'] or field_name.startswith('servicos_'):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif field_name in ['cor_primaria', 'cor_secundaria']:
                field.widget.attrs.update({'class': 'form-control'})
                field.widget.attrs['type'] = 'color'
            else:
                field.widget.attrs.update({'class': 'form-control'})


class FeedPostForm(forms.ModelForm):
    """
    Formulário para posts do feed institucional
    """
    class Meta:
        model = FeedPost
        fields = [
            'titulo', 'conteudo', 'tipo_post', 'imagem', 'autor', 
            'ativo', 'destaque', 'ordem_exibicao'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título da notícia'
            }),
            'conteudo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Conteúdo da notícia'
            }),
            'tipo_post': forms.Select(attrs={
                'class': 'form-select'
            }),
            'imagem': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'autor': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Autor do post'
            }),
            'destaque': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ordem_exibicao': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS para campos específicos
        for field_name, field in self.fields.items():
            if field_name in ['destaque', 'ativo']:
                field.widget.attrs.update({'class': 'form-check-input'})
            elif field_name in ['tipo_post']:
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if not titulo or len(titulo.strip()) == 0:
            raise forms.ValidationError('O título é obrigatório.')
        return titulo.strip()
    
    def clean_conteudo(self):
        conteudo = self.cleaned_data.get('conteudo')
        if not conteudo or len(conteudo.strip()) == 0:
            raise forms.ValidationError('O conteúdo é obrigatório.')
        return conteudo.strip()
    
    def clean_autor(self):
        autor = self.cleaned_data.get('autor')
        if not autor or len(autor.strip()) == 0:
            raise forms.ValidationError('O autor é obrigatório.')
        return autor.strip()


class AssejurNewsForm(forms.ModelForm):
    """
    Formulário para notícias da Assessoria Jurídica
    """
    class Meta:
        model = AssejurNews
        fields = [
            'titulo', 'resumo', 'conteudo', 'categoria', 'icone', 'prioridade', 
            'link_externo', 'tags', 'imagem', 'ativo', 'destaque'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título da notícia jurídica'
            }),
            'resumo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Resumo da notícia'
            }),
            'conteudo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Conteúdo completo da notícia'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'icone': forms.Select(attrs={
                'class': 'form-select'
            }),
            'prioridade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'link_externo': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://exemplo.com/noticia'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Tags separadas por vírgula'
            }),
            'imagem': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'destaque': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS para campos específicos
        for field_name, field in self.fields.items():
            if field_name in ['destaque', 'ativo']:
                field.widget.attrs.update({'class': 'form-check-input'})
            elif field_name in ['categoria', 'icone', 'prioridade']:
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class AssejurInformativoForm(forms.ModelForm):
    """
    Formulário para informativos da Assessoria Jurídica
    """
    class Meta:
        model = AssejurInformativo
        fields = [
            'titulo', 'conteudo', 'icone', 'cor_icone', 
            'prioridade', 'ordem_exibicao', 'ativo'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título do informativo'
            }),
            'conteudo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Conteúdo do informativo'
            }),
            'icone': forms.Select(attrs={
                'class': 'form-select'
            }),
            'cor_icone': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'width: 60px; height: 38px;'
            }),
            'prioridade': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ordem_exibicao': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicionar classes CSS para campos específicos
        for field_name, field in self.fields.items():
            if field_name == 'ativo':
                field.widget.attrs.update({'class': 'form-check-input'})
            elif field_name in ['icone', 'prioridade']:
                field.widget.attrs.update({'class': 'form-select'})
            elif field_name == 'cor_icone':
                field.widget.attrs.update({'class': 'form-control'})
                field.widget.attrs['type'] = 'color'
            else:
                field.widget.attrs.update({'class': 'form-control'})


class PasswordResetRequestForm(forms.Form):
    """
    Formulário para solicitar redefinição de senha
    """
    cpf = forms.CharField(
        label='CPF',
        max_length=14,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'XXX.XXX.XXX-XX'
        }),
        validators=[
            RegexValidator(
                regex=r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
                message='CPF deve estar no formato XXX.XXX.XXX-XX'
            )
        ]
    )
    
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o e-mail cadastrado'
        })
    )


class PasswordResetConfirmForm(forms.Form):
    """
    Formulário para confirmar nova senha
    """
    password1 = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a nova senha'
        })
    )
    
    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        })
    )
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não coincidem.')
        
        return password2


class UsuarioSearchForm(forms.Form):
    """
    Formulário de busca para usuários
    """
    q = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome, CPF ou e-mail...'
        })
    )
    
    tipo_usuario = forms.ChoiceField(
        label='Tipo de Usuário',
        required=False,
        choices=[('', 'Todos')] + Usuario.TIPO_USUARIO_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    ativo = forms.ChoiceField(
        label='Status',
        required=False,
        choices=[
            ('', 'Todos'),
            ('true', 'Ativo'),
            ('false', 'Inativo')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    data_criacao_inicio = forms.DateField(
        label='Data de Criação (Início)',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control'
        })
    )
    
    data_criacao_fim = forms.DateField(
        label='Data de Criação (Fim)',
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control'
        })
    )


def generate_secure_password(length=8):
    """
    Gera uma senha segura seguindo o padrão do sistema
    Padrão: 2 letras maiúsculas + 2 letras minúsculas + 2 números + 2 caracteres especiais
    """
    # Padrão: 2 letras maiúsculas + 2 letras minúsculas + 2 números + 2 caracteres especiais
    letras_maiusculas = ''.join(secrets.choice(string.ascii_uppercase) for _ in range(2))
    letras_minusculas = ''.join(secrets.choice(string.ascii_lowercase) for _ in range(2))
    numeros = ''.join(secrets.choice(string.digits) for _ in range(2))
    caracteres_especiais = ''.join(secrets.choice('!@#$%^&*') for _ in range(2))
    
    # Combinar e embaralhar
    senha = letras_maiusculas + letras_minusculas + numeros + caracteres_especiais
    senha_lista = list(senha)
    secrets.SystemRandom().shuffle(senha_lista)
    
    return ''.join(senha_lista)


# =============================================================================
# FORMULÁRIOS PARA ATAS DE REUNIÃO - EDITOR AVANÇADO
# =============================================================================

class AtaReuniaoEditorForm(forms.ModelForm):
    """
    Formulário avançado para atas de reunião com editor similar ao SEI
    Sistema completo com editor de texto rico e funcionalidades avançadas
    """
    
    def clean_conteudo_completo(self):
        conteudo = self.cleaned_data.get('conteudo_completo')
        # Permitir conteúdo vazio para criação inicial
        return conteudo
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Debug: imprimir dados do formulário
        print("=" * 50)
        print("DEBUG AtaReuniaoEditorForm.clean()")
        print(f"cleaned_data: {cleaned_data}")
        print(f"errors: {self.errors}")
        print("=" * 50)
        
        return cleaned_data
    
    class Meta:
        from diretoria.models import AtaReuniao
        model = AtaReuniao
        fields = [
            'titulo', 'tipo_reuniao', 'data_reuniao', 'local',
            'presidente', 'secretario', 'pauta', 'deliberacoes', 
            'observacoes', 'conteudo_completo'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título da reunião',
                'id': 'titulo-edit'
            }),
            'tipo_reuniao': forms.Select(attrs={
                'class': 'form-select',
                'id': 'tipo-reuniao-edit'
            }),
            'data_reuniao': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'id': 'id_data_reuniao'
            }),
            'local': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Cidade-UF',
                'id': 'local-edit'
            }),
            'presidente': forms.Select(attrs={
                'class': 'form-select',
                'id': 'presidente-edit'
            }),
            'secretario': forms.Select(attrs={
                'class': 'form-select',
                'id': 'secretario-edit'
            }),
            'pauta': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Pauta da reunião',
                'id': 'pauta-edit'
            }),
            'deliberacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Deliberações da reunião',
                'id': 'deliberacoes-edit'
            }),
            'observacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observações adicionais',
                'id': 'observacoes-edit'
            }),
            'conteudo_completo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 20,
                'placeholder': 'Conteúdo completo da ata com formatação avançada',
                'id': 'id_conteudo_completo_editor',
                'required': False
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar campos obrigatórios
        self.fields['titulo'].required = True
        self.fields['tipo_reuniao'].required = True
        self.fields['data_reuniao'].required = True
        self.fields['local'].required = True
        self.fields['pauta'].required = True
        self.fields['deliberacoes'].required = True
        self.fields['conteudo_completo'].required = False
        
        # Configurar labels personalizados
        self.fields['local'].label = 'Cidade-UF'
        
        # Configurar opções do tipo de reunião
        try:
            from diretoria.models import AtaReuniao
            self.fields['tipo_reuniao'].choices = AtaReuniao.TIPO_REUNIAO_CHOICES
        except ImportError:
            pass
        
        # Configurar querysets para presidente e secretario
        try:
            from diretoria.models import MembroDiretoria
            membros_ativos = MembroDiretoria.objects.filter(ativo=True).select_related('associado', 'cargo')
            self.fields['presidente'].queryset = membros_ativos
            self.fields['secretario'].queryset = membros_ativos
        except ImportError:
            pass
        
        # Definir valor padrão para data_reuniao se não estiver preenchido
        if not self.instance.pk:  # Apenas para novas atas
            from django.utils import timezone
            self.fields['data_reuniao'].initial = timezone.now()
    
    def clean_conteudo_completo(self):
        """Validação do conteúdo completo"""
        conteudo = self.cleaned_data.get('conteudo_completo', '').strip()
        # Campo é opcional, não precisa validar se está vazio
        return conteudo


class AtaReuniaoTemplateForm(forms.Form):
    """
    Formulário para seleção de templates de atas
    """
    TEMPLATE_CHOICES = [
        ('', 'Selecione um template...'),
        ('basico', 'Ata Básica - Estrutura Simples'),
        ('completa', 'Ata Completa - Formato Oficial'),
        ('extraordinaria', 'Reunião Extraordinária'),
        ('emergencia', 'Reunião de Emergência'),
        ('aprovacao', 'Ata de Aprovação de Contas'),
        ('eleicao', 'Ata de Eleição'),
        ('custom', 'Template Personalizado')
    ]
    
    template = forms.ChoiceField(
        choices=TEMPLATE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_template_ata',
            'onchange': 'aplicarTemplateAta()'
        }),
        label='Template da Ata'
    )
    
    titulo_template = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Título personalizado para a ata',
            'id': 'id_titulo_template'
        }),
        label='Título Personalizado'
    )


class AtaReuniaoSearchForm(forms.Form):
    """
    Formulário de busca e filtros para atas de reunião
    """
    
    # Campo de busca
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por título, local ou conteúdo...',
            'id': 'search_atas'
        }),
        label='Buscar'
    )
    
    # Filtros
    tipo_reuniao = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos os tipos')] + [
            ('ordinaria', 'Reunião Ordinária'),
            ('extraordinaria', 'Reunião Extraordinária'),
            ('emergencia', 'Reunião de Emergência'),
            ('especial', 'Reunião Especial'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'filtro_tipo'
        }),
        label='Tipo de Reunião'
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'data_inicio'
        }),
        label='Data Início'
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'data_fim'
        }),
        label='Data Fim'
    )
    
    aprovada = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Todas'),
            ('true', 'Aprovadas'),
            ('false', 'Não Aprovadas')
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'filtro_aprovacao'
        }),
        label='Status de Aprovação'
    )
    
    def clean(self):
        """Validação cruzada dos campos"""
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        if data_inicio and data_fim and data_inicio > data_fim:
            raise forms.ValidationError('Data de início deve ser anterior à data de fim.')
        
        return cleaned_data


# =============================================================================
# FORMULÁRIOS PARA DOCUMENTOS DE PROCESSOS JURÍDICOS
# =============================================================================

class DocumentoProcessoForm(forms.ModelForm):
    """
    Formulário para upload de documentos em processos jurídicos
    Sistema completo com validações e funcionalidades avançadas
    """
    
    class Meta:
        from assejus.models import DocumentoJuridico
        model = DocumentoJuridico
        fields = ['titulo', 'tipo_documento', 'descricao', 'arquivo']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Petição Inicial, Sentença, Despacho...',
                'maxlength': '200'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_documento'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição detalhada do documento (opcional)',
                'maxlength': '1000'
            }),
            'arquivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.txt,.rtf',
                'id': 'id_arquivo_single'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Extrair parâmetros específicos
        self.processo_id = kwargs.pop('processo_id', None)
        self.usuario = kwargs.pop('usuario', None)
        
        super().__init__(*args, **kwargs)
        
        # Se processo_id foi fornecido, pré-selecionar
        if self.processo_id:
            try:
                from assejus.models import ProcessoJuridico
                processo = ProcessoJuridico.objects.get(pk=self.processo_id)
                self.processo_info = processo
                print(f"✅ Processo pré-selecionado: {processo.numero_processo}")
            except ProcessoJuridico.DoesNotExist:
                print(f"❌ Processo com ID {self.processo_id} não encontrado")
        
        # Adicionar classes CSS e configurações
        self._configurar_widgets()
    
    def _configurar_widgets(self):
        """Configura widgets com classes CSS e atributos"""
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'attrs'):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
                elif 'form-control' not in field.widget.attrs['class']:
                    field.widget.attrs['class'] += ' form-control'
    
    def clean_arquivo(self):
        """Validação do arquivo único"""
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            return self._validar_arquivo(arquivo)
        return arquivo
    

    
    def _validar_arquivo(self, arquivo):
        """Validação comum para arquivos"""
        if not arquivo:
            return arquivo
        
        # Verificar tamanho (máx. 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if arquivo.size > max_size:
            raise forms.ValidationError(
                f'Arquivo muito grande. Tamanho máximo permitido: 10MB. '
                f'Tamanho atual: {arquivo.size / (1024*1024):.1f}MB'
            )
        
        # Verificar extensão
        extensoes_permitidas = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.txt', '.rtf']
        nome_arquivo = arquivo.name.lower()
        if not any(nome_arquivo.endswith(ext) for ext in extensoes_permitidas):
            raise forms.ValidationError(
                f'Formato de arquivo não permitido. '
                f'Formatos aceitos: {", ".join(extensoes_permitidas)}'
            )
        
        # Validação de nome do arquivo removida - aceita qualquer nome
        
        return arquivo
    
    def clean_titulo(self):
        """Validação do título"""
        titulo = self.cleaned_data.get('titulo', '').strip()
        if not titulo:
            raise forms.ValidationError('Título é obrigatório.')
        
        if len(titulo) < 3:
            raise forms.ValidationError('Título deve ter pelo menos 3 caracteres.')
        
        return titulo
    
    def save(self, commit=True):
        """Salva o documento com metadados adicionais"""
        documento = super().save(commit=False)
        
        # Definir processo se fornecido
        if self.processo_id:
            from assejus.models import ProcessoJuridico
            documento.processo_id = self.processo_id
        
        # Definir usuário que fez upload
        if self.usuario:
            documento.usuario_upload = self.usuario
        
        if commit:
            documento.save()
        
        return documento


class DocumentoProcessoMultiploForm(forms.Form):
    """
    Formulário para upload múltiplo de documentos
    """
    
    tipo_documento = forms.ChoiceField(
        choices=[
            ('peticao', 'Petição'),
            ('sentenca', 'Sentença'),
            ('despacho', 'Despacho'),
            ('certidao', 'Certidão'),
            ('contrato', 'Contrato'),
            ('comprovante', 'Comprovante'),
            ('outro', 'Outro'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_tipo_documento_multiplo'
        }),
        label='Tipo de Documento'
    )
    
    descricao = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Descrição geral para todos os documentos (opcional)',
            'maxlength': '1000'
        }),
        label='Descrição Geral'
    )
    
    def __init__(self, *args, **kwargs):
        self.processo_id = kwargs.pop('processo_id', None)
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        # Validações específicas para upload múltiplo podem ser adicionadas aqui
        return cleaned_data



class DocumentoProcessoSearchForm(forms.Form):
    """
    Formulário de busca e filtros para documentos de processos
    """
    
    # Campo de busca
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por título, descrição ou número do processo...',
            'id': 'search_documentos'
        }),
        label='Buscar'
    )
    
    # Filtros
    tipo_documento = forms.ChoiceField(
        required=False,
        choices=[('', 'Todos os tipos')] + [
            ('peticao', 'Petição'),
            ('sentenca', 'Sentença'),
            ('despacho', 'Despacho'),
            ('certidao', 'Certidão'),
            ('contrato', 'Contrato'),
            ('comprovante', 'Comprovante'),
            ('outro', 'Outro'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'filtro_tipo'
        }),
        label='Tipo de Documento'
    )
    
    processo = forms.ModelChoiceField(
        required=False,
        queryset=None,  # Será definido no __init__
        empty_label='Todos os processos',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'filtro_processo'
        }),
        label='Processo'
    )
    
    data_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'data_inicio'
        }),
        label='Data Início'
    )
    
    data_fim = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'id': 'data_fim'
        }),
        label='Data Fim'
    )
    
    usuario_upload = forms.ModelChoiceField(
        required=False,
        queryset=None,  # Será definido no __init__
        empty_label='Todos os usuários',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'filtro_usuario'
        }),
        label='Usuário Upload'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Definir querysets dinâmicos
        try:
            from assejus.models import ProcessoJuridico
            from django.contrib.auth.models import User
            
            self.fields['processo'].queryset = ProcessoJuridico.objects.all().order_by('-data_cadastro')
            self.fields['usuario_upload'].queryset = User.objects.filter(
                documentos_upload__isnull=False
            ).distinct().order_by('first_name', 'last_name')
        except ImportError:
            pass
    
    def clean(self):
        """Validação cruzada dos campos"""
        cleaned_data = super().clean()
        data_inicio = cleaned_data.get('data_inicio')
        data_fim = cleaned_data.get('data_fim')
        
        if data_inicio and data_fim and data_inicio > data_fim:
            raise forms.ValidationError('Data de início deve ser anterior à data de fim.')
        
        return cleaned_data


class DocumentoProcessoEditForm(forms.ModelForm):
    """
    Formulário para edição de documentos existentes
    """
    
    class Meta:
        from assejus.models import DocumentoJuridico
        model = DocumentoJuridico
        fields = ['titulo', 'tipo_documento', 'descricao']
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título do documento',
                'maxlength': '200'
            }),
            'tipo_documento': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descrição do documento',
                'maxlength': '1000'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Adicionar classes CSS
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'attrs'):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'
                elif 'form-control' not in field.widget.attrs['class']:
                    field.widget.attrs['class'] += ' form-control'
    
    def clean_titulo(self):
        """Validação do título"""
        titulo = self.cleaned_data.get('titulo', '').strip()
        if not titulo:
            raise forms.ValidationError('Título é obrigatório.')
        
        if len(titulo) < 3:
            raise forms.ValidationError('Título deve ter pelo menos 3 caracteres.')
        
        return titulo


class DocumentoProcessoReplaceForm(forms.ModelForm):
    """
    Formulário para substituir arquivo de documento existente
    """
    
    class Meta:
        from assejus.models import DocumentoJuridico
        model = DocumentoJuridico
        fields = ['arquivo']
        widgets = {
            'arquivo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.txt,.rtf',
                'id': 'id_novo_arquivo'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['arquivo'].required = True
        self.fields['arquivo'].help_text = 'Selecione o novo arquivo (máx. 10MB)'
    
    def clean_arquivo(self):
        """Validação do novo arquivo"""
        arquivo = self.cleaned_data.get('arquivo')
        if arquivo:
            # Usar a mesma validação do formulário principal
            form_doc = DocumentoProcessoForm()
            return form_doc._validar_arquivo(arquivo)
        return arquivo


class ExPresidenteForm(forms.ModelForm):
    """
    Formulário para gerenciar ex-presidentes
    """
    
    class Meta:
        from .models import ExPresidente
        model = ExPresidente
        fields = [
            'nome', 'posto_graduacao', 'foto', 'periodo_inicio', 
            'periodo_fim', 'biografia', 'principais_realizacoes', 
            'ativo', 'ordem_exibicao'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome completo do ex-presidente'
            }),
            'posto_graduacao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Coronel, Tenente-Coronel, etc.'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'periodo_inicio': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'periodo_fim': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'biografia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Biografia do ex-presidente...'
            }),
            'principais_realizacoes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Principais realizações durante o mandato...'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ordem_exibicao': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Ordem de exibição (0 = primeiro)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['foto'].required = False
        self.fields['biografia'].required = False
        self.fields['principais_realizacoes'].required = False


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class HistoriaAssociacaoForm(forms.ModelForm):
    """
    Formulário para gerenciar marcos históricos da associação
    """
    # Campo para upload múltiplo de imagens
    imagens_galeria = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*',
            'multiple': True
        }),
        required=False,
        help_text="Selecione múltiplas imagens para a galeria (Ctrl+clique para selecionar várias)"
    )
    
    class Meta:
        from .models import HistoriaAssociacao
        model = HistoriaAssociacao
        fields = [
            'titulo', 'descricao', 'data_marcante', 'tipo', 
            'imagem', 'ativo', 'destaque', 'ordem_exibicao'
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Título do marco histórico'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Descrição detalhada do marco histórico...'
            }),
            'data_marcante': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }, format='%Y-%m-%d'),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            }),
            'imagem': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'destaque': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ordem_exibicao': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': 'Ordem de exibição (0 = primeiro)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['imagem'].required = False
        self.fields['imagens_galeria'].required = False
        
        # Garantir que a data seja carregada corretamente para edição
        if self.instance and self.instance.pk and hasattr(self.instance, 'data_marcante') and self.instance.data_marcante:
            # Converter para string no formato YYYY-MM-DD para input type="date"
            formatted_date = self.instance.data_marcante.strftime('%Y-%m-%d')
            # Definir o valor inicial
            self.fields['data_marcante'].initial = formatted_date
            # Forçar o valor no widget
            self.fields['data_marcante'].widget.attrs.update({'value': formatted_date})
    
    def clean_data_marcante(self):
        """Garantir que a data seja validada corretamente"""
        data = self.cleaned_data.get('data_marcante')
        if data:
            return data
        return None


