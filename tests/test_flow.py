import os,sys,tempfile,unittest
from pathlib import Path
from fastapi.testclient import TestClient

class FlowTests(unittest.TestCase):
 def test_teacher_to_student_to_results(self):
  with tempfile.TemporaryDirectory() as d:
   os.environ['DATABASE_URL']='sqlite:///'+str(Path(d)/'test.db')
   os.environ['SECRET_KEY']='test-secret-only'
   sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
   import importlib
   if 'main' in sys.modules: del sys.modules['main']
   m=importlib.import_module('main')
   with TestClient(m.app) as c:
    self.assertEqual(c.get('/api/health').json(),{'ok':True})
    r=c.post('/api/register',json={'name':'Giáo viên A','email':'gv@example.com','password':'securepass123'})
    self.assertEqual(r.status_code,200,r.text)
    h={'Authorization':'Bearer '+r.json()['token']}
    cid=c.post('/api/classes',json={'name':'12C2','subject':'Tất cả môn'},headers=h).json()['id']
    self.assertEqual(c.post(f'/api/classes/{cid}/students',json={'name':'Học sinh A','code':'HS01'},headers=h).status_code,200)
    data={'title':'Kiểm tra','subject':'Địa lí','classroom_id':cid,'questions':[{'text':'Thủ đô Việt Nam?','options':['Hà Nội','Huế'],'answer':0}],'pixels':['#ff0000']*100}
    r=c.post('/api/games',json=data,headers=h);self.assertEqual(r.status_code,200,r.text)
    code=r.json()['code'];game=c.get('/api/play/'+code).json()
    self.assertNotIn('answer',str(game))
    self.assertEqual(c.post(f'/api/play/{code}/submit',json={'name':'Học sinh A','code':'','answers':[0]}).status_code,422)
    self.assertEqual(c.post(f'/api/play/{code}/submit',json={'name':'Học sinh A','code':'HS01','answers':[-1]}).status_code,422)
    r=c.post(f'/api/play/{code}/submit',json={'name':'Học sinh A','code':'HS01','answers':[0]})
    self.assertEqual(r.status_code,200,r.text);self.assertEqual(r.json()['score'],1)
    gid=c.get('/api/games',headers=h).json()[0]['id']
    self.assertEqual(c.get(f'/api/games/{gid}/results',headers=h).json()[0]['score'],1)
    self.assertEqual(c.get(f'/api/games/{gid}/results').status_code,401)
    stats=c.get(f'/api/games/{gid}/summary',headers=h).json()
    self.assertEqual((stats['students'],stats['attempts'],stats['average_percent']),(1,1,100.0))
    by_student=c.get(f'/api/games/{gid}/student-summary',headers=h)
    self.assertEqual(by_student.status_code,200)
    self.assertEqual(by_student.json()[0]['best_score'],1)
    self.assertEqual(by_student.json()[0]['attempts'],1)
    self.assertEqual(c.get(f'/api/games/{gid}/student-summary').status_code,401)
    self.assertEqual(c.patch(f'/api/games/{gid}/status?active=false',headers=h).status_code,200)
    self.assertEqual(c.get('/api/play/'+code).status_code,404)
    self.assertEqual(c.patch(f'/api/games/{gid}/status?active=true',headers=h).json()['active'],True)
    self.assertEqual(c.get('/api/play/'+code).status_code,200)
if __name__=='__main__':unittest.main()
