from fastapi import FastAPI
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import httpx
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from uuid import uuid4
import asyncio
import sys
from playwright.async_api import async_playwright
from bson import ObjectId


# Correct Windows event loop policy
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient(os.getenv("MONGO_URI"))
db = client["jobtracker"]
jobs_collection = db["jobs"]




@app.post("/scrape/microsoft")
async def scrape_microsoft():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                viewport={"width": 1280, "height": 800}
            )
            page = await context.new_page()
            await page.goto("https://jobs.careers.microsoft.com/global/en/search", timeout=90000)

            await page.wait_for_selector('li.job-tile', timeout=15000)

            jobs = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('li.job-tile')).map(item => ({
                    title: item.querySelector('h3.job-title')?.innerText.trim() || '',
                    link: item.querySelector('a.job-title-link')?.href || '',
                    location: item.querySelector('span.job-location')?.innerText.trim() || 'Remote'
                }));
            }''')

            if not jobs:
                return {"error": "No jobs extracted"}

            jobs_with_meta = [dict(
                job,
                job_id=str(uuid4()),
                company="Microsoft",
                posted_date=datetime.now(),
                source="microsoft"
            ) for job in jobs]

            jobs_collection.delete_many({"source": "microsoft"})
            result = jobs_collection.insert_many(jobs_with_meta)

            return {
                "status": "success",
                "jobs_added": len(result.inserted_ids),
                "sample_job": jobs_with_meta[0]
            }

    except Exception as e:
        return {"error": str(e)}







@app.post("/scrape/brex")
async def scrape_brex():
    try:
        url = "https://www.brex.com/_next/data/wArwWKz_EVcGELMBhYgnK/careers.json"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

        jobs = data.get("jobs", [])
        if not jobs:
            return {"error": "No jobs found from Brex"}

        jobs_with_meta = []
        for job in jobs:
            jobs_with_meta.append({
                "job_id": str(uuid4()),
                "title": job.get("title", ""),
                "link": job.get("absolute_url", ""),
                "location": job.get("location", {}).get("name", "Remote"),
                "company": "Brex",
                "posted_date": datetime.now(),
                "source": "brex"
            })

        jobs_collection.delete_many({"source": "brex"})
        result = jobs_collection.insert_many(jobs_with_meta)

        return {
            "status": "success",
            "jobs_added": len(result.inserted_ids),
            "sample_job": jobs_with_meta[0] if jobs_with_meta else {}
        }

    except Exception as e:
        return {"error": str(e)}
 





@app.post("/scrape/jobber")
async def scrape_jobber():
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                viewport={"width": 1280, "height": 800}
            )
            page = await context.new_page()
            await page.goto("https://boards-api.greenhouse.io/v1/boards/jobber/jobs", timeout=90000)

            await page.wait_for_selector(".opening", timeout=15000)

            jobs = await page.evaluate("""() => {
                return Array.from(document.querySelectorAll('.opening')).map(item => {
                    const titleEl = item.querySelector('a');
                    const locationEl = item.querySelector('.location');
                    return {
                        title: titleEl?.innerText || '',
                        link: titleEl?.href || '',
                        location: locationEl?.innerText || 'Remote'
                    };
                });
            }""")

            if not jobs:
                return {"error": "No jobs found on Jobber careers page"}

            jobs_with_meta = [dict(
                job,
                job_id=str(uuid4()),
                company="Jobber",
                posted_date=datetime.now(),
                source="jobber"
            ) for job in jobs if job['title'] and job['link']]

            jobs_collection.delete_many({"source": "jobber"})
            result = jobs_collection.insert_many(jobs_with_meta)

            return {
                "status": "success",
                "jobs_added": len(result.inserted_ids),
                "sample_job": jobs_with_meta[0] if jobs_with_meta else {}
            }

    except Exception as e:
        return {"error": str(e)}
    





@app.post("/scrape/notion")
async def scrape_notion():
    try:
        url = "https://boards-api.greenhouse.io/v1/boards/notion/jobs"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = await response.json()

        jobs = data.get("jobs", [])

        if not jobs:
            return {"error": "No jobs found from Notion"}

        jobs_with_meta = [
            {
                "job_id": str(uuid4()),
                "title": job.get("title", ""),
                "link": f"https://boards.greenhouse.io/notion/jobs/{job.get('id')}",
                "location": job.get("location", {}).get("name", "Remote"),
                "company": "Notion",
                "posted_date": datetime.now(),
                "source": "notion"
            }
            for job in jobs if job.get("title") and job.get("id")
        ]

        jobs_collection.delete_many({"source": "notion"})
        result = jobs_collection.insert_many(jobs_with_meta)

        return {
            "status": "success",
            "jobs_added": len(result.inserted_ids),
            "sample_job": jobs_with_meta[0] if jobs_with_meta else {}
        }

    except Exception as e:
        return {"error": str(e)}




@app.post("/scrape/intercom")
async def scrape_intercom():
    try:
        url = "https://boards-api.greenhouse.io/v1/boards/intercom/jobs"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

        jobs = data.get("jobs", [])
        if not jobs:
            return {"error": "No jobs found from intercom"}

        jobs_with_meta = []
        for job in jobs:
            jobs_with_meta.append({
                "job_id": str(uuid4()),
                "title": job.get("title", ""),
                "link": job.get("absolute_url", ""),
                "location": job.get("location", {}).get("name", "Remote"),
                "company": "intercom",
                "posted_date": datetime.now(),
                "source": "intercom"
            })

        jobs_collection.delete_many({"source": "intercom"})
        result = jobs_collection.insert_many(jobs_with_meta)

        return {
            "status": "success",
            "jobs_added": len(result.inserted_ids),
            "sample_job": jobs_with_meta[0] if jobs_with_meta else {}
        }

    except Exception as e:
        return {"error": str(e)}
 




@app.post("/scrape/zoominfo")
async def scrape_zoominfo():
    try:
        url = "https://boards-api.greenhouse.io/v1/boards/zoominfo/jobs"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

        jobs = data.get("jobs", [])
        if not jobs:
            return {"error": "No jobs found from zoominfo"}

        jobs_with_meta = []
        for job in jobs:
            jobs_with_meta.append({
                "job_id": str(uuid4()),
                "title": job.get("title", ""),
                "link": job.get("absolute_url", ""),
                "location": job.get("location", {}).get("name", "Remote"),
                "company": "zoominfo",
                "posted_date": datetime.now(),
                "source": "zoominfo"
            })

        jobs_collection.delete_many({"source": "zoominfo"})
        result = jobs_collection.insert_many(jobs_with_meta)

        return {
            "status": "success",
            "jobs_added": len(result.inserted_ids),
            "sample_job": jobs_with_meta[0] if jobs_with_meta else {}
        }

    except Exception as e:
        return {"error": str(e)}






@app.post("/scrape/circleci")
async def scrape_circleci():
    try:
        url = "https://boards-api.greenhouse.io/v1/boards/circleci/jobs"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()

        jobs = data.get("jobs", [])
        if not jobs:
            return {"error": "No jobs found from circleci"}

        jobs_with_meta = []
        for job in jobs:
            jobs_with_meta.append({
                "job_id": str(uuid4()),
                "title": job.get("title", ""),
                "link": job.get("absolute_url", ""),
                "location": job.get("location", {}).get("name", "Remote"),
                "company": "circleci",
                "posted_date": datetime.now(),
                "source": "circleci"
            })

        jobs_collection.delete_many({"source": "circleci"})
        result = jobs_collection.insert_many(jobs_with_meta)

        return {
            "status": "success",
            "jobs_added": len(result.inserted_ids),
            "sample_job": jobs_with_meta[0] if jobs_with_meta else {}
        }

    except Exception as e:
        return {"error": str(e)}

def serialize_job(job):
    job = dict(job)
    if '_id' in job:
        job['_id'] = str(job['_id'])
    return job


@app.get("/jobs")
async def get_jobs(company: str = Query(None)):
    query = {"company": company} if company else {}
    jobs = list(
        jobs_collection
        .find(query, {"_id": 0})
        .sort("posted_date", -1)
        .limit(5000)
    )
    return {"jobs": jobs}


@app.post("/cleanup")
async def cleanup_jobs():
    try:
        cutoff_date = datetime.now() - timedelta(days=50)
        result = jobs_collection.delete_many({"posted_date": {"$lt": cutoff_date}})
        return {
            "status": "success",
            "deleted_count": result.deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)