import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sparkles, Mail, Lock } from 'lucide-react';
import api from '../services/api';
import LoadingOverlay from '../components/LoadingOverlay';

function Login() {
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await api.post('/auth/login', { email, senha });
      const { access_token, usuario } = response.data;
      
      // Save token & user profile details to localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(usuario));
      
      navigate('/');
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || 
        'Erro ao conectar com o servidor. Verifique suas credenciais.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <LoadingOverlay show={loading} text="Autenticando..." />

      <div className="glass-card auth-card">
        <div className="auth-header">
          <div className="auth-logo">
            <Sparkles size={26} color="#fff" />
          </div>
          <h1 className="auth-title">Augenet AI</h1>
          <p className="auth-subtitle">Entre na sua conta para acessar o portal</p>
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

        <form onSubmit={handleLogin}>
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
            <label className="form-label" htmlFor="senha">Senha de Acesso</label>
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
                placeholder="Sua senha secreta"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
              />
            </div>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%', marginTop: '1rem', padding: '0.85rem' }}
          >
            Acessar Sistema
          </button>
        </form>

        <div className="auth-footer">
          Não tem uma conta? <Link to="/register" className="auth-link">Cadastre-se</Link>
        </div>
      </div>
    </div>
  );
}

export default Login;
