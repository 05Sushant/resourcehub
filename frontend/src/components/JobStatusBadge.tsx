interface JobStatusBadgeProps {
  status: string;
}

export default function JobStatusBadge({ status }: JobStatusBadgeProps) {
  const statusClass = `status-badge status-${status.toLowerCase()}`;

  const labels: Record<string, string> = {
    PENDING: 'Queued',
    RUNNING: 'Processing',
    COMPLETED: 'Completed',
    FAILED: 'Failed',
  };

  return <span className={statusClass}>{labels[status] || status}</span>;
}
