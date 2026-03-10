from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, ConfigDict
from typing import List

# ==========================================
# 1. KONFIGURASI DATABASE
# ==========================================
DATABASE_URL = "sqlite:///./data_tugas.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ==========================================
# 2. MODEL DATABASE (SQLAlchemy)
# ==========================================
class ItemEntity(Base):
    __tablename__ = "items_table"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, nullable=False)
    description = Column(Text, nullable=True)

# Buat tabel di SQLite
Base.metadata.create_all(bind=engine)

# ==========================================
# 3. SCHEMA VALIDASI (Pydantic)
# ==========================================
class ItemRequest(BaseModel):
    name: str
    description: str | None = None

class ItemResponse(ItemRequest):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# 4. INISIALISASI APLIKASI FASTAPI
# ==========================================
app = FastAPI(title="Tugas FastAPI Farel", version="1.0.0")

# Dependency untuk sesi DB
def get_database_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 5. ENDPOINTS
# ==========================================

@app.post("/items/", response_model=ItemResponse, tags=["Items"])
def create_item(item: ItemRequest, db: Session = Depends(get_database_session)):
    """Menambahkan item baru ke database"""
    new_item = ItemEntity(name=item.name, description=item.description)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.get("/items/", response_model=List[ItemResponse], tags=["Items"])
def get_all_items(db: Session = Depends(get_database_session)):
    """Mengambil semua daftar item"""
    return db.query(ItemEntity).all()

@app.get("/items/{item_id}", response_model=ItemResponse, tags=["Items"])
def get_item_by_id(item_id: int, db: Session = Depends(get_database_session)):
    """Mengambil detail satu item berdasarkan ID"""
    item = db.query(ItemEntity).filter(ItemEntity.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Data item tidak ditemukan")
    return item