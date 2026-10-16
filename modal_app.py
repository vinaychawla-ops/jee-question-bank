"""Modal deployment for the JEE Question Bank static site.

Deploys the production Vite build (web/dist/) as a static file server.
Run: MODAL_TOKEN_ID=... MODAL_TOKEN_SECRET=... modal deploy modal_app.py
"""
import modal

app = modal.App("jee-question-bank")

image = (
    modal.Image.debian_slim()
    .pip_install("fastapi[standard]")
    .add_local_dir("web/dist", "/dist", copy=True)
)


@app.function(image=image)
@modal.asgi_app()
def web():
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles

    fastapi_app = FastAPI()
    fastapi_app.mount("/", StaticFiles(directory="/dist", html=True), name="static")
    return fastapi_app
