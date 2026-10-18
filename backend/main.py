import os, secrets, hashlib, hmac, json, random, string
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, Boolean, select
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

DB=os.getenv('DATABASE_URL','sqlite:///./matrix.db').replace('postgres://','postgresql://',1)
engine=create_engine(DB,connect_args={'check_same_thread':False} if DB.startswith('sqlite') else {},pool_pre_ping=True)
SessionLocal=sessionmaker(bind=engine)
Base=declarative_base()
class Teacher(Base):
 __tablename__='teachers'; id=Column(Integer,primary_key=True); name=Column(String(120)); email=Column(String(200),unique=True,index=True); password=Column(String(250))
class Classroom(Base):
 __tablename__='classes'; id=Column(Integer,primary_key=True); teacher_id=Column(Integer,ForeignKey('teachers.id')); name=Column(String(100)); subject=Column(String(100))
class Student(Base):
 __tablename__='students'; id=Column(Integer,primary_key=True); classroom_id=Column(Integer,ForeignKey('classes.id')); code=Column(String(50)); name=Column(String(120))
class Game(Base):
 __tablename__='games'; id=Column(Integer,primary_key=True); teacher_id=Column(Integer,ForeignKey('teachers.id')); classroom_id=Column(Integer,ForeignKey('classes.id')); code=Column(String(10),unique=True,index=True); title=Column(String(200)); subject=Column(String(100)); questions=Column(Text); pixels=Column(Text); active=Column(Boolean,default=True)
class Attempt(Base):
 __tablename__='attempts'; id=Column(Integer,primary_key=True); game_id=Column(Integer,ForeignKey('games.id')); student_id=Column(Integer,ForeignKey('students.id'),nullable=True); student_name=Column(String(120)); student_code=Column(String(50)); score=Column(Integer); total=Column(Integer); answers=Column(Text); created=Column(DateTime,default=lambda:datetime.now(timezone.utc))
Base.metadata.create_all(engine)
app=FastAPI(title='Ma tran sac mau API')
origins=os.getenv('CORS_ORIGINS','http://localhost:5173,http://127.0.0.1:5173').split(',')
app.add_middleware(CORSMiddleware,allow_origins=origins,allow_credentials=False,allow_methods=['*'],allow_headers=['*'])
secret=os.getenv('SECRET_KEY','development-only-change-me')
if os.getenv('APP_ENV')=='production' and secret=='development-only-change-me':
 raise RuntimeError('SECRET_KEY must be configured in production')
signer=URLSafeTimedSerializer(secret)
def db():
 with SessionLocal() as s: yield s
def hashed(p):
 salt=secrets.token_hex(16); key=hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(salt),260000).hex();return salt+':'+key
def verify(p,stored):
 try:
  salt,key=stored.split(':'); return hmac.compare_digest(hashlib.pbkdf2_hmac('sha256',p.encode(),bytes.fromhex(salt),260000).hex(),key)
 except Exception:return False
def auth(authorization:Optional[str]=Header(None),s:Session=Depends(db)):
 if not authorization or not authorization.startswith('Bearer '):raise HTTPException(401,'Cần đăng nhập')
 try: ident=signer.loads(authorization[7:],max_age=60*60*24*7)
 except (BadSignature,SignatureExpired):raise HTTPException(401,'Phiên đăng nhập hết hạn')
 t=s.get(Teacher,ident)
 if not t:raise HTTPException(401,'Không tìm thấy tài khoản')
 return t
class Account(BaseModel):
 name:str=Field(min_length=2,max_length=120); email:str=Field(min_length=5,max_length=200); password:str=Field(min_length=8,max_length=100)
class Login(BaseModel):
 email:str=Field(min_length=5,max_length=200); password:str
class ClassIn(BaseModel):
 name:str=Field(min_length=1,max_length=100); subject:str=Field(default='Tất cả môn',max_length=100)
class StudentIn(BaseModel):
 name:str=Field(min_length=1,max_length=120); code:str=Field(min_length=1,max_length=50)
class Question(BaseModel):
 text:str=Field(min_length=1,max_length=1000); options:list[str]=Field(min_length=2,max_length=6); answer:int=Field(ge=0,le=5)
class GameIn(BaseModel):
 title:str=Field(min_length=1,max_length=200); subject:str=Field(default='Tổng hợp',max_length=100); classroom_id:int; questions:list[Question]=Field(min_length=1,max_length=100); pixels:list[str]=Field(min_length=1,max_length=400)
class Submit(BaseModel):
 name:str=Field(min_length=1,max_length=120); code:str=Field(default='',max_length=50); answers:list[int]=Field(max_length=100)
