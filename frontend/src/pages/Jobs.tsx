import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import type { Job } from '../types/job';
import { getJobs } from '../services/jobService';
import JobStatusBadge from '../components/JobStatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchJobs = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await getJobs();
      setJobs(data);
    } catch {
      setError('Unable to connect to the server.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    let ignore = false;
    async function load() {
      try {
        const data = await getJobs();
        if (!ignore) setJobs(data);
      } catch {
        if (!ignore) setError('Unable to connect to the server.');
      } finally {
        if (!ignore) setIsLoading(false);
      }
    }
    load();
    return () => { ignore = true; };
  }, []);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString();
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading jobs..." />;
  }

  if (error) {
    return <ErrorMessage message={error} onRetry={fetchJobs} />;
  }

  return (
    <div className="jobs-page">
      <div className="jobs-header">
        <h1>My Jobs</h1>
        <Link to="/create-job" className="btn-primary">Create Job</Link>
      </div>

      {jobs.length === 0 ? (
        <div className="empty-state">
          <p>No jobs yet.</p>
          <Link to="/create-job" className="btn-primary">Create your first job</Link>
        </div>
      ) : (
        <div className="jobs-list">
          {jobs.map((job) => (
            <Link key={job.id} to={`/jobs/${job.id}`} className="job-card card">
              <div className="job-card-header">
                <span className="job-id">Job #{job.id}</span>
                <JobStatusBadge status={job.status} />
              </div>
              <div className="job-card-body">
                <p><strong>Operation:</strong> {job.operation}</p>
                <p><strong>Resource:</strong> #{job.resource}</p>
                <p><strong>Created:</strong> {formatDate(job.created_at)}</p>
                {job.completed_at && (
                  <p><strong>Completed:</strong> {formatDate(job.completed_at)}</p>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
