# JobListingTracker


 Job Scraper 🕵️ – Scrapes jobs from multiple sites (including Microsoft) and displays them.  

---
 📂 Project Structure
```
│── job-scraper/           # Job Scraper app
│   ├── backend/       # FastAPI backend for scraping jobs
│   ├── frontend/      # Frontend to display scraped jobs

```
 1️⃣ Job Scraper App



The **Job Scraper** fetches job postings from career websites (like Microsoft) and displays:

- Job Title  
- Company  
- Location  
- Application Link  

 ⚙️ Setup

 Backend
```bash
cd job-scraper/backend
python -m venv .venv
.venv\Scripts\activate   # (Windows)
# source .venv/bin/activate   # (Linux/Mac)

uvicorn main:app --reload --port 5000

````
Backend runs at:

```
http://127.0.0.1:5000
```

Frontend

```bash
cd job-scraper/frontend
npm install
npm start
```

Frontend runs at:
```
http://localhost:3000



```

