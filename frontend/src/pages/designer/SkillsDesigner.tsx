import NotesButton from '../../components/collaboration/NotesButton';
import './designer-page.css';

export default function SkillsDesigner() {
  return (
    <div className="designer-page">
      <div className="page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
          <div>
            <h1 className="page-title">⚔️ Skills Designer</h1>
            <p className="page-subtitle">Create and manage skill configurations</p>
          </div>
          <NotesButton designerType="skills" />
        </div>
      </div>
      <div className="page-content">
        <p>Skills designer interface coming soon...</p>
      </div>
    </div>
  );
}

