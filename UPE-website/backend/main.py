from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List

from database import engine, get_db, Base
from models import Beverage
from schemas import BeverageCreate, BeverageResponse

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="UPE Rechner API", version="1.0.0")

# CORS - allow all origins for simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "UPE Rechner Backend", "version": "1.0.0"}


@app.get("/beverages/", response_model=List[BeverageResponse])
def get_beverages(db: Session = Depends(get_db)):
    """Get all beverages, sorted by creation date (newest first)"""
    beverages = db.query(Beverage).order_by(Beverage.created_at.desc()).all()
    return beverages


@app.post("/beverages/", response_model=BeverageResponse, status_code=201)
def create_beverage(beverage: BeverageCreate, db: Session = Depends(get_db)):
    """Create a new beverage entry"""
    db_beverage = Beverage(
        name=beverage.name,
        type=beverage.type,
        volume=beverage.volume,
        price=beverage.price,
        store=beverage.store,
        alcohol_content=beverage.alcohol_content,
    )
    db.add(db_beverage)
    db.commit()
    db.refresh(db_beverage)
    return db_beverage
