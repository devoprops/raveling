import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './hooks/useAuth';
import ProtectedRoute from './components/auth/ProtectedRoute';
import DesignerLayout from './components/layout/DesignerLayout';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';
import GameplayPage from './pages/GameplayPage';
import DesignerSuite from './pages/designer/DesignerSuite';
import SkillsDesigner from './pages/designer/SkillsDesigner';
import SpellsDesigner from './pages/designer/SpellsDesigner';
import ZonesDesigner from './pages/designer/ZonesDesigner';
import CharactersDesigner from './pages/designer/CharactersDesigner';
import WearablesDesigner from './pages/designer/WearablesDesigner';
import WeaponsDesigner from './pages/designer/WeaponsDesigner';
import ConsumablesDesigner from './pages/designer/ConsumablesDesigner';
import UserManagement from './pages/admin/UserManagement';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/gameplay" element={<GameplayPage />} />
          
          <Route
            path="/designer"
            element={
              <ProtectedRoute>
                <DesignerLayout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Navigate to="/designer/skills" replace />} />
            <Route path="skills/*" element={<SkillsDesigner />} />
            <Route path="spells/*" element={<SpellsDesigner />} />
            <Route path="zones/*" element={<ZonesDesigner />} />
            <Route path="characters/*" element={<CharactersDesigner />} />
            <Route path="wearables/*" element={<WearablesDesigner />} />
            <Route path="weapons/*" element={<WeaponsDesigner />} />
            <Route path="consumables/*" element={<ConsumablesDesigner />} />
          </Route>
          
          <Route
            path="/admin/users"
            element={
              <ProtectedRoute>
                <UserManagement />
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;

