import type { Resource } from '../types/resource';

interface ResourceCardProps {
  resource: Resource;
}

export default function ResourceCard({ resource }: ResourceCardProps) {
  const isActive = resource.status === 'ACTIVE';

  return (
    <div className={`card resource-card ${isActive ? 'resource-active' : 'resource-disabled'}`}>
      <div className="resource-card-header">
        <h3>{resource.name}</h3>
        <span className={`status-badge ${isActive ? 'status-active' : 'status-disabled'}`}>
          {resource.status}
        </span>
      </div>
      <p className="resource-type">{resource.resource_type.replace('_', ' ')}</p>
      {resource.description && <p className="resource-desc">{resource.description}</p>}
      <p className="resource-capacity">Capacity: {resource.capacity}</p>
    </div>
  );
}
