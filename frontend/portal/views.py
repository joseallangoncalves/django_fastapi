from django.shortcuts import render, redirect
from django.contrib import messages
from functools import wraps
from core.api_client import executar_storyteller, executar_lecture_extractor, obter_historico

def auth_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('access_token'):
            messages.warning(request, "Por favor, faça login para acessar esta página.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

@auth_required
def dashboard_view(request):
    token = request.session['access_token']
    res = obter_historico(token)
    
    logs = []
    if res.get('success'):
        logs = res['data']
        
    context = {
        'nome': request.session.get('user_name'),
        'email': request.session.get('user_email'),
        'cargo': request.session.get('user_role'),
        'logs': logs,
        'logs_count': len(logs)
    }
    return render(request, 'portal/dashboard.html', context)

@auth_required
def storyteller_view(request):
    token = request.session['access_token']
    story = None
    tema = ""
    
    if request.method == 'POST':
        tema = request.POST.get('tema', '').strip()
        if not tema:
            messages.error(request, "Por favor, digite um tema.")
        else:
            messages.info(request, "Processando tema com o Agente de IA...")
            res = executar_storyteller(tema, token)
            if res.get('success'):
                story = res['data']['historia']
                messages.success(request, "História gerada com sucesso!")
            else:
                messages.error(request, res.get('error', "Erro na geração."))
                
    context = {
        'story': story,
        'tema': tema,
        'nome': request.session.get('user_name')
    }
    return render(request, 'portal/storyteller.html', context)

@auth_required
def lecture_extractor_view(request):
    token = request.session['access_token']
    aula = None
    transcricao = ""
    
    if request.method == 'POST':
        transcricao = request.POST.get('transcricao', '').strip()
        if not transcricao:
            messages.error(request, "Por favor, cole a transcrição da aula.")
        else:
            messages.info(request, "Extraindo tópicos de aula com o padrão T-E-C...")
            res = executar_lecture_extractor(transcricao, token)
            if res.get('success'):
                aula = res['data']
                messages.success(request, "Aula processada e organizada com sucesso!")
            else:
                messages.error(request, res.get('error', "Erro no processamento da aula."))
                
    context = {
        'aula': aula,
        'transcricao': transcricao,
        'nome': request.session.get('user_name')
    }
    return render(request, 'portal/lecture_extractor.html', context)
