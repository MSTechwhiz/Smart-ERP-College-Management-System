cd backend
venv\Scripts\activate
uvicorn app.main:app --reload

cd frontend
npm init 
npm install 
npm start