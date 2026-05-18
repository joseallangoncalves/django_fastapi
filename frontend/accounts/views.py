from django.shortcuts import render, redirect
from django.contrib import messages
from core.api_client import registrar_usuario, login_usuario, logout_usuario

def login_view(request):
    # Redirect to dashboard if user is already authenticated
    if request.session.get('access_token'):
        return redirect('dashboard')
        
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '').strip()
        
        if not email or not senha:
            messages.error(request, "Por favor, preencha todos os campos.")
            return render(request, 'accounts/login.html')
            
        res = login_usuario(email, senha)
        if res.get('success'):
            # Save auth token and user profile in Django session
            data = res['data']
            request.session['access_token'] = data['access_token']
            request.session['user_name'] = data['usuario']['nome']
            request.session['user_email'] = data['usuario']['email']
            request.session['user_role'] = data['usuario']['cargo']
            
            messages.success(request, f"Bem-vindo(a) de volta, {data['usuario']['nome']}!")
            return redirect('dashboard')
        else:
            messages.error(request, res.get('error', 'Credenciais inválidas.'))
            
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.session.get('access_token'):
        return redirect('dashboard')
        
    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip()
        senha = request.POST.get('senha', '').strip()
        confirm_senha = request.POST.get('confirm_senha', '').strip()
        
        if not nome or not email or not senha or not confirm_senha:
            messages.error(request, "Todos os campos são obrigatórios.")
            return render(request, 'accounts/register.html')
            
        if senha != confirm_senha:
            messages.error(request, "As senhas não coincidem.")
            return render(request, 'accounts/register.html')
            
        if len(senha) < 6:
            messages.error(request, "A senha deve conter no mínimo 6 caracteres.")
            return render(request, 'accounts/register.html')
            
        res = registrar_usuario(nome, email, senha)
        if res.get('success'):
            messages.success(request, "Conta criada com sucesso! Faça seu login abaixo.")
            return redirect('login')
        else:
            messages.error(request, res.get('error', "Erro no cadastro."))
            
    return render(request, 'accounts/register.html')

def logout_view(request):
    token = request.session.get('access_token')
    if token:
        logout_usuario(token)
    request.session.flush()
    messages.info(request, "Você encerrou sua sessão.")
    return redirect('login')
