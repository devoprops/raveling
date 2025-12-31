import { useState } from 'react';
import CollaborationArea from './CollaborationArea';
import './NotesButton.css';

interface NotesButtonProps {
  designerType: string;
}

export default function NotesButton({ designerType }: NotesButtonProps) {
  const [showNotes, setShowNotes] = useState(false);

  return (
    <>
      <button className="notes-btn" onClick={() => setShowNotes(true)} title="Open collaboration notes">
        📝 Notes
      </button>
      {showNotes && (
        <div className="notes-overlay">
          <div className="notes-modal">
            <CollaborationArea initialTab={designerType} onClose={() => setShowNotes(false)} />
          </div>
        </div>
      )}
    </>
  );
}