@app.get('/api/health')
def health():return {'ok':True}
@app.post('/api/register')
def register(a:Account,s:Session=Depends(db)):
 email=a.email.strip().lower()
 if '@' not in email or '.' not in email.split('@')[-1]:raise HTTPException(422,'Email không hợp lệ')
 if s.scalar(select(Teacher).where(Teacher.email==email)):raise HTTPException(409,'Email đã được sử dụng')
 t=Teacher(name=a.name.strip(),email=email,password=hashed(a.password));s.add(t);s.commit();s.refresh(t);return {'token':signer.dumps(t.id),'name':t.name}
@app.post('/api/login')
def login(a:Login,s:Session=Depends(db)):
 t=s.scalar(select(Teacher).where(Teacher.email==a.email.strip().lower()))
 if not t or not verify(a.password,t.password):raise HTTPException(401,'Email hoặc mật khẩu không đúng')
 return {'token':signer.dumps(t.id),'name':t.name}
@app.get('/api/classes')
def classes(t:Teacher=Depends(auth),s:Session=Depends(db)):
 return [{'id':c.id,'name':c.name,'subject':c.subject} for c in s.scalars(select(Classroom).where(Classroom.teacher_id==t.id)).all()]
@app.post('/api/classes')
def create_class(a:ClassIn,t:Teacher=Depends(auth),s:Session=Depends(db)):
 c=Classroom(teacher_id=t.id,**a.model_dump());s.add(c);s.commit();s.refresh(c);return {'id':c.id}
@app.get('/api/classes/{cid}/students')
def students(cid:int,t:Teacher=Depends(auth),s:Session=Depends(db)):
 c=s.get(Classroom,cid)
 if not c or c.teacher_id!=t.id:raise HTTPException(404,'Không tìm thấy lớp')
 return [{'id':x.id,'name':x.name,'code':x.code} for x in s.scalars(select(Student).where(Student.classroom_id==cid)).all()]
@app.post('/api/classes/{cid}/students')
def add_student(cid:int,a:StudentIn,t:Teacher=Depends(auth),s:Session=Depends(db)):
 c=s.get(Classroom,cid)
 if not c or c.teacher_id!=t.id:raise HTTPException(404,'Không tìm thấy lớp')
 if s.scalar(select(Student).where(Student.classroom_id==cid,Student.code==a.code.strip())):raise HTTPException(409,'Mã học sinh đã tồn tại trong lớp')
 st=Student(classroom_id=cid,name=a.name.strip(),code=a.code.strip());s.add(st);s.commit();s.refresh(st);return {'id':st.id}
def own_class(s,t,cid):
 c=s.get(Classroom,cid)
 if not c or c.teacher_id!=t.id:raise HTTPException(404,'Không tìm thấy lớp')
@app.post('/api/games')
def create_game(a:GameIn,t:Teacher=Depends(auth),s:Session=Depends(db)):
 own_class(s,t,a.classroom_id)
 for q in a.questions:
  if q.answer>=len(q.options):raise HTTPException(422,'Đáp án nằm ngoài số phương án')
 code=''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(6))
 while s.scalar(select(Game).where(Game.code==code)):code=''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(6))
 g=Game(teacher_id=t.id,classroom_id=a.classroom_id,code=code,title=a.title,subject=a.subject,questions=json.dumps([q.model_dump() for q in a.questions],ensure_ascii=False),pixels=json.dumps(a.pixels));s.add(g);s.commit();return {'code':code}
@app.get('/api/games')
def my_games(t:Teacher=Depends(auth),s:Session=Depends(db)):
 return [{'id':g.id,'code':g.code,'title':g.title,'subject':g.subject,'classroom_id':g.classroom_id,'active':g.active} for g in s.scalars(select(Game).where(Game.teacher_id==t.id).order_by(Game.id.desc())).all()]
@app.get('/api/play/{code}')
def play(code:str,s:Session=Depends(db)):
 g=s.scalar(select(Game).where(Game.code==code.upper(),Game.active==True))
 if not g:raise HTTPException(404,'Mã trò chơi không hợp lệ')
 questions=json.loads(g.questions)
 return {'title':g.title,'subject':g.subject,'code':g.code,'questions':[{'text':q['text'],'options':q['options']} for q in questions],'pixels':[]}
