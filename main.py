from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker, Session, DeclarativeBase
from pydantic import BaseModel

# --- DATABASE SETUP ---
DATABASE_URL = "sqlite:///./books.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modern SQLAlchemy 2.0 Way to define the Base
class Base(DeclarativeBase):
    pass

# --- DATABASE MODEL ---
class BookDB(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    author = Column(String)
    description = Column(String)

# Create the database tables
Base.metadata.create_all(bind=engine)

# --- PYDANTIC SCHEMAS ---
class BookCreate(BaseModel):
    title: str
    author: str
    description: str

class BookResponse(BookCreate):
    id: int
    class Config:
        from_attributes = True

# --- API APP ---
app = FastAPI(title="Book Management API - Phase 2")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- REQUIRED ENDPOINTS PER TASK DOCUMENTS ---

@app.post("/books", response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """POST /books: Add a new book [cite: 5928, 5929, 5930]"""
    new_book = BookDB(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.get("/books", response_model=list[BookResponse])
def get_all_books(db: Session = Depends(get_db)):
    """GET /books: Fetch all books from DB [cite: 5937, 5938, 5939]"""
    return db.query(BookDB).all()

@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """GET /books/:id: Fetch one book by its ID [cite: 5946, 5948, 5949]"""
    book = db.query(BookDB).filter(BookDB.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book