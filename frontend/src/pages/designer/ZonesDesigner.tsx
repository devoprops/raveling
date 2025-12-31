import NotesButton from '../../components/collaboration/NotesButton';
import './designer-page.css';

export default function ZonesDesigner() {
  return (
    <div className="designer-page">
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div>
            <h1 className="page-title">🗺️ Zones Designer</h1>
            <p className="page-subtitle">Create and manage zone configurations</p>
          </div>
          <NotesButton designerType="zones" />
        </div>
      </div>
      <div className="page-content">
        <p>Zones designer interface coming soon...</p>
      </div>
    </div>
  );
}

