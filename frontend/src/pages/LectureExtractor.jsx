import React, { useState } from 'react';
import { BookOpen, FileText, AlertTriangle, Play, CheckCircle } from 'lucide-react';
import api from '../services/api';
import LoadingOverlay from '../components/LoadingOverlay';
import CodeBlock from '../components/CodeBlock';
import Layout from '../components/Layout';

function LectureExtractor() {
  const [transcricao, setTranscricao] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  // Results
  const [titulo, setTitulo] = useState('');
  const [secoes, setSecoes] = useState([]);
  const [activeSectionIdx, setActiveSectionIdx] = useState(0);
  const [activeTab, setActiveTab] = useState('teoria'); // 'teoria' | 'exemplo' | 'codigo'

  const handleExtract = async (e) => {
    e.preventDefault();
    if (!transcricao.trim()) return;

    setLoading(true);
    setError('');
    setTitulo('');
    setSecoes([]);

    try {
      const response = await api.post('/skills/lecture_extractor', { transcricao });
      setTitulo(response.data.titulo);
      setSecoes(response.data.secoes || []);
      setActiveSectionIdx(0);
      setActiveTab('teoria');
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || 
        'Erro ao extrair conteúdo pedagógico. Verifique se o texto de transcrição é válido.'
      );
    } finally {
      setLoading(false);
    }
  };

  const currentSection = secoes[activeSectionIdx];

  return (
    <Layout>
      <LoadingOverlay show={loading} text="IA processando e mapeando transcrição no padrão T-E-C..." />

      <header style={{ marginBottom: '2rem' }}>
        <h1>Extrator de Aulas (TEC)</h1>
        <p className="page-description">Transforma transcrições brutas de aulas em fundamentação teórica, analogias práticas e códigos comentados</p>
      </header>

      {error && (
        <div style={{ background: 'rgba(255, 76, 76, 0.12)', border: '1px solid rgba(255, 76, 76, 0.3)', color: '#ff4c4c', padding: '1rem', borderRadius: '12px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <AlertTriangle size={20} />
          <span>{error}</span>
        </div>
      )}

      {/* Input area */}
      {secoes.length === 0 ? (
        <div className="glass-card">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText size={22} color="var(--primary)" />
            Colar Transcrição da Aula
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            Cole a transcrição de voz gravada ou notas rápidas contendo alguma aula técnica de programação. O extrator AI cuidará de estruturar tudo de forma pedagógica.
          </p>

          <form onSubmit={handleExtract}>
            <div className="form-group">
              <label className="form-label" htmlFor="transcricao">Transcrição Bruta</label>
              <textarea
                id="transcricao"
                required
                className="form-input form-textarea"
                placeholder="Cole o texto aqui... Ex: 'Hoje pessoal vamos falar sobre decorators em Python. Decorators são basicamente funções que envolvem outras funções para adicionar comportamentos a elas sem mudar o código interno. Por exemplo, se você quer medir o tempo de execução de uma função...'"
                value={transcricao}
                onChange={(e) => setTranscricao(e.target.value)}
                style={{ height: '240px' }}
              />
            </div>

            <button type="submit" className="btn btn-primary" style={{ padding: '0.85rem 2rem' }}>
              Processar e Estruturar Aula
              <Play size={18} />
            </button>
          </form>
        </div>
      ) : (
        /* Outputs view */
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '0.9rem', color: 'var(--primary)', fontWeight: 700, textTransform: 'uppercase' }}>
              Aula Estruturada com Sucesso
            </span>
            <button 
              type="button" 
              className="btn btn-secondary" 
              onClick={() => { setSecoes([]); setTitulo(''); }}
            >
              Processar Nova Aula
            </button>
          </div>

          <div className="glass-card">
            <h2 style={{ fontSize: '1.75rem', color: 'var(--text-bright)', marginBottom: '2rem', textAlign: 'center' }}>
              {titulo || 'Tema Técnico da Aula'}
            </h2>

            {/* Sidebar pagination style for sections */}
            <div style={{ display: 'flex', gap: '2rem', alignItems: 'start' }}>
              
              {/* Section selector sidebar */}
              <div style={{ width: '220px', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '0.5rem', display: 'block' }}>
                  SEÇÕES DETECTADAS
                </span>
                {secoes.map((sec, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className={`btn ${activeSectionIdx === idx ? 'btn-primary' : 'btn-secondary'}`}
                    style={{ justifyContent: 'flex-start', fontSize: '0.85rem', padding: '0.65rem 1rem' }}
                    onClick={() => {
                      setActiveSectionIdx(idx);
                      setActiveTab('teoria');
                    }}
                  >
                    Seção {idx + 1}
                  </button>
                ))}
              </div>

              {/* Section content display */}
              <div style={{ flex: 1, background: 'rgba(0, 0, 0, 0.15)', padding: '2rem', borderRadius: '12px', border: '1px solid var(--border)' }}>
                {currentSection && (
                  <div>
                    {/* Tab Navigation (TEC) */}
                    <div className="tabs-header">
                      <button
                        type="button"
                        className={`tab-btn ${activeTab === 'teoria' ? 'active' : ''}`}
                        onClick={() => setActiveTab('teoria')}
                      >
                        Teoria (Theory)
                      </button>
                      <button
                        type="button"
                        className={`tab-btn ${activeTab === 'exemplo' ? 'active' : ''}`}
                        onClick={() => setActiveTab('exemplo')}
                      >
                        Exemplo (Example)
                      </button>
                      <button
                        type="button"
                        className={`tab-btn ${activeTab === 'codigo' ? 'active' : ''}`}
                        onClick={() => setActiveTab('codigo')}
                      >
                        Código (Code)
                      </button>
                    </div>

                    {/* Tab Contents */}
                    <div style={{ minHeight: '200px' }}>
                      {activeTab === 'teoria' && (
                        <div style={{ lineHeight: '1.7', color: 'var(--text)' }}>
                          <p style={{ whiteSpace: 'pre-wrap' }}>{currentSection.teoria}</p>
                        </div>
                      )}

                      {activeTab === 'exemplo' && (
                        <div style={{ lineHeight: '1.7', color: 'var(--text)' }}>
                          <p style={{ whiteSpace: 'pre-wrap' }}>{currentSection.exemplo}</p>
                        </div>
                      )}

                      {activeTab === 'codigo' && (
                        <div>
                          <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                            Código-fonte limpo estruturado pelo Agente:
                          </p>
                          <CodeBlock code={currentSection.codigo} language="python" />
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>

            </div>
          </div>
        </div>
      )}
    </Layout>
  );
}

export default LectureExtractor;
