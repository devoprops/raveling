import { useAuth } from '../hooks/useAuth';
import LoginForm from '../components/auth/LoginForm';

export default function HomePage() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        color: '#c4c4c4'
      }}>
        Loading...
      </div>
    );
  }

  if (user) {
    // Redirect to designer if already logged in
    window.location.href = '/designer';
    return null;
  }

  return <LoginForm />;
}

