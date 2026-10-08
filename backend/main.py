from fastapi import FastAPI, HTTPException, UploadFile, File, Form
import google.generativeai as genai
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import PyPDF2
import io

# Carrega variaveis do .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Modelo padrao
MODEL_NAME = "gemini-3.8-flash"

app = FastAPI(
    title="API do EstudaAI", 
    description="API para gerar roteiros de estudos para universitarios a partir da ementa (Texto ou PDF)"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# A rota agora aceita Form Data em vez de JSON para suportar upload de arquivos
@app.post("/gerar-roteiro")
async def gerar_roteiro(
    disciplina: str = Form(..., description="Nome da disciplina"),
    horas_semanais: int = Form(..., description="Horas disponiveis por semana"),
    ementa: str = Form("", description="Texto da ementa (opcional se enviar PDF)"),
    arquivo: UploadFile = File(None, description="Arquivo PDF da ementa")
):
    texto_final_ementa = ementa

    # Se um arquivo foi enviado, tenta ler e extrair o texto do PDF
    if arquivo:
        if not arquivo.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Apenas arquivos no formato PDF sao aceitos.")
        
        try:
            conteudo = await arquivo.read()
            leitor_pdf = PyPDF2.PdfReader(io.BytesIO(conteudo))
            texto_extraido = ""
            for pagina in leitor_pdf.pages:
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_extraido += texto_pagina + "\n"
            
            texto_final_ementa = texto_extraido
        except Exception as e:
            raise HTTPException(status_code=400, detail="Nao foi possivel processar o PDF. Verifique se o arquivo esta corrompido.")

    # Regra de negocio: valida se tem texto suficiente (seja colado ou do PDF)
    if len(texto_final_ementa.split()) < 5:
         raise HTTPException(status_code=400, detail="A ementa fornecida (ou extraida do PDF) e muito curta. Forneca mais detalhes.")

    # Engenharia de Prompt para o Gemini
    prompt = (
        f"Atue como um tutor universitario especialista em planejamento de estudos. "
        f"Crie um roteiro de estudos organizado por semanas para a disciplina de '{disciplina}'. "
        f"A ementa da disciplina e a seguinte: {texto_final_ementa}. "
        f"O aluno tem {horas_semanais} horas disponiveis por semana para estudar essa materia. "
        f"O roteiro deve incluir os topicos a serem estudados e sugestoes de metodos de estudo adequados ao tempo."
    )

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return {"roteiro": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao integrar com o Gemini: {str(e)}")