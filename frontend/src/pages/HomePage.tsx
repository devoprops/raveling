import { useAuth } from '../hooks/useAuth';
import LoginForm from '../components/auth/LoginForm';

export default function HomePage() {
  const { user } = useAuth();

  if (user) {
    // Redirect to designer if already logged in
    window.location.href = '/designer';
    return null;
  }

  return <LoginForm />;
}

