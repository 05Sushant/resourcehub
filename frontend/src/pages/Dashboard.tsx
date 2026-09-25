import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import type { Resource } from '../types/resource';
import { getResources } from '../services/resourceService';
import ResourceCard from '../components/ResourceCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

export default function Dashboard() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchResources = async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await getResources();
      setResources(data);
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
        const data = await getResources();
        if (!ignore) setResources(data);
      } catch {
        if (!ignore) setError('Unable to connect to the server.');
      } finally {
        if (!ignore) setIsLoading(false);
      }
    }
    load();
    return () => { ignore = true; };
  }, []);

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Manage your resources and processing jobs.</p>
      </div>

      <div className="dashboard-actions">
        <Link to="/create-job" className="btn-primary">Create New Job</Link>
        <Link to="/jobs" className="btn-secondary">View My Jobs</Link>
      </div>

      <div className="section">
        <h2>Available Resources</h2>
        {isLoading && <LoadingSpinner message="Loading resources..." />}
        {error && <ErrorMessage message={error} onRetry={fetchResources} />}
        {!isLoading && !error && resources.length === 0 && (
          <p className="empty-state">No resources available.</p>
        )}
        {!isLoading && !error && resources.length > 0 && (
          <div className="dashboard-cards">
            {resources.map((resource) => (
              <ResourceCard key={resource.id} resource={resource} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
