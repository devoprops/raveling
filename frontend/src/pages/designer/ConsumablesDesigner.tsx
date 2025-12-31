import NotesButton from '../../components/collaboration/NotesButton';
import './designer-page.css';

export default function ConsumablesDesigner() {
  return (
    <div className="designer-page">
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div>
            <h1 className="page-title">🧪 Consumables Designer</h1>
            <p className="page-subtitle">Create and manage consumable item configurations</p>
          </div>
          <NotesButton designerType="consumables" />
        </div>
      </div>
      <div className="page-content">
        <p>Consumables designer interface coming soon...</p>
      </div>
    </div>
  );
}

