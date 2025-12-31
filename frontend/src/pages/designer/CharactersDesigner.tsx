import NotesButton from '../../components/collaboration/NotesButton';
import './designer-page.css';

export default function CharactersDesigner() {
  return (
    <div className="designer-page">
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div>
            <h1 className="page-title">👤 Characters Designer</h1>
            <p className="page-subtitle">Create and manage character configurations</p>
          </div>
          <NotesButton designerType="characters" />
        </div>
      </div>
      <div className="page-content">
        <p>Characters designer interface coming soon...</p>
      </div>
    </div>
  );
}

