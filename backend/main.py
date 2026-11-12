from fastapi import FastAPI

app = FastAPI(title="Central de Solicitações")

@app.get("/ola")
def ola():
    return {"mensagem": "API funcionando"}