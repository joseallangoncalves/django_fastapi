from django.shortcuts import render, redirect
from django.contrib import messages
from functools import wraps
from core.api_client import (
    executar_storyteller, executar_lecture_extractor, obter_historico,
    upload_contrato, obter_contratos, obter_contrato_por_id, atualizar_contrato, excluir_contrato
)

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

# --- CONTRATOS INTELIGENTES VIEWS ---

@auth_required
def contracts_list_view(request):
    token = request.session['access_token']
    res = obter_contratos(token)
    contratos = []
    if res.get('success'):
        contratos = res['data']
    else:
        messages.error(request, res.get('error', "Erro ao buscar contratos."))
        
    context = {
        'contratos': contratos,
        'contratos_count': len(contratos),
        'nome': request.session.get('user_name')
    }
    return render(request, 'portal/contracts_list.html', context)

@auth_required
def contract_upload_view(request):
    token = request.session['access_token']
    if request.method == 'POST':
        if 'file' not in request.FILES:
            messages.error(request, "Nenhum arquivo enviado.")
        else:
            file = request.FILES['file']
            messages.info(request, "Extraindo metadados do contrato com IA... Por favor, aguarde.")
            res = upload_contrato(file.name, file.read(), token)
            if res.get('success'):
                messages.success(request, "Contrato extraído e cadastrado com sucesso!")
                return redirect('contract_detail', contract_id=res['data']['id'])
            else:
                messages.error(request, res.get('error', "Falha ao processar o contrato."))
                
    context = {
        'nome': request.session.get('user_name')
    }
    return render(request, 'portal/contract_upload.html', context)

@auth_required
def contract_detail_view(request, contract_id):
    token = request.session['access_token']
    res = obter_contrato_por_id(contract_id, token)
    if not res.get('success'):
        messages.error(request, res.get('error', "Contrato não encontrado."))
        return redirect('contracts_list')
        
    context = {
        'contrato': res['data'],
        'nome': request.session.get('user_name')
    }
    return render(request, 'portal/contract_detail.html', context)

@auth_required
def contract_edit_view(request, contract_id):
    token = request.session['access_token']
    
    # 1. Carrega dados atuais
    res = obter_contrato_por_id(contract_id, token)
    if not res.get('success'):
        messages.error(request, "Contrato não encontrado.")
        return redirect('contracts_list')
    contrato = res['data']
    
    if request.method == 'POST':
        # 2. Constrói payload de atualização
        payload = {
            "numero_contrato": request.POST.get('numero_contrato', '').strip(),
            "contratante": request.POST.get('contratante', '').strip(),
            "contratado": request.POST.get('contratado', '').strip(),
            "valor_total": float(request.POST.get('valor_total') or 0.0),
            "moeda": request.POST.get('moeda', 'BRL').strip(),
            "resumo": request.POST.get('resumo', '').strip(),
            "observacoes": request.POST.get('observacoes', '').strip()
        }
        
        # Datas precisam ser enviadas no formato YYYY-MM-DD ou nulas
        data_inicio_str = request.POST.get('data_inicio')
        if data_inicio_str:
            payload["data_inicio"] = data_inicio_str
            
        data_fim_str = request.POST.get('data_fim')
        if data_fim_str:
            payload["data_fim"] = data_fim_str
            
        res_update = atualizar_contrato(contract_id, payload, token)
        if res_update.get('success'):
            messages.success(request, "Contrato atualizado com sucesso!")
            return redirect('contract_detail', contract_id=contract_id)
        else:
            messages.error(request, res_update.get('error', "Erro ao atualizar contrato."))
            contrato = payload  # Preserva os campos preenchidos pelo usuário em caso de erro
            
    # Formatação de datas de vigência para preenchimento correto no input date do HTML
    # Exemplo de data retornada do FastAPI: '2026-05-18T00:00:00' -> extrai '2026-05-18'
    if 'data_inicio' in contrato and contrato['data_inicio']:
        contrato['data_inicio_iso'] = contrato['data_inicio'].split('T')[0]
    if 'data_fim' in contrato and contrato['data_fim']:
        contrato['data_fim_iso'] = contrato['data_fim'].split('T')[0]
        
    context = {
        'contrato': contrato,
        'nome': request.session.get('user_name')
    }
    return render(request, 'portal/contract_edit.html', context)

@auth_required
def contract_delete_view(request, contract_id):
    token = request.session['access_token']
    res = excluir_contrato(contract_id, token)
    if res.get('success'):
        messages.success(request, "Contrato removido com sucesso!")
    else:
        messages.error(request, res.get('error', "Erro ao excluir contrato."))
    return redirect('contracts_list')
