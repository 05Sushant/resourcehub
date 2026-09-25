import { useState, useEffect } from 'react';
import type { FormEvent, ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { isAxiosError } from 'axios';
import type { Resource } from '../types/resource';
import { getResources } from '../services/resourceService';
import { createJob } from '../services/jobService';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

// Only expose operations that have actual backend processor implementations
const OPERATION_MAP: Record<string, { operation: string; label: string }> = {
  CSV_ANALYTICS: { operation: 'PROFILE', label: 'CSV Profile Analysis' },
  IMAGE_PROCESSING: { operation: 'RESIZE', label: 'Image Resize' },
};

export default function CreateJob() {
  const navigate = useNavigate();

  // Resource loading state
  const [resources, setResources] = useState<Resource[]>([]);
  const [isLoadingResources, setIsLoadingResources] = useState(true);
  const [resourceError, setResourceError] = useState('');

  // Form state
  const [selectedResourceId, setSelectedResourceId] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [width, setWidth] = useState('');
  const [height, setHeight] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const fetchResources = async () => {
    setIsLoadingResources(true);
    setResourceError('');
    try {
      const data = await getResources();
      setResources(data);
    } catch {
      setResourceError('Unable to connect to the server.');
    } finally {
      setIsLoadingResources(false);
    }
  };

  useEffect(() => {
    let ignore = false;
    async function load() {
      try {
        const data = await getResources();
        if (!ignore) setResources(data);
      } catch {
        if (!ignore) setResourceError('Unable to connect to the server.');
      } finally {
        if (!ignore) setIsLoadingResources(false);
      }
    }
    load();
    return () => { ignore = true; };
  }, []);

  // Derived state from selection
  const selectedResource = resources.find((r) => r.id === Number(selectedResourceId));
  const operationInfo = selectedResource ? OPERATION_MAP[selectedResource.resource_type] : null;
  const isResize = operationInfo?.operation === 'RESIZE';

  // Only ACTIVE resources can be selected
  const activeResources = resources.filter((r) => r.status === 'ACTIVE');

  const getAcceptedFileTypes = (): string => {
    if (isResize) return '.png,.jpg,.jpeg';
    return '.csv';
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    setSelectedFile(e.target.files?.[0] || null);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitError('');

    if (!selectedResource || !operationInfo || !selectedFile) return;

    // Validate RESIZE parameters
    if (isResize) {
      const w = Number(width);
      const h = Number(height);
      if (!Number.isInteger(w) || !Number.isInteger(h) || w <= 0 || h <= 0) {
        setSubmitError('Width and height must be positive integers.');
        return;
      }
    }

    setIsSubmitting(true);

    const formData = new FormData();
    formData.append('resource', String(selectedResource.id));
    formData.append('operation', operationInfo.operation);
    formData.append('input_file', selectedFile);

    if (isResize) {
      formData.append(
        'parameters',
        JSON.stringify({ width: Number(width), height: Number(height) })
      );
    } else {
      formData.append('parameters', '{}');
    }

    try {
      const job = await createJob(formData);
      navigate(`/jobs/${job.id}`);
    } catch (err) {
      if (isAxiosError(err) && err.response) {
        const data = err.response.data;
        if (data?.detail) {
          setSubmitError(data.detail);
        } else if (typeof data === 'object') {
          const firstKey = Object.keys(data)[0];
          if (firstKey) {
            const val = data[firstKey];
            const msg = Array.isArray(val) ? val[0] : String(val);
            setSubmitError(`${firstKey}: ${msg}`);
          } else {
            setSubmitError('Failed to submit job for processing.');
          }
        } else {
          setSubmitError('Failed to submit job for processing.');
        }
      } else {
        setSubmitError('Unable to connect to the server.');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoadingResources) {
    return <LoadingSpinner message="Loading resources..." />;
  }

  if (resourceError) {
    return <ErrorMessage message={resourceError} onRetry={fetchResources} />;
  }

  return (
    <div className="create-job-page">
      <h1>Create Job</h1>

      <form className="create-job-form" onSubmit={handleSubmit}>
        {submitError && <div className="auth-error">{submitError}</div>}

        {/* Step 1: Select Resource */}
        <div className="form-group">
          <label htmlFor="resource">Select Resource</label>
          <select
            id="resource"
            value={selectedResourceId}
            onChange={(e) => {
              setSelectedResourceId(e.target.value);
              setSelectedFile(null);
              setWidth('');
              setHeight('');
            }}
            required
            disabled={isSubmitting}
          >
            <option value="">-- Choose a resource --</option>
            {activeResources.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name} ({r.resource_type.replace('_', ' ')})
              </option>
            ))}
          </select>
          {activeResources.length === 0 && (
            <p className="form-hint">No active resources available.</p>
          )}
        </div>

        {/* Step 2: Show Operation */}
        {operationInfo && (
          <>
            <div className="form-group">
              <label>Operation</label>
              <div className="operation-display">{operationInfo.label}</div>
            </div>

            {/* Step 3: File Upload */}
            <div className="form-group">
              <label htmlFor="input_file">
                {isResize ? 'Image File' : 'CSV File'}
              </label>
              <input
                id="input_file"
                type="file"
                accept={getAcceptedFileTypes()}
                onChange={handleFileChange}
                required
                disabled={isSubmitting}
              />
              {selectedFile && (
                <p className="form-hint">Selected: {selectedFile.name}</p>
              )}
            </div>

            {/* Step 4: Parameters for RESIZE */}
            {isResize && (
              <>
                <div className="form-group">
                  <label htmlFor="width">Width (px)</label>
                  <input
                    id="width"
                    type="number"
                    min="1"
                    step="1"
                    value={width}
                    onChange={(e) => setWidth(e.target.value)}
                    placeholder="e.g. 800"
                    required
                    disabled={isSubmitting}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="height">Height (px)</label>
                  <input
                    id="height"
                    type="number"
                    min="1"
                    step="1"
                    value={height}
                    onChange={(e) => setHeight(e.target.value)}
                    placeholder="e.g. 600"
                    required
                    disabled={isSubmitting}
                  />
                </div>
              </>
            )}

            {/* Step 5: Submit */}
            <button type="submit" className="btn-primary" disabled={isSubmitting}>
              {isSubmitting ? 'Submitting job...' : 'Submit Job'}
            </button>
          </>
        )}
      </form>
    </div>
  );
}
