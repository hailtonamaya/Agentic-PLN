from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os
import importlib.util
import sys
import os

BASE_DIR = os.path.dirname(__file__)


def load_rag(project_folder):

    project_path = os.path.join(BASE_DIR, project_folder)

    # agregar proyecto al path
    if project_path not in sys.path:
        sys.path.append(project_path)

    # cambiar directorio de ejecución
    os.chdir(project_path)

    rag_path = os.path.join(project_path, "src/RAG/rag_pipeline.py")

    spec = importlib.util.spec_from_file_location("rag_pipeline", rag_path)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module.ask


ask_pediatria = load_rag("PLN-Proyecto-Pediatria")
ask_cardiologia = load_rag("PLN-Proyecto-Cardiologia")
ask_epidemiologia = load_rag("PLN-Proyecto-Epidemiologia")


# ---------- FASTAPI ----------
app = FastAPI(
    title="Medical Multi-RAG API",
    description="API para consultar múltiples RAG médicos",
    version="1.0"
)


class QueryRequest(BaseModel):
    question: str
    specialty: str


@app.get("/")
def root():
    return {"message": "Medical RAG API funcionando"}


@app.post("/ask")
def ask_rag(query: QueryRequest):
    print(f"Recibida pregunta: {query.question} | Especialidad: {query.specialty}")

    question = query.question
    specialty = query.specialty.lower()

    try:

        if specialty == "pediatria":
            answer = ask_pediatria(question)

        elif specialty == "cardiologia":
            answer = ask_cardiologia(question)

        elif specialty == "epidemiologia":
            answer = ask_epidemiologia(question)

        else:
            return {"error": "Especialidad no válida"}

        return {
            "specialty": specialty,
            "question": question,
            "answer": answer
        }

    except Exception as e:

        return {
            "error": str(e)
        }