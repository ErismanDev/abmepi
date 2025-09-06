from django.db import models

class ConfiguracaoCobranca(models.Model):
    """
    Configurações para cobrança e carnê de pagamento
    """
    nome = models.CharField(max_length=100, help_text="Nome da configuração (ex: Configuração Padrão)")
    ativo = models.BooleanField(default=True, help_text="Configuração ativa para uso")
    
    # Dados de cobrança
    chave_pix = models.CharField(max_length=100, help_text="Chave PIX para pagamento")
    titular = models.CharField(max_length=100, help_text="Nome do titular da conta")
    banco = models.CharField(max_length=100, help_text="Nome do banco ou instituição")
    
    # Mensagem personalizada
    mensagem_linha1 = models.CharField(max_length=100, default="Pague Suas mensalidade na sede da", help_text="Primeira linha da mensagem")
    mensagem_linha2 = models.CharField(max_length=100, default="associação ou pelo QRcode e mande o", help_text="Segunda linha da mensagem")
    mensagem_linha3 = models.CharField(max_length=100, default="comprovante para", help_text="Terceira linha da mensagem")
    telefone_comprovante = models.CharField(max_length=20, default="86 988197790", help_text="Telefone para envio do comprovante")
    
    # Configurações do QR Code
    qr_code_ativo = models.BooleanField(default=True, help_text="Exibir QR Code no carnê")
    qr_code_tamanho = models.IntegerField(default=15, help_text="Tamanho do QR Code em mm")
    
    # Configurações gerais
    data_criacao = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Configuração de Cobrança"
        verbose_name_plural = "Configurações de Cobrança"
        ordering = ['-ativo', '-data_criacao']
    
    def __str__(self):
        return f"{self.nome} {'(Ativo)' if self.ativo else '(Inativo)'}"
    
    def get_mensagem_completa(self):
        """Retorna a mensagem completa formatada"""
        return f"{self.mensagem_linha1}\n{self.mensagem_linha2}\n{self.mensagem_linha3} {self.telefone_comprovante}"
    
    def get_configuracao_ativa(self):
        """Retorna a configuração ativa ou cria uma padrão"""
        config = ConfiguracaoCobranca.objects.filter(ativo=True).first()
        if not config:
            # Criar configuração padrão se não existir
            config = ConfiguracaoCobranca.objects.create(
                nome="Configuração Padrão",
                ativo=True,
                chave_pix="86 988197790",
                titular="Gustavo Henrique de Araujo Sousa",
                banco="MERCADO PAGO"
            )
        return config
