import { useState, useEffect } from 'react';
import type { FormEvent, ChangeEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { isAxiosError } from 'axios';
import type { Resource } from '../types/resource';
import { getResources } from '../services/resourceService';
import { createJob } from '../services/jobService';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

type OperationInfo = {
  operation: string;
  label: string;
  input: 'csv' | 'image';
};

const OPERATIONS_BY_RESOURCE: Record<string, OperationInfo[]> = {
  CSV_ANALYTICS: [
    { operation: 'PROFILE', label: 'Profile CSV', input: 'csv' },
    { operation: 'ANALYZE', label: 'Analyze CSV', input: 'csv' },
    { operation: 'VALIDATE', label: 'Validate CSV', input: 'csv' },
  ],
  IMAGE_PROCESSING: [
    { operation: 'RESIZE', label: 'Resize Image', input: 'image' },
    { operation: 'GRAYSCALE', label: 'Convert to Grayscale', input: 'image' },
  ],
};

type ValidationColumn = {
  name: string;
  type: 'string' | 'integer' | 'float';
};

export default function CreateJob() {
  const navigate = useNavigate();

  const [resources, setResources] = useState<Resource[]>([]);
  const [isLoadingResources, setIsLoadingResources] = useState(true);
  const [resourceError, setResourceError] = useState('');

  const [selectedResourceId, setSelectedResourceId] = useState('');
  const [selectedOperation, setSelectedOperation] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const [width, setWidth] = useState('');
  const [height, setHeight] = useState('');
  const [validationColumns, setValidationColumns] = useState<ValidationColumn[]>([
    { name: '', type: 'string' },
  ]);

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
    return () => {
      ignore = true;
    };
  }, []);

  const selectedResource = resources.find(
    (resource) => resource.id === Number(selectedResourceId),
  );

  const availableOperations = selectedResource
    ? OPERATIONS_BY_RESOURCE[selectedResource.resource_type] ?? []
    : [];

  const operationInfo = availableOperations.find(
    (operation) => operation.operation === selectedOperation,
  );

  const isResize = selectedOperation === 'RESIZE';
  const isValidate = selectedOperation === 'VALIDATE';
  const isImageOperation = operationInfo?.input === 'image';

  const activeResources = resources.filter(
    (resource) => resource.status === 'ACTIVE',
  );

  const resetOperationState = () => {
    setSelectedOperation('');
    setSelectedFile(null);
    setWidth('');
    setHeight('');
    setValidationColumns([{ name: '', type: 'string' }]);
    setSubmitError('');
  };

  const handleResourceChange = (value: string) => {
    setSelectedResourceId(value);
    resetOperationState();
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    setSelectedFile(event.target.files?.[0] ?? null);
  };

  const updateValidationColumn = (
    index: number,
    field: keyof ValidationColumn,
    value: string,
  ) => {
    setValidationColumns((current) =>
      current.map((column, columnIndex) =>
        columnIndex === index
          ? { ...column, [field]: value }
          : column,
      ),
    );
  };

  const addValidationColumn = () => {
    setValidationColumns((current) => [
      ...current,
      { name: '', type: 'string' },
    ]);
  };

  const removeValidationColumn = (index: number) => {
    setValidationColumns((current) =>
      current.length === 1
        ? current
        : current.filter((_, columnIndex) => columnIndex !== index),
    );
  };

  const buildParameters = (): Record<string, unknown> | null => {
    if (isResize) {
      const parsedWidth = Number(width);
      const parsedHeight = Number(height);

      if (
        !Number.isInteger(parsedWidth) ||
        !Number.isInteger(parsedHeight) ||
        parsedWidth <= 0 ||
        parsedHeight <= 0
      ) {
        setSubmitError('Width and height must be positive integers.');
        return null;
      }

      return {
        width: parsedWidth,
        height: parsedHeight,
      };
    }

    if (isValidate) {
      const columns: Record<string, string> = {};

      for (const column of validationColumns) {
        const name = column.name.trim();

        if (!name) {
          setSubmitError('Every validation column must have a name.');
          return null;
        }

        if (columns[name]) {
          setSubmitError(`Duplicate validation column: ${name}`);
          return null;
        }

        columns[name] = column.type;
      }

      return { columns };
    }

    return {};
  };

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    setSubmitError('');

    if (!selectedResource || !operationInfo || !selectedFile) {
      setSubmitError('Please select a resource, operation, and input file.');
      return;
    }

    const parameters = buildParameters();

    if (!parameters) return;

    setIsSubmitting(true);

    const formData = new FormData();
    formData.append('resource', String(selectedResource.id));
    formData.append('operation', operationInfo.operation);
    formData.append('input_file', selectedFile);
    formData.append('parameters', JSON.stringify(parameters));

    try {
      const job = await createJob(formData);
      navigate(`/jobs/${job.id}`);
    } catch (error) {
      if (isAxiosError(error) && error.response) {
        const data = error.response.data;

        if (data?.detail) {
          setSubmitError(data.detail);
        } else if (typeof data === 'object') {
          const firstKey = Object.keys(data)[0];

          if (firstKey) {
            const value = data[firstKey];
            const message = Array.isArray(value) ? value[0] : String(value);
            setSubmitError(`${firstKey}: ${message}`);
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

        <div className="form-group">
          <label htmlFor="resource">Select Resource</label>
          <select
            id="resource"
            value={selectedResourceId}
            onChange={(event) => handleResourceChange(event.target.value)}
            required
            disabled={isSubmitting}
          >
            <option value="">-- Choose a resource --</option>
            {activeResources.map((resource) => (
              <option key={resource.id} value={resource.id}>
                {resource.name} ({resource.resource_type.replace('_', ' ')})
              </option>
            ))}
          </select>

          {activeResources.length === 0 && (
            <p className="form-hint">No active resources available.</p>
          )}
        </div>

        {selectedResource && availableOperations.length > 0 && (
          <div className="form-group">
            <label htmlFor="operation">Operation</label>
            <select
              id="operation"
              value={selectedOperation}
              onChange={(event) => {
                setSelectedOperation(event.target.value);
                setSelectedFile(null);
                setWidth('');
                setHeight('');
                setValidationColumns([{ name: '', type: 'string' }]);
                setSubmitError('');
              }}
              required
              disabled={isSubmitting}
            >
              <option value="">-- Choose an operation --</option>
              {availableOperations.map((operation) => (
                <option key={operation.operation} value={operation.operation}>
                  {operation.label}
                </option>
              ))}
            </select>
          </div>
        )}

        {operationInfo && (
          <>
            <div className="form-group">
              <label htmlFor="input_file">
                {isImageOperation ? 'Image File' : 'CSV File'}
              </label>
              <input
                id="input_file"
                type="file"
                accept={isImageOperation ? '.png,.jpg,.jpeg' : '.csv'}
                onChange={handleFileChange}
                required
                disabled={isSubmitting}
              />
              {selectedFile && (
                <p className="form-hint">Selected: {selectedFile.name}</p>
              )}
            </div>

            {isResize && (
              <div className="form-group">
                <label>Resize Dimensions</label>
                <div className="form-row">
                  <input
                    id="width"
                    type="number"
                    min="1"
                    step="1"
                    value={width}
                    onChange={(event) => setWidth(event.target.value)}
                    placeholder="Width (px)"
                    required
                    disabled={isSubmitting}
                  />
                  <input
                    id="height"
                    type="number"
                    min="1"
                    step="1"
                    value={height}
                    onChange={(event) => setHeight(event.target.value)}
                    placeholder="Height (px)"
                    required
                    disabled={isSubmitting}
                  />
                </div>
              </div>
            )}

            {isValidate && (
              <div className="form-group">
                <label>Expected CSV Schema</label>

                {validationColumns.map((column, index) => (
                  <div className="form-row" key={index}>
                    <input
                      type="text"
                      value={column.name}
                      onChange={(event) =>
                        updateValidationColumn(index, 'name', event.target.value)
                      }
                      placeholder="Column name"
                      required
                      disabled={isSubmitting}
                    />

                    <select
                      value={column.type}
                      onChange={(event) =>
                        updateValidationColumn(index, 'type', event.target.value)
                      }
                      disabled={isSubmitting}
                    >
                      <option value="string">String</option>
                      <option value="integer">Integer</option>
                      <option value="float">Float</option>
                    </select>

                    <button
                      type="button"
                      className="btn-secondary"
                      onClick={() => removeValidationColumn(index)}
                      disabled={isSubmitting || validationColumns.length === 1}
                    >
                      Remove
                    </button>
                  </div>
                ))}

                <button
                  type="button"
                  className="btn-secondary"
                  onClick={addValidationColumn}
                  disabled={isSubmitting}
                >
                  + Add Column
                </button>

                <p className="form-hint">
                  Define the columns and expected data types for the uploaded CSV.
                </p>
              </div>
            )}

            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Submitting job...' : 'Submit Job'}
            </button>
          </>
        )}
      </form>
    </div>
  );
}
