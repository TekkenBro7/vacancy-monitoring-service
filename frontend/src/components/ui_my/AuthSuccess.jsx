import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '@/utils/AuthContext';

export default function AuthSuccess() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const { checkAuth } = useAuth();

  useEffect(() => {
    const token = params.get('access_token');

    if (!token) {
      navigate('/login');
      return;
    }

    localStorage.setItem('token', token);

    checkAuth().then(() => {
      navigate('/');
    });
  }, []);

  return <div>Авторизация...</div>;
}
