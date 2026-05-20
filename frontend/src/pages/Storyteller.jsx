import React, { useState } from 'react';
import { Sparkles, MessageSquare, AlertTriangle, ArrowRight } from 'lucide-react';
import api from '../services/api';
import LoadingOverlay from '../components/LoadingOverlay';
import Layout from '../components/Layout';

function Storyteller() {
  const [tema, setTema] = useState('');
  const [historia, setHistoria] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerate = async (e) => {
    e.preventDefault();
    if (!tema.trim()) return;

    setLoading(true);
    setError('');
    setHistoria('');

    try {
      // Call standard modular endpoint
      const response = await api.post('/skills/storyteller', { tema });
      setHistoria(response.data.historia);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || 
        'Erro ao invocar o modelo Groq Llama 3 para geração de histórias.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <LoadingOverlay show={loading} text="Groq Llama 3.1 gerando história criativa..." />

      <header style={{ marginBottom: '2rem' }}>
        <h1>Storyteller IA</h1>
        <p className="page-description">Habilidade de geração de narrativas criativas baseadas em temas personalizados</p>
      </header>

      {error && (
        <div style={{ background: 'rgba(255, 76, 76, 0.12)', border: '1px solid rgba(255, 76, 76, 0.3)', color: '#ff4c4c', padding: '1rem', borderRadius: '12px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div className="grid-2" style={{ alignItems: 'start', gap: '2rem' }}>
        {/* Left Input Card */}
        <div className="glass-card">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <MessageSquare size={22} color="var(--primary)" />
            Escolha o Tema
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            Escreva o enredo, personagens, ou tema geral sobre o qual você gostaria que a Inteligência Artificial gerasse uma história envolvente.
          </p>

          <form onSubmit={handleGenerate}>
            <div className="form-group">
              <label className="form-label" htmlFor="tema">Tema da História</label>
              <textarea
                id="tema"
                required
                className="form-input form-textarea"
                placeholder="Ex: Uma viagem espacial até Marte onde a tripulação descobre uma civilização subterrânea pacífica que cultiva plantas luminosas..."
                value={tema}
                onChange={(e) => setTema(e.target.value)}
                style={{ height: '140px' }}
              />
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '0.85rem' }}>
              Gerar História
              <ArrowRight size={18} />
            </button>
          </form>
        </div>

        {/* Right Output Card */}
        <div className="glass-card" style={{ minHeight: '350px', display: 'flex', flexDirection: 'column' }}>
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sparkles size={22} color="var(--secondary)" />
            Narrativa Gerada
          </h2>

          {historia ? (
            <div className="story-output" style={{ flex: 1, marginTop: 0, overflowY: 'auto', maxHeight: '450px' }}>
              {historia.split('\n\n').map((paragraph, index) => (
                <p key={index} style={{ marginBottom: '1rem', color: 'var(--text-bright)' }}>{paragraph}</p>
              ))}
            </div>
          ) : (
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', border: '1px dashed var(--border)', borderRadius: '12px', padding: '2rem', textAlign: 'center' }}>
              Digite o tema à esquerda e clique em gerar para ler a história da inteligência artificial.
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

export default Storyteller;
