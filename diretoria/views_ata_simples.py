from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.core.files.base import ContentFile
import os

from .models_ata_simples import AtaSimples
from .forms_ata_simples import AtaSimplesForm, AtaEditorForm, AtaEditorAvancadoForm

class AtaSimplesListView(LoginRequiredMixin, ListView):
    """
    Lista de atas simples
    """
    model = AtaSimples
    template_name = 'diretoria/ata_simples_list.html'
    context_object_name = 'atas'
    paginate_by = 20
    
    def get_queryset(self):
        return AtaSimples.objects.all().order_by('-data_reuniao')

class AtaSimplesCreateView(LoginRequiredMixin, CreateView):
    """
    Criar nova ata simples
    """
    model = AtaSimples
    form_class = AtaSimplesForm
    template_name = 'diretoria/ata_simples_create.html'
    
    def form_valid(self, form):
        form.instance.criado_por = self.request.user
        response = super().form_valid(form)
        
        # Gerar HTML automaticamente
        self.object.conteudo_html = self.object.gerar_html()
        self.object.save()
        
        messages.success(
            self.request, 
            f'Ata "{self.object.titulo}" criada com sucesso! Agora você pode editá-la.'
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy('diretoria:ata_simples_edit', kwargs={'pk': self.object.pk})

class AtaSimplesEditView(LoginRequiredMixin, UpdateView):
    """
    Editar ata simples
    """
    model = AtaSimples
    form_class = AtaSimplesForm
    template_name = 'diretoria/ata_simples_edit.html'
    context_object_name = 'ata'
    
    def get_success_url(self):
        return reverse_lazy('diretoria:ata_simples_edit', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Regenerar HTML quando dados básicos mudam
        self.object.conteudo_html = self.object.gerar_html()
        self.object.save()
        
        messages.success(
            self.request, 
            f'Ata "{self.object.titulo}" atualizada com sucesso!'
        )
        return response

class AtaEditorView(LoginRequiredMixin, UpdateView):
    """
    Editor de conteúdo em texto da ata
    """
    model = AtaSimples
    form_class = AtaEditorForm
    template_name = 'diretoria/ata_editor_texto.html'
    context_object_name = 'ata'
    
    def get_success_url(self):
        return reverse_lazy('diretoria:ata_simples_view', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Regenerar HTML com base no conteúdo editado
        self.object.conteudo_html = self.object.gerar_html()
        self.object.save()
        
        # Salvar arquivo HTML
        self.salvar_arquivo_html()
        
        messages.success(
            self.request, 
            f'Conteúdo da ata "{self.object.titulo}" salvo com sucesso!'
        )
        return response
    
    def salvar_arquivo_html(self):
        """Salva o conteúdo HTML em arquivo"""
        if self.object.conteudo_html:
            filename = f"{self.object.titulo_slug}.html"
            content = ContentFile(self.object.conteudo_html.encode('utf-8'))
            self.object.arquivo_html.save(filename, content, save=True)


class AtaEditorAvancadoView(LoginRequiredMixin, UpdateView):
    """
    Editor avançado de conteúdo HTML da ata (estilo SEI)
    """
    model = AtaSimples
    form_class = AtaEditorAvancadoForm
    template_name = 'diretoria/ata_editor_avancado.html'
    context_object_name = 'ata'
    
    def get_success_url(self):
        return reverse_lazy('diretoria:ata_simples_view', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Salvar arquivo HTML
        self.salvar_arquivo_html()
        
        messages.success(
            self.request, 
            f'Conteúdo da ata "{self.object.titulo}" salvo com sucesso!'
        )
        return response
    
    def salvar_arquivo_html(self):
        """Salva o conteúdo HTML em arquivo"""
        if self.object.conteudo_html:
            filename = f"{self.object.titulo_slug}.html"
            content = ContentFile(self.object.conteudo_html.encode('utf-8'))
            self.object.arquivo_html.save(filename, content, save=True)

class AtaSimplesDetailView(LoginRequiredMixin, DetailView):
    """
    Visualizar ata simples
    """
    model = AtaSimples
    template_name = 'diretoria/ata_simples_detail.html'
    context_object_name = 'ata'

@login_required
def visualizar_ata_html(request, pk):
    """
    Visualizar ata em HTML puro
    """
    ata = get_object_or_404(AtaSimples, pk=pk)
    
    if not ata.conteudo_html:
        ata.conteudo_html = ata.gerar_html()
        ata.save()
    
    return HttpResponse(ata.conteudo_html, content_type='text/html')

@login_required
def imprimir_ata(request, pk):
    """
    Página de impressão da ata
    """
    ata = get_object_or_404(AtaSimples, pk=pk)
    
    if not ata.conteudo_html:
        ata.conteudo_html = ata.gerar_html()
        ata.save()
    
    # Adicionar CSS específico para impressão
    html_impressao = ata.conteudo_html.replace(
        '<style>',
        '''<style>
        @media print {
            body { margin: 0; padding: 15px; }
            .no-print { display: none !important; }
            .print-only { display: block !important; }
        }
        .print-only { display: none; }
        '''
    )
    
    return HttpResponse(html_impressao, content_type='text/html')

@login_required
def baixar_ata_html(request, pk):
    """
    Baixar arquivo HTML da ata
    """
    ata = get_object_or_404(AtaSimples, pk=pk)
    
    if not ata.conteudo_html:
        ata.conteudo_html = ata.gerar_html()
        ata.save()
    
    # Salvar arquivo se não existir
    if not ata.arquivo_html:
        ata.salvar_arquivo_html()
    
    if ata.arquivo_html:
        response = HttpResponse(ata.arquivo_html.read(), content_type='text/html')
        response['Content-Disposition'] = f'attachment; filename="{ata.titulo_slug}.html"'
        return response
    
    # Fallback: gerar arquivo na hora
    response = HttpResponse(ata.conteudo_html, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="{ata.titulo_slug}.html"'
    return response

@login_required
def regenerar_html(request, pk):
    """
    Regenerar HTML da ata
    """
    ata = get_object_or_404(AtaSimples, pk=pk)
    
    # Regenerar HTML baseado nos dados atuais
    ata.conteudo_html = ata.gerar_html()
    ata.save()
    
    # Salvar arquivo
    ata.salvar_arquivo_html()
    
    messages.success(request, 'HTML da ata regenerado com sucesso!')
    return redirect('diretoria:ata_simples_edit', pk=pk)

@login_required
def finalizar_ata(request, pk):
    """
    Finalizar ata (mudar status para finalizada)
    """
    ata = get_object_or_404(AtaSimples, pk=pk)
    
    if request.method == 'POST':
        ata.status = 'finalizada'
        ata.save()
        
        messages.success(request, f'Ata "{ata.titulo}" finalizada com sucesso!')
        return redirect('diretoria:ata_simples_list')
    
    return render(request, 'diretoria/ata_finalizar_confirm.html', {'ata': ata})

@login_required
def assinar_ata(request, pk):
    """
    Assinar ata (mudar status para assinada)
    """
    ata = get_object_or_404(AtaSimples, pk=pk)
    
    if request.method == 'POST':
        ata.status = 'assinada'
        ata.save()
        
        messages.success(request, f'Ata "{ata.titulo}" assinada com sucesso!')
        return redirect('diretoria:ata_simples_list')
    
    return render(request, 'diretoria/ata_assinar_confirm.html', {'ata': ata})
