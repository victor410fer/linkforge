from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import models
from database import engine, get_db
from routes import auth, links, billing

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="LinkForge API", version="1.0.0")

# CORS: allow your Vercel domain (update after deployment)
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "https://your-project.vercel.app",   # replace with actual Vercel URL
    "null"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(links.router)
app.include_router(billing.router)

@app.get("/")
def root():
    return {"name": "LinkForge API", "status": "running"}

# Catch-all redirection (works only for API domain; frontend handles its own)
@app.get("/{slug}")
def redirect_to_url(slug: str, db: Session = Depends(get_db)):
    link = db.query(models.Link).filter(models.Link.slug == slug).first()
    if link:
        link.clicks += 1
        db.commit()
        return RedirectResponse(url=link.original_url)
    return {"error": "Link not found"}
