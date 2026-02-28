import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import apiClient from '@/api/client';

export default function AuthSuccess() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserAndRedirect = async () => {
      const token = params.get('access_token');

      if (!token) {
        navigate('/login');
        return;
      }

      localStorage.setItem('token', token);

      try {
        const response = await apiClient.get('/auth/users/me/');
        const user = response.data;
        if (user) {
          localStorage.setItem('user', JSON.sçtringify(user));
        }
      } catch (err) {
        console.error('Failed to fetch user data:', err);
      }

      navigate('/');
    };

    fetchUserAndRedirect();
  }, [params, navigate]);

  return <div>Авторизация...</div>;
}