@app.post('/api/play/{code}/submit')
def submit(code:str,a:Submit,s:Session=Depends(db)):
 g=s.scalar(select(Game).where(Game.code==code.upper(),Game.active==True))
 if not g:raise HTTPException(404,'Trò chơi không tồn tại')
 qs=json.loads(g.questions)
 if len(a.answers)!=len(qs):raise HTTPException(422,'Chưa hoàn tất câu hỏi')
 if any(not isinstance(v,int) or isinstance(v,bool) or v<0 or v>=len(q['options']) for v,q in zip(a.answers,qs)):
  raise HTTPException(422,'Đáp án không hợp lệ')
 if s.scalar(select(Student.id).where(Student.classroom_id==g.classroom_id)) and not a.code.strip():
  raise HTTPException(422,'Lớp đã có danh sách học sinh, cần nhập mã học sinh')
 student=None
 if a.code.strip():
  student=s.scalar(select(Student).where(Student.classroom_id==g.classroom_id,Student.code==a.code.strip()))
  if not student:raise HTTPException(400,'Mã học sinh không thuộc lớp')
  if student.name.casefold().strip()!=a.name.casefold().strip():raise HTTPException(400,'Họ tên không khớp mã học sinh')
 correct=[v==q['answer'] for v,q in zip(a.answers,qs)]
 score=sum(correct)
 attempt=Attempt(game_id=g.id,student_id=student.id if student else None,student_name=a.name.strip(),student_code=a.code.strip(),score=score,total=len(qs),answers=json.dumps(a.answers));s.add(attempt);s.commit()
 return {'score':score,'total':len(qs),'correct':correct,'pixels':json.loads(g.pixels)}
@app.get('/api/games/{gid}/results')
def results(gid:int,t:Teacher=Depends(auth),s:Session=Depends(db)):
 g=s.get(Game,gid)
 if not g or g.teacher_id!=t.id:raise HTTPException(404,'Không tìm thấy trò chơi')
 return [{'name':a.student_name,'code':a.student_code,'score':a.score,'total':a.total,'created':a.created.isoformat()} for a in s.scalars(select(Attempt).where(Attempt.game_id==gid).order_by(Attempt.id.desc())).all()]

@app.get('/api/games/{gid}/summary')
def game_summary(gid:int,t:Teacher=Depends(auth),s:Session=Depends(db)):
 g=s.get(Game,gid)
 if not g or g.teacher_id!=t.id:raise HTTPException(404,'Không tìm thấy trò chơi')
 attempts=s.scalars(select(Attempt).where(Attempt.game_id==gid)).all()
 unique={a.student_code.strip() or a.student_name.strip().casefold() for a in attempts}
 return {'attempts':len(attempts),'students':len(unique),'average_percent':round(sum(a.score/a.total*100 for a in attempts)/len(attempts),1) if attempts else 0,'perfect_attempts':sum(a.score==a.total for a in attempts)}

@app.patch('/api/games/{gid}/status')
def change_game_status(gid:int,active:bool,t:Teacher=Depends(auth),s:Session=Depends(db)):
 g=s.get(Game,gid)
 if not g or g.teacher_id!=t.id:raise HTTPException(404,'Không tìm thấy trò chơi')
 g.active=active;s.commit();return {'id':gid,'active':active}

@app.get('/api/games/{gid}/student-summary')
def student_summary(gid:int,t:Teacher=Depends(auth),s:Session=Depends(db)):
 g=s.get(Game,gid)
 if not g or g.teacher_id!=t.id:raise HTTPException(404,'Không tìm thấy trò chơi')
 attempts=s.scalars(select(Attempt).where(Attempt.game_id==gid).order_by(Attempt.id)).all()
 grouped={}
 for a in attempts:
  key=('id',a.student_id) if a.student_id else ('guest',a.student_code.strip() or a.student_name.strip().casefold())
  if key not in grouped:grouped[key]={'name':a.student_name,'code':a.student_code,'attempts':0,'best_score':0,'last_score':0,'total':a.total,'sum_score':0}
  item=grouped[key];item['attempts']+=1;item['best_score']=max(item['best_score'],a.score);item['last_score']=a.score;item['sum_score']+=a.score
 return sorted([{'name':x['name'],'code':x['code'],'attempts':x['attempts'],'best_score':x['best_score'],'last_score':x['last_score'],'average_score':round(x['sum_score']/x['attempts'],2),'total':x['total']} for x in grouped.values()],key=lambda x:(-x['best_score'],x['name']))

# Standalone online UI: no Node.js or client installation required for visitors.
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
ONLINE_DIR=Path(__file__).resolve().parents[1]/'online'
app.mount('/online',StaticFiles(directory=str(ONLINE_DIR)),name='online-assets')
@app.get('/',include_in_schema=False)
def online_home():return FileResponse(ONLINE_DIR/'index.html')
