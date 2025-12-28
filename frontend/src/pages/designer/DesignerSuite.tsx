import { Navigate } from 'react-router-dom';

export default function DesignerSuite() {
  // Redirect to skills designer by default
  return <Navigate to="/designer/skills" replace />;
}

