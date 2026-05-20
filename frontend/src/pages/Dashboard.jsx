import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, FileText, Trash2, Edit3, Eye, Calendar, DollarSign, 
  Sparkles, CheckCircle2, ShieldAlert, Cpu, Layers, HelpCircle 
} from 'lucide-react';
import api from '../services/api';
import LoadingOverlay from '../components/LoadingOverlay';
import Layout from '../components/Layout';

function Dashboard() {
  const [contracts, setContracts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  
  // Selected contract for modal view/edit
  const [selectedContract, setSelectedContract] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editFormData, setEditFormData] = useState({
    numero_contrato: '',
    contratante: '',
    contratado: '',
    valor_total: 0,
    moeda: 'BRL',
    resumo: '',
    observacoes: ''
  });

  const fileInputRef = useRef(null);

  // Fetch contracts on mount
  useEffect(() => {
    fetchContracts();
  }, []);

  const fetchContracts = async () => {
    setLoading(true);
    try {
      const response = await api.get('/contracts/');
      setContracts(response.data);
    } catch (err) {
      console.error(err);
      setError('Erro ao buscar o histórico de execuções.');
    } finally {
      setLoading(false);
    }
  };

  // Drag and drop event handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current.click();
  };

  // Upload file API call
  const uploadFile = async (file) => {
    setActionLoading(true);
    setError('');
    setSuccessMsg('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await api.post('/contracts/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setSuccessMsg(`Documento "${file.name}" classificado e processado com sucesso!`);
      // Auto dismiss success toast
      setTimeout(() => setSuccessMsg(''), 5000);
      
      fetchContracts();
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || 
        'Erro ao processar o arquivo. Certifique-se de que é um formato válido (PDF, DOCX, TXT, MD).'
      );
    } finally {
      setActionLoading(false);
    }
  };

  // Delete contract API call
  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja excluir permanentemente este registro?')) return;
    
    setActionLoading(true);
    try {
      await api.delete(`/contracts/${id}`);
      setSuccessMsg('Registro excluído com sucesso.');
      setTimeout(() => setSuccessMsg(''), 4000);
      fetchContracts();
      if (selectedContract?.id === id) {
        setSelectedContract(null);
      }
    } catch (err) {
      console.error(err);
      setError('Erro ao excluir o registro.');
    } finally {
      setActionLoading(false);
    }
  };

  // Open contract details view
  const handleView = (contract) => {
    setSelectedContract(contract);
    setIsEditing(false);
  };

  // Open contract edit view
  const handleEditClick = (contract) => {
    setSelectedContract(contract);
    setIsEditing(true);
    setEditFormData({
      numero_contrato: contract.numero_contrato || '',
      contratante: contract.contratante || '',
      contratado: contract.contratado || '',
      valor_total: contract.valor_total || 0,
      moeda: contract.moeda || 'BRL',
      resumo: contract.resumo || '',
      observacoes: contract.observacoes || ''
    });
  };

  // Handle Edit Input change
  const handleEditChange = (e) => {
    const { name, value } = e.target;
    setEditFormData(prev => ({
      ...prev,
      [name]: name === 'valor_total' ? parseFloat(value) || 0 : value
    }));
  };

  // Submit contract updates
  const handleUpdateSubmit = async (e) => {
    e.preventDefault();
    setActionLoading(true);
    setError('');

    try {
      const response = await api.put(`/contracts/${selectedContract.id}`, editFormData);
      setSuccessMsg('Registro atualizado com sucesso!');
      setTimeout(() => setSuccessMsg(''), 4000);
      setSelectedContract(response.data);
      setIsEditing(false);
      fetchContracts();
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || 
        'Erro ao salvar as atualizações do documento.'
      );
    } finally {
      setActionLoading(false);
    }
  };

  // Metric Calculation
  const totalExecutions = contracts.length;
  const totalValue = contracts.reduce((acc, cur) => acc + (cur.valor_total || 0), 0);
  const activeSkillsCount = 15; // Mapped skills

  // Skill showcase array
  const showcaseSkills = [
    { title: 'Analisador Contratual', desc: 'Extrai multas, termos, obrigações de minutas contratuais.', type: 'core' },
    { title: 'Extrator Técnico de Aulas', desc: 'Converte transcrições no padrão pedagógico T-E-C (Teoria, Exemplo, Código).', type: 'core' },
    { title: 'Resumo Estratégico', desc: 'Sintetiza documentos complexos salvando insights em arquivos de alta legibilidade.', type: 'core' },
    { title: 'Analisador WhatsApp', desc: 'Processa históricos de chats identificando tarefas, links e datas cruciais.', type: 'core' },
  ];

  return (
    <Layout>
      <LoadingOverlay show={actionLoading} />

      <header style={{ marginBottom: '2rem' }}>
        <h1>Augenet AI Portal</h1>
        <p className="page-description">Painel de controle de inteligência artificial e processamento de arquivos</p>
      </header>

      {/* Alert Notices */}
      {error && (
        <div style={{ background: 'rgba(255, 76, 76, 0.12)', border: '1px solid rgba(255, 76, 76, 0.3)', color: '#ff4c4c', padding: '1rem', borderRadius: '12px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <ShieldAlert size={20} />
          <span>{error}</span>
        </div>
      )}

      {successMsg && (
        <div style={{ background: 'rgba(46, 213, 115, 0.12)', border: '1px solid rgba(46, 213, 115, 0.3)', color: '#2ed573', padding: '1rem', borderRadius: '12px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <CheckCircle2 size={20} />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Metrics Cards Row */}
      <section className="grid-3" style={{ marginBottom: '2.5rem' }}>
        <div className="glass-card metric-card">
          <div className="metric-icon metric-purple">
            <Cpu size={24} />
          </div>
          <div className="metric-info">
            <span className="metric-label">Execuções de IA</span>
            <span className="metric-value">{totalExecutions}</span>
          </div>
        </div>

        <div className="glass-card metric-card">
          <div className="metric-icon metric-cyan">
            <DollarSign size={24} />
          </div>
          <div className="metric-info">
            <span className="metric-label">Volume Processado</span>
            <span className="metric-value">
              {totalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}
            </span>
          </div>
        </div>

        <div className="glass-card metric-card">
          <div className="metric-icon metric-pink">
            <Layers size={24} />
          </div>
          <div className="metric-info">
            <span className="metric-label">Habilidades Ativas</span>
            <span className="metric-value">{activeSkillsCount}</span>
          </div>
        </div>
      </section>

      {/* Primary Actions: Drag and Drop AI Classifier */}
      <section className="grid-2" style={{ marginBottom: '3rem', alignItems: 'start' }}>
        <div className="glass-card">
          <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Upload size={22} color="var(--primary)" />
            Classificador de Documentos IA
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            Envie qualquer arquivo nos formatos PDF, DOCX, TXT ou MD. A IA do Augenet vai classificar o documento, aplicar a habilidade recomendada e extrair os dados estruturados de forma autônoma.
          </p>
          
          <div 
            className={`upload-container ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            onClick={triggerFileSelect}
          >
            <Upload className="upload-icon" />
            <div>
              <p style={{ fontWeight: 600, color: 'var(--text-bright)', marginBottom: '0.25rem' }}>
                Arraste o arquivo aqui ou clique para selecionar
              </p>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                PDF, DOCX, TXT ou MD (Max 10MB)
              </p>
            </div>
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              accept=".pdf,.docx,.doc,.txt,.md"
              onChange={handleFileChange}
            />
          </div>
        </div>

        {/* AI Skills Showcase */}
        <div className="glass-card">
          <h2>Habilidades de IA Em Destaque</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
            Conheça as capacidades pré-mapeadas e configuradas que o Agente Smart Router utiliza para extração:
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            {showcaseSkills.map((sk, idx) => (
              <div key={idx} style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border)', borderRadius: '10px' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--secondary)' }}>{sk.title}</span>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{sk.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* History table list */}
      <section className="glass-card" style={{ marginBottom: '3rem' }}>
        <h2>Histórico de Documentos Analisados</h2>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
            Buscando dados no banco relacional...
          </div>
        ) : contracts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            Nenhum documento processado por este usuário ainda. Faça o upload acima!
          </div>
        ) : (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Nº Documento</th>
                  <th>Origem/Contratante</th>
                  <th>Destino/Contratado</th>
                  <th>Valor</th>
                  <th>Roteador IA</th>
                  <th>Ações</th>
                </tr>
              </thead>
              <tbody>
                {contracts.map((contract) => (
                  <tr key={contract.id}>
                    <td style={{ fontWeight: 600, color: 'var(--text-bright)' }}>{contract.numero_contrato}</td>
                    <td>{contract.contratante}</td>
                    <td>{contract.contratado}</td>
                    <td>
                      {contract.valor_total > 0 
                        ? `${contract.valor_total.toLocaleString('pt-BR', { style: 'currency', currency: contract.moeda || 'BRL' })}`
                        : 'N/A'
                      }
                    </td>
                    <td>
                      <span className="badge badge-success" style={{ fontSize: '0.7rem' }}>
                        {contract.observacoes?.includes('smart_router_') 
                          ? contract.observacoes.split('smart_router_')[1].split(']')[0]
                          : contract.observacoes?.includes('smart_router_') 
                            ? 'classificador'
                            : 'AI Extractor'
                        }
                      </span>
                    </td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button 
                          type="button" 
                          className="btn btn-secondary" 
                          style={{ padding: '0.4rem', borderRadius: '6px' }}
                          title="Visualizar Detalhes"
                          onClick={() => handleView(contract)}
                        >
                          <Eye size={16} />
                        </button>
                        <button 
                          type="button" 
                          className="btn btn-secondary" 
                          style={{ padding: '0.4rem', borderRadius: '6px' }}
                          title="Editar"
                          onClick={() => handleEditClick(contract)}
                        >
                          <Edit3 size={16} />
                        </button>
                        <button 
                          type="button" 
                          className="btn btn-secondary" 
                          style={{ padding: '0.4rem', borderRadius: '6px', color: '#ff4c4c' }}
                          title="Excluir"
                          onClick={() => handleDelete(contract.id)}
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      {/* Sliding detail/edit panel modal */}
      {selectedContract && (
        <div 
          style={{ 
            position: 'fixed', 
            top: 0, 
            right: 0, 
            bottom: 0, 
            width: '100%', 
            maxWidth: '560px', 
            background: 'var(--bg-surface)', 
            borderLeft: '1px solid var(--border)',
            boxShadow: 'var(--shadow-lg)', 
            zIndex: 999, 
            padding: '2.5rem',
            overflowY: 'auto',
            animation: 'slideIn 0.3s cubic-bezier(0.16, 1, 0.3, 1)'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
            <h2 style={{ margin: 0 }}>
              {isEditing ? 'Editar Registro' : 'Detalhes do Registro'}
            </h2>
            <button 
              type="button" 
              className="btn btn-secondary" 
              style={{ padding: '0.4rem 0.8rem', fontSize: '0.8rem' }}
              onClick={() => setSelectedContract(null)}
            >
              Fechar
            </button>
          </div>

          {isEditing ? (
            /* EDIT FORM */
            <form onSubmit={handleUpdateSubmit}>
              <div className="form-group">
                <label className="form-label">Número do Contrato / Documento</label>
                <input 
                  type="text" 
                  name="numero_contrato"
                  className="form-input" 
                  value={editFormData.numero_contrato}
                  onChange={handleEditChange}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label">Contratante / Nome da Habilidade</label>
                <input 
                  type="text" 
                  name="contratante"
                  className="form-input" 
                  value={editFormData.contratante}
                  onChange={handleEditChange}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Contratado / Origem de Execução</label>
                <input 
                  type="text" 
                  name="contratado"
                  className="form-input" 
                  value={editFormData.contratado}
                  onChange={handleEditChange}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1rem' }} className="form-group">
                <div>
                  <label className="form-label">Valor Total</label>
                  <input 
                    type="number" 
                    name="valor_total"
                    step="0.01"
                    className="form-input" 
                    value={editFormData.valor_total}
                    onChange={handleEditChange}
                  />
                </div>
                <div>
                  <label className="form-label">Moeda</label>
                  <input 
                    type="text" 
                    name="moeda"
                    className="form-input" 
                    value={editFormData.moeda}
                    onChange={handleEditChange}
                  />
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Resumo do Conteúdo (IA)</label>
                <textarea 
                  name="resumo"
                  className="form-input form-textarea" 
                  value={editFormData.resumo}
                  onChange={handleEditChange}
                  style={{ height: '180px' }}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Metadados e Observações de Auditoria</label>
                <input 
                  type="text" 
                  name="observacoes"
                  className="form-input" 
                  value={editFormData.observacoes}
                  onChange={handleEditChange}
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem' }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>
                  Salvar Alterações
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setIsEditing(false)}
                >
                  Cancelar
                </button>
              </div>
            </form>
          ) : (
            /* DETAILS VIEW */
            <div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '1rem', borderRadius: '8px' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
                    Nº DOCUMENTO
                  </span>
                  <span style={{ fontWeight: 600, color: 'var(--text-bright)' }}>
                    {selectedContract.numero_contrato}
                  </span>
                </div>

                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '1rem', borderRadius: '8px' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
                    VALOR TOTAL
                  </span>
                  <span style={{ fontWeight: 600, color: 'var(--text-bright)' }}>
                    {selectedContract.valor_total > 0 
                      ? selectedContract.valor_total.toLocaleString('pt-BR', { style: 'currency', currency: selectedContract.moeda || 'BRL' })
                      : 'N/A'
                    }
                  </span>
                </div>

                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '1rem', borderRadius: '8px' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
                    ORIGEM / CONTRATANTE
                  </span>
                  <span>{selectedContract.contratante}</span>
                </div>

                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '1rem', borderRadius: '8px' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
                    DESTINO / CONTRATADO
                  </span>
                  <span>{selectedContract.contratado}</span>
                </div>

                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '1rem', borderRadius: '8px', gridColumn: 'span 2' }}>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
                    AUDITORIA E CLASSIFICAÇÃO IA
                  </span>
                  <span style={{ fontSize: '0.85rem', color: 'var(--secondary)' }}>
                    {selectedContract.observacoes}
                  </span>
                </div>
              </div>

              <div style={{ marginBottom: '2rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.5rem' }}>
                  CONTEÚDO EXTRAÍDO / RESUMO IA
                </span>
                <div 
                  style={{ 
                    background: '#090a15', 
                    padding: '1.25rem', 
                    borderRadius: '10px', 
                    fontSize: '0.9rem', 
                    lineHeight: '1.6', 
                    whiteSpace: 'pre-wrap', 
                    maxHeight: '300px', 
                    overflowY: 'auto',
                    border: '1px solid var(--border)'
                  }}
                >
                  {selectedContract.resumo}
                </div>
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <button 
                  type="button" 
                  className="btn btn-primary" 
                  style={{ flex: 1 }}
                  onClick={() => handleEditClick(selectedContract)}
                >
                  Editar Dados
                </button>
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  style={{ color: '#ff4c4c' }}
                  onClick={() => handleDelete(selectedContract.id)}
                >
                  Excluir Registro
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </Layout>
  );
}

export default Dashboard;
