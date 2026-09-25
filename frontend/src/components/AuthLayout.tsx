import type { ReactNode } from 'react';

interface AuthLayoutProps {
  title: string;
  children: ReactNode;
}

export default function AuthLayout({ title, children }: AuthLayoutProps) {
  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2>{title}</h2>
        {children}
      </div>
    </div>
  );
}
