import { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'http://localhost:5000';

function App() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [scraping, setScraping] = useState({
    microsoft: false,
    brex: false,
    jobber:false,
    notion:false,
    intercom:false,
    zoominfo:false,
    circleci:false
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/jobs`);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || 'Failed to fetch jobs');
      }
      
      const data = await response.json();
      const validatedJobs = Array.isArray(data?.jobs) 
        ? data.jobs.map(job => ({
            title: job.title || 'No Title Available',
            company: job.company || 'Unknown Company',
            location: job.location || 'Location Not Specified',
            link: job.link || '',
            posted_date: job.posted_date || new Date().toISOString(),
            job_id: job.job_id || job.link || Math.random().toString(36).substring(7)
          }))
        : [];
      setJobs(validatedJobs);
    } catch (err) {
      setError(`Fetch Error: ${err.message}`);
      console.error('Fetch Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const triggerScrape = async (company) => {
    try {
      setScraping(prev => ({ ...prev, [company]: true }));
      setError(null);
      
      const response = await fetch(`${API_BASE_URL}/scrape/${company}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `Server returned ${response.status}`);
      }

      const result = await response.json();
      setSuccess(`Added ${result.jobs_added} ${company} jobs`);
      await fetchJobs();
    } catch (err) {
      console.error('Full error:', err);
      setError(`Scrape failed: ${err.message}`);
    } finally {
      setScraping(prev => ({ ...prev, [company]: false }));
    }
  };

  const triggerCleanup = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/cleanup`, { 
        method: 'POST' 
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || 'Cleanup failed');
      }
      
      const result = await response.json();
      setSuccess(`Cleaned up ${result.deleted_count} old jobs`);
      await fetchJobs();
    } catch (err) {
      setError(`Cleanup Error: ${err.message}`);
      console.error('Cleanup Error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { 
    fetchJobs(); 
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      setSuccess(null);
      setError(null);
    }, 5000);
    return () => clearTimeout(timer);
  }, [success, error]);

  const renderJobCard = (job) => {
    const company = job.company || 'Unknown Company';
    const title = job.title || 'No Title Available';
    const location =
  typeof job.location === 'string'
    ? job.location
    : job.location?.name || 'Location Not Specified';
    const postedDate = job.posted_date 
      ? new Date(job.posted_date).toLocaleDateString() 
      : 'Date Unavailable';
    const jobId = job.job_id || job.link || Math.random().toString(36).substring(7);

    return (
      <div key={`${company}-${jobId}`} className={`job-card ${company.toLowerCase()}`}>
        <div className="job-header">
          <h3>{title}</h3>
          <span className={`company-tag ${company.toLowerCase()}`}>
            {company}
          </span>
        </div>
        <p className="location">
          <i className="fas fa-map-marker-alt"></i> {location}
        </p>
        <p className="posted-date">
          <i className="far fa-clock"></i> Posted: {postedDate}
        </p>
        {job.link && (
          <a 
            href={job.link} 
            target="_blank" 
            rel="noopener noreferrer"
            className="apply-btn"
          >
            View Job <i className="fas fa-external-link-alt"></i>
          </a>
        )}
      </div>
    );
  };

  return (
    <div className="app">
      <header>
        <h1>Tech Job Tracker</h1>
        <p className="subtitle">Finding Best Jobs For You</p>
      </header>

      <div className="controls">
        <button 
          onClick={() => triggerScrape('microsoft')}
          disabled={scraping.microsoft}
          className={`microsoft-btn ${scraping.microsoft ? 'loading' : ''}`}
        >
          {scraping.microsoft ? 'Scraping...' : 'Scrape Microsoft Jobs'}
        </button>
        
        <button 
          onClick={() => triggerScrape('brex')}
          disabled={scraping.brex}
          className={`brex-bt ${scraping.brex ? 'loading' : ''}`}
        >
          {scraping.brex ? 'Scraping...' : 'Scrape Brex Jobs'}
        </button>

        <button 
          onClick={() => triggerScrape('jobber')}
          disabled={scraping.jobber}
          className={`jobber-btn ${scraping.jobber ? 'loading' : ''}`}
        >
          {scraping.jobber ? 'Scraping...' : 'Scrape Jobber Jobs'}
        </button>
        
        <button 
          onClick={() => triggerScrape('notion')}
          disabled={scraping.notion}
          className={`notion-btn ${scraping.notion ? 'loading' : ''}`}
        >
          {scraping.notion ? 'Scraping...' : 'Scrape notion Jobs'}
        </button>

        <button 
          onClick={() => triggerScrape('intercom')}
          disabled={scraping.intercom}
          className={`intercom-btn ${scraping.intercom ? 'loading' : ''}`}
        >
          {scraping.intercom ? 'Scraping...' : 'Scrape Intercom Jobs'}
        </button>

        <button 
          onClick={() => triggerScrape('zoominfo')}
          disabled={scraping.zoominfo}
          className={`zoominfo-btn ${scraping.zoominfo ? 'loading' : ''}`}
        >
          {scraping.zoominfo ? 'Scraping...' : 'Scrape Zoominfo Jobs'}
        </button>

        <button 
          onClick={() => triggerScrape('circleci')}
          disabled={scraping.circleci}
          className={`circleci-btn ${scraping.circleci ? 'loading' : ''}`}
        >
          {scraping.circleci ? 'Scraping...' : 'Scrape Circleci Jobs'}
        </button>

        <button 
          onClick={triggerCleanup}
          disabled={loading}
          className="cleanup-btn"
        >
          {loading ? 'Cleaning...' : 'Cleanup Old Jobs (30+ days)'}
        </button>
      </div>

      {error && <div className="alert error">{error}</div>}
      {success && <div className="alert success">{success}</div>}

      {loading ? (
        <div className="loading-spinner"></div>
      ) : jobs.length === 0 ? (
        <div className="empty-state">
          <p>No jobs found. Try scraping first!</p>
        </div>
      ) : (
        <div className="job-list">
          {jobs.map(renderJobCard)}
        </div>
      )}
    </div>
  );
}

export default App;