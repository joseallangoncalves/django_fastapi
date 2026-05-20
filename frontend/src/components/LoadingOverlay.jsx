import React from 'react';

function LoadingOverlay({ show, text = 'Processando com Inteligência Artificial...' }) {
  if (!show) return null;
  return (
    <div className="loading-overlay">
      <div className="spinner"></div>
      <div className="loading-text">{text}</div>
    </div>
  );
}

export default LoadingOverlay;
