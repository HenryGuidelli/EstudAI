from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
import google.generativeai as genai
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io
import uuid
import markdown
from xhtml2pdf import pisa

# Carregar variáveis de ambiente
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Modelo atualizado
MODEL_NAME = "gemini-3.5-flash-lite"

app = FastAPI(title="API do EstudaAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar diretório local para os PDFs
DIRETORIO_PDFS = "pdfs_gerados"
os.makedirs(DIRETORIO_PDFS, exist_ok=True)

@app.post("/gerar-roteiro")
async def gerar_roteiro(
    disciplina: str = Form(...),
    horas_semanais: int = Form(...),
    ementa: str = Form(""),
    arquivo: UploadFile = File(None)
):
    texto_final_ementa = ementa

    if arquivo:
        if not arquivo.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Apenas arquivos PDF são aceitos.")
        try:
            conteudo = await arquivo.read()
            leitor_pdf = PyPDF2.PdfReader(io.BytesIO(conteudo))
            texto_extraido = ""
            for pagina in leitor_pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_extraido += texto_pagina + "\n"
            texto_final_ementa = texto_extraido
        except Exception:
            raise HTTPException(status_code=400, detail="Não foi possível processar o PDF.")

    prompt = (
        f"Você é um tutor universitário especialista em engenharia pedagógica, neurociência do aprendizado e metodologias de estudo.\n"
        f"Seu objetivo é criar um plano de estudos altamente estruturado, prático e otimizado para a disciplina de '{disciplina}'.\n\n"
        f"### INFORMAÇÕES DE CONTEXTO\n"
        f"- Ementa da disciplina: {texto_final_ementa}\n"
        f"- Tempo disponível: {horas_semanais} horas por semana.\n\n"
        f"### DIRETRIZES DE SAÍDA\n"
        f"Crie o roteiro utilizando formatação Markdown (use cabeçalhos, negrito, listas e bullet points). O documento deve conter obrigatoriamente as seguintes seções:\n\n"
        f"1. **Visão Geral e Estratégia:** Uma breve introdução de 1 parágrafo sobre a natureza da disciplina e a melhor abordagem de estudo (ex: foco em matemática, leitura teórica densa, programação prática, etc.).\n"
        f"2. **Divisão do Tempo ({horas_semanais}h semanais):** Sugira como o aluno deve fracionar essas horas na semana (ex: porcentagem para leitura, porcentagem para exercícios, porcentagem para revisão). Recomende métodos de estudo específicos (ex: Pomodoro, Técnica Feynman, Flashcards).\n"
        f"3. **Cronograma Semanal Detalhado:** Divida os tópicos da ementa em um roteiro sequencial de semanas. Para cada semana, especifique:\n"
        f"   - **Tema da Semana:** O tópico central.\n"
        f"   - **Objetivos de Aprendizagem:** O que o aluno deve saber ao final da semana.\n"
        f"   - **Plano de Ação:** Instruções claras de como gastar as {horas_semanais} horas (ex: '2h lendo a teoria X', '2h resolvendo a lista Y').\n"
        f"4. **Dicas de Ouro e Recursos:** Recomendações de tipos de materiais complementares ou hacks específicos para dominar os assuntos mais difíceis dessa ementa."
    )
    
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        # Limite máximo de tokens configurado para respostas longas e completas
        config = genai.types.GenerationConfig(max_output_tokens=10000)
        
        # Chamada assíncrona para não bloquear o servidor
        response = await model.generate_content_async(prompt, generation_config=config)
        texto_roteiro = response.text

        # 1. Converter Markdown do Gemini para HTML
        html_content = markdown.markdown(texto_roteiro)
        
        # 2. Estruturar o HTML com estilo básico para o PDF
        html_estruturado = f"""
        <html>
        <head>
            <style>
                @page {{ margin: 2cm; }}
                body {{ font-family: Helvetica, sans-serif; font-size: 14px; color: #333; line-height: 1.6; }}
                h1, h2, h3 {{ color: #2563EB; margin-bottom: 10px; }}
                li {{ margin-bottom: 6px; }}
                strong {{ color: #1F2937; }}
            </style>
        </head>
        <body>
            <h1>Plano de Estudos: {disciplina}</h1>
            {html_content}
        </body>
        </html>
        """

        # 3. Gerar nome único e salvar o ficheiro localmente
        file_id = uuid.uuid4().hex
        caminho_pdf = os.path.join(DIRETORIO_PDFS, f"roteiro_{file_id}.pdf")
        
        with open(caminho_pdf, "w+b") as pdf_file:
            pisa.CreatePDF(html_estruturado, dest=pdf_file)

        return {
            "roteiro": texto_roteiro,
            "file_id": file_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

# Nova rota para VISUALIZAR no navegador (inline)
@app.get("/view/{file_id}")
def view_pdf(file_id: str):
    caminho_pdf = os.path.join(DIRETORIO_PDFS, f"roteiro_{file_id}.pdf")
    if os.path.exists(caminho_pdf):
        return FileResponse(
            caminho_pdf, 
            media_type="application/pdf", 
            filename="Plano_de_Estudos.pdf",
            content_disposition_type="inline" # Força o navegador a abrir a pré-visualização
        )
    raise HTTPException(status_code=404, detail="Arquivo não encontrado")

# Rota mantida para BAIXAR diretamente (attachment)
@app.get("/download/{file_id}")
def download_pdf(file_id: str):
    caminho_pdf = os.path.join(DIRETORIO_PDFS, f"roteiro_{file_id}.pdf")
    if os.path.exists(caminho_pdf):
        return FileResponse(
            caminho_pdf, 
            media_type="application/pdf", 
            filename="Plano_de_Estudos.pdf",
            content_disposition_type="attachment" # Força o download imediato
        )
    raise HTTPException(status_code=404, detail="Arquivo não encontrado")
