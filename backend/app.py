from fastapi import FastAPI,Depends,HTTPException,UploadFile,File,Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Annotated
from database import connect_db,engine,SessionLocal
from sqlalchemy import text
import model
import os,shutil,random,time,threading,zipfile,tempfile
from datetime import datetime,timedelta
from fastapi.responses import FileResponse

app = FastAPI()

model.Base.metadata.create_all(bind=engine)
db_dependency = Annotated[Session,Depends(connect_db)]

Upload_dir = "uploads"
os.makedirs(Upload_dir,exist_ok = True)

origins = ["http://127.0.0.1:5500","http://localhost:5500"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/')
def home():
    return {'status':'success','message':'Welcome to file sharing app'}

@app.get('/check_db')
def check_db(db:db_dependency):
    try:
        db.execute(text("select 1"))
        return {'status':'success','message':'Database is Connected'}
    except Exception as e:
        raise HTTPException(status_code = 500,detail={'status':'error','message':'Database Connection Failed:{str(e)}'})




@app.post('/Upload_file')
def upload_file(db:db_dependency,files:UploadFile = File(...)):
    file_path = os.path.join(Upload_dir,files.filename)
    def create_id(db):
        while True:
            new_id = random.randint(100000,999999)

            exist_id = db.query(model.File).filter(model.File.id == new_id).first()

            if not exist_id:
                return new_id
            
    file_id = create_id(db)

    with open(file_path,"wb") as f:
        shutil.copyfileobj(files.file,f)

    db_file = model.File(id = file_id,filename = files.filename,filepath = file_path,created_at = datetime.now(),deleted_at = datetime.now()+timedelta(hours=24))
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {'status':'success','message':'File Uploaded Successfully and deleted after 24 hours','file_id':file_id}


def delete_file():
    while True:
        db = SessionLocal()
        try:
            expired = db.query(model.File).filter(model.File.deleted_at <= datetime.now()).all()

            for f in expired:
                file_path = os.path.join(Upload_dir, f.filename)
                if os.path.exists(file_path):
                    os.remove(file_path)
                db.delete(f)
            db.commit()
        except Exception as e:
            db.rollback()
            print("Error:", e)
        finally:
            db.close()
        time.sleep(300)#after 5 minute is will stop 

@app.on_event('startup')
def start_cleanup():
    threading.Thread(target = delete_file,daemon=True).start()
    threading.Thread(target = delete_folder,daemon=True).start()


@app.get('/get_file/{id}')
def get_file(db:db_dependency,id:int):
    file = db.query(model.File).filter(model.File.id == id).first()

    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    if not os.path.isfile(file.filepath):
        return {'status': 'error', 'message': 'file path is invalid'}
    return FileResponse(path=file.filepath,filename=file.filename,media_type='application/octet-stream')


@app.post('/Upload_folder')
def Upload_folder(db:db_dependency,files:list[UploadFile]=File(...),paths:list[str]=Form(...)):
    def folder_id():
        while True:
            new_id = random.randint(100000,999999)
            exist_id = db.query(model.Folder).filter(model.Folder.id == new_id).first()

            if not exist_id:
                return new_id
            
    folder_id = folder_id()
    saved_files = []

    if (len(files) != len(paths)):
        raise HTTPException(status_code=400,detail='files and paths are mismatched')
    
    root_folder = paths[0].split('/')[0]
    db_folder = model.Folder(id=folder_id,name=root_folder,deleted_at=datetime.utcnow()+timedelta(hours=5))
    db.add(db_folder)
    db.commit()
    db.refresh(db_folder)

    for file,path in zip(files,paths):
        safe_path = os.path.normpath(path).lstrip(os.sep)
        full_path = os.path.join(Upload_dir,safe_path)

        os.makedirs(os.path.dirname(full_path),exist_ok=True)
        with open(full_path,'wb')as f:
            shutil.copyfileobj(file.file,f)
        
        db_files = model.Folder_file(file_name=os.path.basename(path),file_path=full_path,folder_id=db_folder.id)
        db.add(db_files)    
        saved_files.append(path)

    db.commit()
    return {'status':'success','message':'Folder Uploaded SuccessFully and deleted after 5 hours','folder_id':folder_id}


@app.get('/get_folder/{id}')
def get_folder(db:db_dependency,id:int):
    folder = db.query(model.Folder).filter(model.Folder.id == id).first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder ID not found")
    file = db.query(model.Folder_file).filter(model.Folder_file.folder_id == id).all()

    
    temp_zip = tempfile.NamedTemporaryFile(delete=False,suffix = ".zip")
    zip_path = temp_zip.name
    temp_zip.close()

    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as zipf:
        for f in file:
            arcname = os.path.relpath(f.file_path,start=os.path.commonpath([f.file_path]))
            zipf.write(f.file_path,arcname=os.path.basename(f.file_path))
    # return {'folder name':folder.name,
    #         "file":[{'file name': f.file_name,
    #                 'file path':f.file_path}
    #                 for f in file]
    #                 }
    return FileResponse(path = zip_path,filename = f"{folder.name}.zip",media_type='application/zip' )

def delete_folder():
    while True:
        db = SessionLocal()
        try:
            expired = (db.query(model.Folder).filter(model.Folder.deleted_at.isnot(None),
            model.Folder.deleted_at <= datetime.utcnow()).all())
            for f in expired:
                folder_path = os.path.join(Upload_dir, f.name)
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
                db.delete(f)

            db.commit()

        except Exception as e:
            db.rollback()
            print("Error:", e)

        finally:
            db.close()

        time.sleep(300)

