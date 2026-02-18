import { Navigate } from 'react-router-dom';
import { useAuth } from '@/utils/AuthContext';

export default function ProtectedAdminRoute({ children }) {
  const { isAuthenticated, user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="h-12 w-12 border-4 border-[rgb(var(--accent))] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p style={{ color: 'rgb(var(--text-muted))' }}>Загрузка...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (user?.role_name !== 'admin') {
    return <Navigate to="/" replace />;
  }

  return children;
}
