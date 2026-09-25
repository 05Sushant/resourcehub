import { Link } from 'react-router-dom';

export default function Dashboard() {
  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Welcome back!</h1>
        <p>Here is an overview of your resources and jobs.</p>
      </div>

      <div className="dashboard-cards">
        <div className="card">
          <h3>Available Resources</h3>
          <p className="card-value">-- <span>(Placeholder)</span></p>
        </div>
        <div className="card">
          <h3>Active Jobs</h3>
          <p className="card-value">-- <span>(Placeholder)</span></p>
        </div>
        <div className="card">
          <h3>Completed Jobs</h3>
          <p className="card-value">-- <span>(Placeholder)</span></p>
        </div>
      </div>

      <div className="dashboard-actions">
        <Link to="/create-job" className="btn-primary">Create New Job</Link>
        <Link to="/jobs" className="btn-secondary">View My Jobs</Link>
      </div>
    </div>
  );
}
