from sqlalchemy import Column,Integer,String,DateTime,ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class File(Base):
    __tablename__ = "Files"

    id = Column(Integer,primary_key=True,index=True)
    filename = Column(String,index=True)
    filepath = Column(String)
    created_at = Column(DateTime,default=datetime.now)
    deleted_at = Column(DateTime)

class Folder(Base):
    __tablename__ = "folder"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    deleted_at = Column(DateTime)
    files = relationship("Folder_file", back_populates="folder", cascade="all, delete-orphan")

class Folder_file(Base):
    __tablename__ = "folder_files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String)
    file_path = Column(String)
    folder_id = Column(Integer, ForeignKey("folder.id",ondelete = "CASCADE")) 
    folder = relationship("Folder", back_populates="files")