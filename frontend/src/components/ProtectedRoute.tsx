import { Navigate, Outlet } from 'react-router-dom';

export default function ProtectedRoute() {
  // Check if the user has an access token in localStorage
  const token = localStorage.getItem('access_token');

  // If no token is found, redirect them to the login page
  if (!token) {
    return <Navigate to="/login" replace />;
  }

  // If they have a token, render the child routes (Outlet)
  return <Outlet />;
}
