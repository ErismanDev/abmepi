from django import template
import os

register = template.Library()

@register.filter
def filename(value):
    """
    Extrai apenas o nome do arquivo de um caminho completo
    """
    if not value:
        return ''
    return os.path.basename(str(value))

@register.filter
def filesize(value):
    """
    Converte bytes para formato legível (KB, MB, GB)
    """
    if not value:
        return '0 B'
    
    try:
        size = value.size
    except AttributeError:
        return '0 B'
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"
