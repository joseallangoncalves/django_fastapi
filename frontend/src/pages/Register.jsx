import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sparkles, User, Mail, Lock, Shield } from 'lucide-react';
import api from '../services/api';
import LoadingOverlay from '../components/LoadingOverlay';

function Register() {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmSenha, setConfirmSenha] = useState('');
  const [cargo, setCargo] = useState('user');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (senha.length < 6) {
      setError('A senha deve ter no mínimo 6 caracteres.');
      setLoading(false);
      return;
    }

    if (senha !== confirmSenha) {
      setError('As senhas digitadas não coincidem.');
      setLoading(false);
      return;
    }

    try {
      await api.post('/usuarios/', { 
        nome, 
        email, 
        senha, 
        cargo 
      });
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2500);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || 
        'Erro ao registrar usuário. Tente novamente mais tarde.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <LoadingOverlay show={loading} text="Criando sua conta..." />

      <div className="glass-card auth-card">
        <div className="auth-header">
          <div className="auth-logo">
            <Sparkles size={26} color="#fff" />
          </div>
          <h1 className="auth-title">Criar Conta</h1>
          <p className="auth-subtitle">Cadastre-se para obter acesso à plataforma</p>
        </div>

        {error && (
          <div 
            style={{ 
              background: 'rgba(255, 76, 76, 0.15)', 
              border: '1px solid rgba(255, 76, 76, 0.3)', 
              color: '#ff4c4c', 
              padding: '0.85rem 1rem', 
              borderRadius: '10px', 
              marginBottom: '1.5rem',
              fontSize: '0.9rem',
              textAlign: 'center'
            }}
          >
            {error}
          </div>
        )}

        {success && (
          <div 
            style={{ 
              background: 'rgba(46, 213, 115, 0.15)', 
              border: '1px solid rgba(46, 213, 115, 0.3)', 
              color: '#2ed573', 
              padding: '0.85rem 1rem', 
              borderRadius: '10px', 
              marginBottom: '1.5rem',
              fontSize: '0.9rem',
              textAlign: 'center',
              fontWeight: 600
            }}
          >
            Cadastro realizado com sucesso! Redirecionando para login...
          </div>
        )}

        <form onSubmit={handleRegister}>
          <div className="form-group">
            <label className="form-label" htmlFor="nome">Nome Completo</label>
            <div style={{ position: 'relative' }}>
              <User 
                size={18} 
                style={{ 
                  position: 'absolute', 
                  left: '1rem', 
                  top: '50%', 
                  transform: 'translateY(-50%)', 
                  color: 'var(--text-muted)' 
                }} 
              />
              <input
                id="nome"
                type="text"
                required
                className="form-input"
                style={{ paddingLeft: '2.75rem' }}
                placeholder="Seu nome"
                value={nome}
                onChange={(e) => setNome(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="email">E-mail Corporativo</label>
            <div style={{ position: 'relative' }}>
              <Mail 
                size={18} 
                style={{ 
                  position: 'absolute', 
                  left: '1rem', 
                  top: '50%', 
                  transform: 'translateY(-50%)', 
                  color: 'var(--text-muted)' 
                }} 
              />
              <input
                id="email"
                type="email"
                required
                className="form-input"
                style={{ paddingLeft: '2.75rem' }}
                placeholder="nome@empresa.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="cargo">Cargo / Função</label>
            <div style={{ position: 'relative' }}>
              <Shield 
                size={18} 
                style={{ 
                  position: 'absolute', 
                  left: '1rem', 
                  top: '50%', 
                  transform: 'translateY(-50%)', 
                  color: 'var(--text-muted)' 
                }} 
              />
              <select
                id="cargo"
                className="form-input"
                style={{ paddingLeft: '2.75rem', appearance: 'none', background: '#121320' }}
                value={cargo}
                onChange={(e) => setCargo(e.target.value)}
              >
                <option value="user">Usuário Comum</option>
                <option value="admin">Administrador</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="senha">Senha</label>
            <div style={{ position: 'relative' }}>
              <Lock 
                size={18} 
                style={{ 
                  position: 'absolute', 
                  left: '1rem', 
                  top: '50%', 
                  transform: 'translateY(-50%)', 
                  color: 'var(--text-muted)' 
                }} 
              />
              <input
                id="senha"
                type="password"
                required
                className="form-input"
                style={{ paddingLeft: '2.75rem' }}
                placeholder="Mínimo 6 caracteres"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="confirmSenha">Confirmar Senha</label>
            <div style={{ position: 'relative' }}>
              <Lock 
                size={18} 
                style={{ 
                  position: 'absolute', 
                  left: '1rem', 
                  top: '50%', 
                  transform: 'translateY(-50%)', 
                  color: 'var(--text-muted)' 
                }} 
              />
              <input
                id="confirmSenha"
                type="password"
                required
                className="form-input"
                style={{ paddingLeft: '2.75rem' }}
                placeholder="Repita a senha"
                value={confirmSenha}
                onChange={(e) => setConfirmSenha(e.target.value)}
              />
            </div>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%', marginTop: '1rem', padding: '0.85rem' }}
          >
            Registrar e Entrar
          </button>
        </form>

        <div className="auth-footer">
          Já tem conta? <Link to="/login" className="auth-link">Faça Login</Link>
        </div>
      </div>
    </div>
  );
}

export default Register;
