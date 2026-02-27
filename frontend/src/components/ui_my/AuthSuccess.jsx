import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';

export default function AuthSuccess() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  useEffect(() => {
    const token = params.get('access_token');

    if (!token) {
      navigate('/login');
      return;
    }

    localStorage.setItem('token', token);
    localStorage.setItem('oauthLogin', 'true');
    navigate('/');
  }, []);

  return <div>Авторизация...</div>;
}
