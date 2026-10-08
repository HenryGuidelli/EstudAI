# EstudaAI

O EstudaAI é uma aplicação web completa que gera roteiros de estudos personalizados para universitários. A partir da ementa de uma disciplina (inserida via texto ou arquivo PDF) e da disponibilidade de horas semanais, o sistema utiliza a Inteligência Artificial (Google Gemini) para montar um cronograma detalhado estruturado pedagogicamente e exportá-lo diretamente em formato PDF.

## Tecnologias Utilizadas

* **Backend:** Python, FastAPI, Uvicorn, PyPDF2, Markdown, xhtml2pdf, Google Generative AI (gemini-3.8-flash).
* **Frontend:** React Native Web (Expo Router), TypeScript.

## Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:
* Python (versão 3.9 ou superior)
* Node.js
* Uma chave válida da API do Google Gemini (Google AI Studio)

## Como iniciar o projeto localmente

### 1. Clonar o repositório

```bash
git clone [https://github.com/seu-usuario/estudaai.git](https://github.com/seu-usuario/estudaai.git)
cd estudaai
```

### 2. Configurar e rodar o Backend (API)

Abra um terminal na raiz do projeto e acesse a pasta do backend:

```bash
cd backend
```

Crie e ative um ambiente virtual:

**No Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**No Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

Instale as dependências do projeto:
```bash
pip install fastapi uvicorn google-generativeai python-dotenv pydantic python-multipart PyPDF2 markdown xhtml2pdf
```

Crie um arquivo chamado `.env` na raiz da pasta `backend` e adicione sua chave de API do Gemini:
```env
GOOGLE_API_KEY=sua_chave_de_api_aqui
```

Inicie o servidor do backend:
```bash
uvicorn main:app --reload
```
A API estará rodando em `http://127.0.0.1:8000`. Mantenha este terminal aberto.

### 3. Configurar e rodar o Frontend (Interface Web)

Abra um NOVO terminal na raiz do projeto clonado e acesse a pasta do frontend:

```bash
cd frontend
```

Instale as dependências necessárias do Node:
```bash
npm install
```

Inicie a aplicação web (a flag `-c` limpa o cache para evitar problemas com dependências antigas e a flag `-w` força a execução no navegador):
```bash
npx expo start -c -w
```

O projeto será aberto automaticamente no seu navegador padrão (geralmente no endereço `http://localhost:8081`).

## Como usar

1. Com a interface aberta no navegador, alterne entre o Modo Claro ou Escuro conforme sua preferência.
2. Preencha o nome da disciplina e a sua disponibilidade de horas semanais.
3. Forneça a ementa da disciplina escolhendo uma das opções:
   * **Opção 1:** Cole os tópicos manualmente no campo de texto.
   * **Opção 2:** Clique no botão pontilhado para enviar o arquivo PDF da ementa.
4. Clique em "Montar meu roteiro".
5. Aguarde o processamento. Ao finalizar, utilize os botões gerados para **Visualizar** (abre em nova guia) ou **Baixar** o seu Plano de Estudos em formato PDF.