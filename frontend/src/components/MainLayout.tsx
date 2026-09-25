import { Link, useNavigate, Outlet } from 'react-router-dom';
import { logout } from '../services/auth';

export default function MainLayout() {
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="main-layout">
      <header className="main-header">
        <div className="brand">ResourceHub</div>
        <nav className="main-nav">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/jobs">My Jobs</Link>
          <Link to="/create-job">Create Job</Link>
          <button onClick={handleLogout} className="btn-logout">Logout</button>
        </nav>
      </header>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
