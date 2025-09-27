from fastapi import FastAPI
from whatsapp.webhook import router as webhook_router

app = FastAPI(title="Conecta+ Aotencer")

# Registrando rotas
app.include_router(webhook_router)


@app.get("/")
async def root():
    return {"message": "Conecta+ API rodando!"}
