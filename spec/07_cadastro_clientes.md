# Especificação Técnica: Módulo de Cadastro de Clientes e Captura de Documentos

Este documento detalha a arquitetura, modelos de dados e fluxos de tela para o novo módulo de **Cadastro de Clientes** com suporte nativo a captura de imagens de documentos (CPF, RG, Comprovante de Endereço) diretamente de dispositivos móveis.

O módulo respeita a arquitetura híbrida do projeto, mantendo **separação estrita entre Front-end (React) e Back-end (FastAPI)**.

---

## 1. Visão Geral da Funcionalidade

O sistema permitirá que usuários (vendedores, atendentes ou o próprio cliente) realizem um cadastro completo e enviem fotos de documentos comprobatórios. 

### Dados do Cliente a serem coletados:
*   Nome Completo
*   CPF e RG
*   Data de Nascimento
*   Nome da Mãe
*   Endereço Completo (Rua, Bairro, Cidade, UF, CEP)
*   **Plano Escolhido** (Plano que o cliente deseja adquirir)

### Captura de Documentos:
*   **Integração Mobile:** Utilização de recursos nativos do HTML5 (`capture="environment"`) para acionar a câmera do celular diretamente pelo navegador.
*   **Documentos Esperados:** Foto do CPF, Foto do RG (Frente e Verso) e Comprovante de Endereço.
*   **Segurança:** Upload via `multipart/form-data` utilizando tokens JWT para garantir que apenas usuários autorizados enviem arquivos.

---

## 2. Camada de Back-end (FastAPI)

O backend será responsável por receber, validar, salvar os dados estruturados no banco de dados relacional e armazenar de forma segura os arquivos de imagem.

### A. Modelos de Banco de Dados (`models/cliente.py`)

A tabela `clientes` armazenará os dados cadastrais estruturados.

```python
from datetime import date
from sqlalchemy import Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Cliente(Base):
    __tablename__ = "clientes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    cpf: Mapped[str] = mapped_column(String(14), unique=True, index=True, nullable=False)
    rg: Mapped[str] = mapped_column(String(20), nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    nome_mae: Mapped[str] = mapped_column(String(150), nullable=False)
    
    # Endereço
    endereco: Mapped[str] = mapped_column(String(255), nullable=False)
    bairro: Mapped[str] = mapped_column(String(100), nullable=False)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    cep: Mapped[str] = mapped_column(String(10), nullable=False)
    
    # Plano
    plano_escolhido: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Rastreabilidade
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"))
    
    # Relacionamento com documentos
    documentos: Mapped[list["DocumentoCliente"]] = relationship("DocumentoCliente", back_populates="cliente")

class DocumentoCliente(Base):
    __tablename__ = "documentos_cliente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey("clientes.id"), nullable=False)
    tipo_documento: Mapped[str] = mapped_column(String(50), nullable=False) # Ex: "RG_FRENTE", "CPF", "COMPROVANTE_ENDERECO"
    caminho_arquivo: Mapped[str] = mapped_column(String(500), nullable=False) # Path local ou URL do S3
    
    cliente: Mapped["Cliente"] = relationship("Cliente", back_populates="documentos")
```

### B. Schemas Pydantic (`schemas/cliente.py`)

Schemas para validação de entrada de dados do formulário de cliente (exceto os arquivos, que vêm por formulário multipart).

### C. Rotas da API (`routers/clientes.py`)

1.  **`POST /clientes/`**: Cria o registro estruturado do cliente. Retorna o `id` do cliente gerado.
2.  **`POST /clientes/{id_cliente}/documentos/`**: 
    *   Recebe múltiplos arquivos (`UploadFile` do FastAPI).
    *   Valida a extensão do arquivo (apenas `.jpg`, `.jpeg`, `.png`, `.pdf`).
    *   Salva o arquivo fisicamente no servidor (ex: pasta `/uploads/documentos_seguros/`) ou em um bucket na nuvem.
    *   Gera registros na tabela `documentos_cliente` apontando para o caminho do arquivo salvo.
3.  **`GET /clientes/{id_cliente}`**: Retorna os dados do cliente e a lista de documentos (links seguros para visualização).

---

## 3. Camada de Front-end (React SPA)

O front-end terá uma tela dedicada para o fluxo de cadastro e envio de documentos.

### A. Estrutura da Tela (`pages/CadastroCliente.jsx`)

A tela será dividida em etapas (Wizard) ou formulário longo segmentado:

1.  **Sessão de Dados Pessoais:** Inputs para Nome, CPF, RG, Nascimento, Mãe.
2.  **Sessão de Endereço:** Campos de CEP (com busca automática opcional via ViaCEP), Rua, Bairro, Cidade, UF.
3.  **Sessão do Plano:** Select/Dropdown para escolha do plano desejado.
4.  **Sessão de Upload de Documentos:**
    *   Botões de ação estilizados (Glassmorphism) para capturar imagens.

### B. Captura de Câmera (Mobile)

Para garantir que o usuário consiga tirar fotos diretamente do celular, o React utilizará inputs de arquivo configurados especificamente para mobile:

```jsx
// Botão para capturar RG/CPF usando a câmera traseira do celular
<div className="file-upload-wrapper">
  <label htmlFor="camera-upload-rg" className="btn btn-secondary">
    Tirar Foto do RG
  </label>
  <input 
    type="file" 
    id="camera-upload-rg" 
    accept="image/*" 
    capture="environment" // Aciona a câmera nativa em dispositivos móveis
    onChange={(e) => handleFileSelect(e, 'RG')}
    style={{ display: 'none' }}
  />
</div>
```

### C. Envio Seguro (Axios)

Para enviar texto e arquivos com segurança, os dados serão enviados utilizando a instância de rede já configurada no projeto (que injeta o JWT automaticamente):

```javascript
// Exemplo de envio dos documentos (após o cliente ser criado)
const uploadDocumentos = async (clienteId, arquivosSelecionados) => {
  const formData = new FormData();
  
  // Adiciona as fotos ao payload
  arquivosSelecionados.forEach((doc) => {
    formData.append("files", doc.arquivo);
    formData.append("tipos", doc.tipo); // Para identificar se é RG, CPF, etc.
  });

  await api.post(`/clientes/${clienteId}/documentos/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
      // O Token JWT Bearer já é injetado pelo interceptor do Axios
    }
  });
};
```

---

## 4. Segurança de Armazenamento

*   **Arquivos Privados:** Os documentos (RG, CPF) **NÃO** devem ser salvos na pasta pública do front-end (`public/` do React). Eles devem ser armazenados pelo back-end em um diretório restrito ou Bucket privado.
*   **Acesso Restrito:** A rota para visualizar uma imagem (`GET /documentos/{id}/visualizar`) deve exigir o token JWT no cabeçalho. O FastAPI enviará a imagem via `FileResponse` apenas se o usuário for um administrador ou o vendedor responsável.
