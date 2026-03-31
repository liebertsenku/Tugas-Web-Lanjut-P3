from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from pydantic import BaseModel, ConfigDict
from typing import List
from datetime import datetime, timedelta, timezone
import jwt
from passlib.context import CryptContext

# ==========================================
# 1. KONFIGURASI DATABASE & SECURITY
# ==========================================
DATABASE_URL = "sqlite:///./data_tugas.db"
SECRET_KEY = "kunci_rahasia_tugas_farel" # Kunci rahasia untuk JWT
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Konfigurasi Hashing Password & OAuth2
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ==========================================
# 2. MODEL DATABASE (SQLAlchemy)
# ==========================================
class UserEntity(Base):
    __tablename__ = "users_table"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="user") # 'admin' atau 'user'

class ItemEntity(Base):
    __tablename__ = "items_table"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), index=True, nullable=False)
    description = Column(Text, nullable=True)

Base.metadata.create_all(bind=engine)

# ==========================================
# 3. SCHEMA VALIDASI (Pydantic)
# ==========================================
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"

class UserResponse(BaseModel):
    username: str
    role: str
    model_config = ConfigDict(from_attributes=True)

class ItemRequest(BaseModel):
    name: str
    description: str | None = None

class ItemResponse(ItemRequest):
    id: int
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# 4. FUNGSI UTILITAS (Auth & JWT)
# ==========================================
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# ==========================================
# 5. DEPENDENCIES (Database & RBAC)
# ==========================================
def get_database_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_database_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tidak valid atau kadaluarsa",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = db.query(UserEntity).filter(UserEntity.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def require_admin(current_user: UserEntity = Depends(get_current_user)):
    """RBAC: Memastikan user yang login memiliki role 'admin'"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user

# ==========================================
# 6. INISIALISASI APLIKASI
# ==========================================
app = FastAPI(title="Tugas Microservice dengan RBAC")

# ==========================================
# 7. ENDPOINTS
# ==========================================

# --- Auth Endpoints ---
@app.post("/register", response_model=UserResponse, tags=["Auth"])
def register(user: UserCreate, db: Session = Depends(get_database_session)):
    """Mendaftarkan user baru"""
    db_user = db.query(UserEntity).filter(UserEntity.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username sudah terdaftar")
    
    hashed_pw = get_password_hash(user.password)
    new_user = UserEntity(username=user.username, hashed_password=hashed_pw, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login", tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_database_session)):
    """Login untuk mendapatkan akses token JWT"""
    user = db.query(UserEntity).filter(UserEntity.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Username atau password salah")
    
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Item Endpoints (CRUD Terproteksi) ---
@app.get("/items/", response_model=List[ItemResponse], tags=["Items"])
def get_all_items(db: Session = Depends(get_database_session), current_user: UserEntity = Depends(get_current_user)):
    """Semua user yang login (User/Admin) bisa melihat daftar item"""
    return db.query(ItemEntity).all()

@app.post("/items/", response_model=ItemResponse, tags=["Items"])
def create_item(item: ItemRequest, db: Session = Depends(get_database_session), admin_user: UserEntity = Depends(require_admin)):
    """HANYA ADMIN yang boleh menambah item baru"""
    new_item = ItemEntity(name=item.name, description=item.description)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.delete("/items/{item_id}", tags=["Items"])
def delete_item(item_id: int, db: Session = Depends(get_database_session), admin_user: UserEntity = Depends(require_admin)):
    """HANYA ADMIN yang boleh menghapus item"""
    item = db.query(ItemEntity).filter(ItemEntity.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Data item tidak ditemukan")
    
    db.delete(item)
    db.commit()
    return {"detail": f"Item dengan ID {item_id} berhasil dihapus"}