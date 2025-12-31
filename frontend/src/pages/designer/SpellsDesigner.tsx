import NotesButton from '../../components/collaboration/NotesButton';
import './designer-page.css';

export default function SpellsDesigner() {
  return (
    <div className="designer-page">
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div>
            <h1 className="page-title">✨ Spells Designer</h1>
            <p className="page-subtitle">Create and manage spell configurations</p>
          </div>
          <NotesButton designerType="spells" />
        </div>
      </div>
      <div className="page-content">
        <p>Spells designer interface coming soon...</p>
      </div>
    </div>
  );
}

