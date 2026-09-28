import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { isAxiosError } from 'axios';
import type { Job } from '../types/job';
import { getJob } from '../services/jobService';
import { API_BASE_URL } from '../services/api';
import JobStatusBadge from '../components/JobStatusBadge';
import LoadingSpinner from '../components/LoadingSpinner';

type ResultData = {
  [key: string]: unknown;
};

type ColumnInfo = {
  name: string;
  type: string;
  missing?: number;
  unknown?: number;
  unique?: number;
  statistics?: {
    min: number | null;
    max: number | null;
    mean: number | null;
  } | null;
};

export default function JobDetails() {
  const { id } = useParams();
  const [job, setJob] = useState<Job | null>(null);
  const [resultData, setResultData] = useState<ResultData | null>(null);
  const [resultError, setResultError] = useState('');
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

        if (intervalRef.current) {
          clearInterval(intervalRef.current);
          intervalRef.current = null;
        }
      }
    };

    fetchJob();
    intervalRef.current = setInterval(fetchJob, 2000);

    return () => {
      isMounted = false;

      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [jobId]);

  useEffect(() => {
    if (!job?.result_file || job.status !== 'COMPLETED') {
      setResultData(null);
      return;
    }

    if (job.operation === 'RESIZE' || job.operation === 'GRAYSCALE') {
      return;
    }

    const loadResult = async () => {
      try {
        setResultError('');
        const response = await fetch(getFileUrl(job.result_file));

        if (!response.ok) {
          throw new Error('Unable to load result.');
        }

        const data = await response.json();
        setResultData(data);
      } catch {
        setResultError('Unable to load the result data.');
      }
    };

    loadResult();
  }, [job]);

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleString();
  };

  const getFileUrl = (filePath: string) => {
    if (!filePath) return '';
    if (filePath.startsWith('http')) return filePath;

    return `${API_BASE_URL}${filePath.startsWith('/') ? '' : '/'}${filePath}`;
  };

  const statusMessages: Record<string, string> = {
    PENDING: 'Your job is queued for processing.',
    RUNNING: 'Your job is currently being processed.',
    COMPLETED: 'Processing completed.',
    FAILED: 'Processing failed.',
  };

  const isImageOperation =
    job?.operation === 'RESIZE' || job?.operation === 'GRAYSCALE';

  const renderCsvResult = () => {
    if (!resultData) return null;

    const columns = Array.isArray(resultData.columns_info)
      ? (resultData.columns_info as ColumnInfo[])
      : [];

    if (job?.operation === 'VALIDATE') {
      const valid = Boolean(resultData.valid);
      const errors = Array.isArray(resultData.errors)
        ? (resultData.errors as Array<{
            column: string;
            row?: number | null;
            message: string;
          }>)
        : [];

      return (
        <div className="result-data">
          <div className={`validation-result ${valid ? 'valid' : 'invalid'}`}>
            <strong>{valid ? 'CSV is valid' : 'CSV validation failed'}</strong>
            <span>
              {valid
                ? 'The uploaded CSV matches the expected schema.'
                : `${errors.length} validation error${errors.length === 1 ? '' : 's'}.`}
            </span>
          </div>

          {errors.length > 0 && (
            <div className="result-table-container">
              <table className="result-table">
                <thead>
                  <tr>
                    <th>Column</th>
                    <th>Row</th>
                    <th>Message</th>
                  </tr>
                </thead>
                <tbody>
                  {errors.map((item, index) => (
                    <tr key={`${item.column}-${item.row}-${index}`}>
                      <td>{item.column}</td>
                      <td>{item.row ?? '—'}</td>
                      <td>{item.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      );
    }

    return (
      <div className="result-data">
        <div className="result-summary">
          <div>
            <strong>{String(resultData.rows ?? 0)}</strong>
            <span>Rows</span>
          </div>
          <div>
            <strong>{String(resultData.columns ?? 0)}</strong>
            <span>Columns</span>
          </div>
        </div>

        {columns.length > 0 && (
          <div className="result-table-container">
            <table className="result-table">
              <thead>
                <tr>
                  <th>Column</th>
                  <th>Type</th>
                  <th>Missing</th>
                  <th>Unknown</th>
                  <th>Unique</th>
                  {job?.operation === 'ANALYZE' && <th>Statistics</th>}
                </tr>
              </thead>
              <tbody>
                {columns.map((column) => (
                  <tr key={column.name}>
                    <td>{column.name}</td>
                    <td>{column.type}</td>
                    <td>{column.missing ?? 0}</td>
                    <td>{column.unknown ?? 0}</td>
                    <td>{column.unique ?? 0}</td>
                    {job?.operation === 'ANALYZE' && (
                      <td>
                        {column.statistics
                          ? `Min: ${column.statistics.min ?? '—'} | Max: ${
                              column.statistics.max ?? '—'
                            } | Mean: ${
                              column.statistics.mean?.toFixed(2) ?? '—'
                            }`
                          : '—'}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return <LoadingSpinner message="Loading job details..." />;
  }

  if (error) {
    return (
      <div className="job-details-page">
        <div className="error-message">
          <p>{error}</p>
          <Link to="/jobs" className="btn-secondary">
            Back to Jobs
          </Link>
        </div>
      </div>
    );
  }

  if (!job) return null;

  const isProcessing = job.status === 'PENDING' || job.status === 'RUNNING';
  const isCompleted = job.status === 'COMPLETED';
  const isFailed = job.status === 'FAILED';

  return (
    <div className="job-details-page">
      <div className="job-details-header">
        <h1>Job #{job.id}</h1>
        <JobStatusBadge status={job.status} />
      </div>

      <div className={`job-status-message status-msg-${job.status.toLowerCase()}`}>
        {isProcessing && <div className="spinner spinner-small" />}
        <p>{statusMessages[job.status]}</p>
      </div>

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
            <span className="job-info-value">
              {job.input_file.split('/').pop()}
            </span>
          </div>
        )}
      </div>

      {isFailed && job.error_message && (
        <div className="auth-error">
          <strong>Error:</strong> {job.error_message}
        </div>
      )}

      {isCompleted && (
        <div className="job-result-section">
          <h2>Result</h2>

          {job.result_file ? (
            <>
              {isImageOperation ? (
                <div className="result-image-container">
                  <img
                    src={getFileUrl(job.result_file)}
                    alt={`${job.operation} result`}
                    className="result-image"
                  />
                </div>
              ) : resultError ? (
                <div className="auth-error">{resultError}</div>
              ) : (
                renderCsvResult()
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
        <Link to="/jobs" className="btn-secondary">
          Back to Jobs
        </Link>
        <Link to="/create-job" className="btn-secondary">
          Create Another Job
        </Link>
      </div>
    </div>
  );
}
