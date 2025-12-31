import NotesButton from '../../components/collaboration/NotesButton';
import './designer-page.css';

export default function WearablesDesigner() {
  return (
    <div className="designer-page">
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div>
            <h1 className="page-title">🛡️ Wearables Designer</h1>
            <p className="page-subtitle">Create and manage wearable item configurations</p>
          </div>
          <NotesButton designerType="wearables" />
        </div>
      </div>
      <div className="page-content">
        <p>Wearables designer interface coming soon...</p>
      </div>
    </div>
  );
}

