from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import TemplateAta, AtaReuniao, MembroDiretoria
from .forms import AtaReuniaoForm


@method_decorator(login_required, name='dispatch')
class TemplateListView(View):
    """
    API para listar templates de ata
    """
    def get(self, request):
        templates = TemplateAta.objects.filter(ativo=True)
        data = []
        for template in templates:
            data.append({
                'id': template.id,
                'nome': template.nome,
                'descricao': template.descricao,
                'conteudo': template.conteudo
            })
        return JsonResponse(data, safe=False)


@method_decorator(login_required, name='dispatch')
class MembroDiretoriaListView(View):
    """
    API para listar membros da diretoria
    """
    def get(self, request):
        membros = MembroDiretoria.objects.filter(ativo=True).select_related('associado', 'cargo')
        data = []
        for membro in membros:
            data.append({
                'id': membro.id,
                'nome': membro.associado.nome,
                'cargo': membro.cargo.nome
            })
        return JsonResponse(data, safe=False)


@method_decorator(login_required, name='dispatch')
class AtaDetailView(View):
    """
    API para obter detalhes de uma ata
    """
    def get(self, request, pk):
        try:
            ata = AtaReuniao.objects.get(pk=pk)
            data = {
                'id': ata.id,
                'titulo': ata.titulo,
                'tipo_reuniao': ata.tipo_reuniao,
                'data_reuniao': ata.data_reuniao.strftime('%Y-%m-%dT%H:%M') if ata.data_reuniao else '',
                'local': ata.local,
                'presidente': ata.presidente.id if ata.presidente else None,
                'secretario': ata.secretario.id if ata.secretario else None,
                'membros_presentes': list(ata.membros_presentes.values_list('id', flat=True)),
                'membros_ausentes': list(ata.membros_ausentes.values_list('id', flat=True)),
                'conteudo_completo': ata.conteudo_completo or '',
                'pauta': ata.pauta or '',
                'deliberacoes': ata.deliberacoes or '',
                'observacoes': ata.observacoes or ''
            }
            return JsonResponse(data)
        except AtaReuniao.DoesNotExist:
            return JsonResponse({'error': 'Ata não encontrada'}, status=404)


@csrf_exempt
@login_required
@require_http_methods(["POST", "PUT"])
def salvar_ata_api(request, pk=None):
    """
    API para salvar/criar ata
    """
    try:
        if request.method == 'POST':
            # Criar nova ata
            form = AtaReuniaoForm(request.POST, request.FILES)
        else:
            # Atualizar ata existente
            try:
                ata = AtaReuniao.objects.get(pk=pk)
                form = AtaReuniaoForm(request.POST, request.FILES, instance=ata)
            except AtaReuniao.DoesNotExist:
                return JsonResponse({'error': 'Ata não encontrada'}, status=404)
        
        if form.is_valid():
            ata = form.save()
            return JsonResponse({
                'success': True,
                'message': 'Ata salva com sucesso!',
                'ata_id': ata.id
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@login_required
@require_http_methods(["POST"])
def salvar_conteudo_ata(request, pk):
    """
    API para salvar apenas o conteúdo da ata
    """
    try:
        import json
        data = json.loads(request.body)
        conteudo = data.get('conteudo', '')
        
        try:
            ata = AtaReuniao.objects.get(pk=pk)
            ata.conteudo_completo = conteudo
            ata.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Conteúdo salvo com sucesso!'
            })
        except AtaReuniao.DoesNotExist:
            return JsonResponse({'error': 'Ata não encontrada'}, status=404)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
