import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { isAxiosError } from 'axios';
import type { Job } from '../types/job';
import { getJob } from '../services/jobService';
import { API_BASE_URL } from '../services/api';
import JobStatusBadge from '../components/JobStatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

export default function JobDetails() {
  const { id } = useParams();
  const [job, setJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const jobId = Number(id);

  useEffect(() => {
    let isMounted = true;

    const fetchJob = async () => {
      try {
        const data = await getJob(jobId);
        if (!isMounted) return;
        setJob(data);
        setIsLoading(false);
        setError('');

        // Stop polling if job reached a terminal state
        if (data.status === 'COMPLETED' || data.status === 'FAILED') {
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
            intervalRef.current = null;
          }
        }
      } catch (err) {
        if (!isMounted) return;
        setIsLoading(false);
        if (isAxiosError(err) && err.response?.status === 404) {
          setError('Job not found.');
        } else {
          setError('Unable to connect to the server.');
        }
        // Stop polling on error
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    };

    // Initial fetch
    fetchJob();

    // Start polling every 2 seconds
    intervalRef.current = setInterval(fetchJob, 2000);

    return () => {
      isMounted = false;
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [jobId]);

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleString();
  };

  // Build the full URL for a file path returned by the backend
  const getFileUrl = (filePath: string) => {
    if (!filePath) return '';
    // If the backend returns a full URL, use it directly
    if (filePath.startsWith('http')) return filePath;
    // Otherwise, prepend the API base URL
    return `${API_BASE_URL}${filePath.startsWith('/') ? '' : '/'}${filePath}`;
  };

  const statusMessages: Record<string, string> = {
    PENDING: 'Your job is queued for processing.',
    RUNNING: 'Your job is currently being processed.',
    COMPLETED: 'Processing completed.',
    FAILED: 'Processing failed.',
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading job details..." />;
  }

  if (error) {
    return (
      <div className="job-details-page">
        <div className="error-message">
          <p>{error}</p>
          <Link to="/jobs" className="btn-secondary">Back to Jobs</Link>
        </div>
      </div>
    );
  }

  if (!job) return null;

  const isProcessing = job.status === 'PENDING' || job.status === 'RUNNING';
  const isCompleted = job.status === 'COMPLETED';
  const isFailed = job.status === 'FAILED';
  const isImageResult = job.operation === 'RESIZE' && job.result_file;

  return (
    <div className="job-details-page">
      <div className="job-details-header">
        <h1>Job #{job.id}</h1>
        <JobStatusBadge status={job.status} />
      </div>

      {/* Status message */}
      <div className={`job-status-message status-msg-${job.status.toLowerCase()}`}>
        {isProcessing && <div className="spinner spinner-small" />}
        <p>{statusMessages[job.status]}</p>
      </div>

      {/* Job info */}
      <div className="job-info-grid">
        <div className="job-info-item">
          <span className="job-info-label">Resource</span>
          <span className="job-info-value">#{job.resource}</span>
        </div>
        <div className="job-info-item">
          <span className="job-info-label">Operation</span>
          <span className="job-info-value">{job.operation}</span>
        </div>
        <div className="job-info-item">
          <span className="job-info-label">Parameters</span>
          <span className="job-info-value">
            {Object.keys(job.parameters).length > 0
              ? JSON.stringify(job.parameters)
              : 'None'}
          </span>
        </div>
        <div className="job-info-item">
          <span className="job-info-label">Created</span>
          <span className="job-info-value">{formatDate(job.created_at)}</span>
        </div>
        <div className="job-info-item">
          <span className="job-info-label">Started</span>
          <span className="job-info-value">{formatDate(job.started_at)}</span>
        </div>
        <div className="job-info-item">
          <span className="job-info-label">Completed</span>
          <span className="job-info-value">{formatDate(job.completed_at)}</span>
        </div>
        {job.input_file && (
          <div className="job-info-item">
            <span className="job-info-label">Input File</span>
            <span className="job-info-value">{job.input_file.split('/').pop()}</span>
          </div>
        )}
      </div>

      {/* Error message for failed jobs */}
      {isFailed && job.error_message && (
        <div className="auth-error">
          <strong>Error:</strong> {job.error_message}
        </div>
      )}

      {/* Result section for completed jobs */}
      {isCompleted && (
        <div className="job-result-section">
          <h2>Result</h2>
          {job.result_file ? (
            <>
              {isImageResult && (
                <div className="result-image-container">
                  <img
                    src={getFileUrl(job.result_file)}
                    alt="Resize result"
                    className="result-image"
                  />
                </div>
              )}
              <a
                href={getFileUrl(job.result_file)}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary"
              >
                Download Result
              </a>
            </>
          ) : (
            <p>Result is not available yet.</p>
          )}
        </div>
      )}

      <div className="job-details-actions">
        <Link to="/jobs" className="btn-secondary">Back to Jobs</Link>
        <Link to="/create-job" className="btn-secondary">Create Another Job</Link>
      </div>
    </div>
  );
}
