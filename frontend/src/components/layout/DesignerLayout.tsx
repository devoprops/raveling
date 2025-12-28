import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import './DesignerLayout.css';

export default function DesignerLayout() {
  return (
    <div className="designer-layout">
      <Header />
      <div className="designer-content">
        <Sidebar />
        <main className="designer-main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

