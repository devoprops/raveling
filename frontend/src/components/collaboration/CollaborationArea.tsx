import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useUserColor } from '../../hooks/useUserColor';
import { useAuth } from '../../hooks/useAuth';
import './CollaborationArea.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const DESIGNER_TABS = [
  { id: 'weapons', label: 'Weapons' },
  { id: 'skills', label: 'Skills' },
  { id: 'spells', label: 'Spells' },
  { id: 'wearables', label: 'Wearables' },
  { id: 'consumables', label: 'Consumables' },
  { id: 'characters', label: 'Characters' },
  { id: 'zones', label: 'Zones' },
  { id: 'general', label: 'General' },
  { id: 'quick_notes', label: 'Quick Notes' },
];

interface CollaborationAreaProps {
  initialTab?: string;
  onClose?: () => void;
}

export default function CollaborationArea({ initialTab, onClose }: CollaborationAreaProps) {
  const { user } = useAuth();
  const { userColor, updateUserColor } = useUserColor();
  const [activeTab, setActiveTab] = useState<string>(initialTab || 'weapons');
  const [notes, setNotes] = useState<Record<string, string>>({});
  const [lastUpdated, setLastUpdated] = useState<Record<string, { username: string; time: string }>>({});
  const [saving, setSaving] = useState<Record<string, boolean>>({});
  const [showColorPicker, setShowColorPicker] = useState(false);
  const [tempColor, setTempColor] = useState(userColor);
  const saveTimeoutRef = useRef<Record<string, NodeJS.Timeout>>({});

  useEffect(() => {
    // Load all notes on mount
    DESIGNER_TABS.forEach((tab) => {
      loadNote(tab.id);
    });
  }, []);

  const loadNote = async (designerType: string) => {
    try {
      const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/collaboration/notes/${designerType}`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      const note = response.data;
      setNotes((prev) => ({ ...prev, [designerType]: note.content || '' }));
      
      if (note.updated_by_username) {
        setLastUpdated((prev) => ({
          ...prev,
          [designerType]: {
            username: note.updated_by_username,
            time: note.updated_at ? new Date(note.updated_at).toLocaleString() : '',
          },
        }));
      }
    } catch (error) {
      console.error(`Failed to load note for ${designerType}:`, error);
    }
  };

  const saveNote = async (designerType: string, content: string) => {
    // Clear existing timeout
    if (saveTimeoutRef.current[designerType]) {
      clearTimeout(saveTimeoutRef.current[designerType]);
    }

    // Set saving state
    setSaving((prev) => ({ ...prev, [designerType]: true }));

    // Debounce save
    saveTimeoutRef.current[designerType] = setTimeout(async () => {
      try {
        const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
        await axios.post(
          `${API_URL}/api/collaboration/notes/${designerType}`,
          { content },
          { headers: { Authorization: `Bearer ${token}` } }
        );

        setLastUpdated((prev) => ({
          ...prev,
          [designerType]: {
            username: user?.username || 'Unknown',
            time: new Date().toLocaleString(),
          },
        }));
      } catch (error) {
        console.error(`Failed to save note for ${designerType}:`, error);
        alert('Failed to save note. Please try again.');
      } finally {
        setSaving((prev) => ({ ...prev, [designerType]: false }));
      }
    }, 500);
  };

  const handleContentChange = (designerType: string, value: string) => {
    setNotes((prev) => ({ ...prev, [designerType]: value }));
    saveNote(designerType, value);
  };

  const handleColorChange = async () => {
    try {
      await updateUserColor(tempColor);
      setShowColorPicker(false);
    } catch (error) {
      alert('Failed to update color. Please try again.');
    }
  };

  const isQuickNotes = activeTab === 'quick_notes';

  return (
    <div className={`collaboration-area ${!onClose ? 'standalone' : ''}`}>
      <div className="collaboration-header">
        <h2>Collaboration Notes</h2>
        <div className="header-actions">
          <div className="color-picker-container">
            <button
              className="color-picker-btn"
              onClick={() => setShowColorPicker(!showColorPicker)}
              style={{ backgroundColor: userColor }}
              title="Change your text color"
            >
              <span className="color-indicator" style={{ backgroundColor: userColor }}></span>
              Your Color
            </button>
            {showColorPicker && (
              <div className="color-picker-popup">
                <input
                  type="color"
                  value={tempColor}
                  onChange={(e) => setTempColor(e.target.value)}
                />
                <div className="color-picker-actions">
                  <button onClick={handleColorChange}>Apply</button>
                  <button onClick={() => {
                    setTempColor(userColor);
                    setShowColorPicker(false);
                  }}>Cancel</button>
                </div>
              </div>
            )}
          </div>
          {onClose && (
            <button className="close-btn" onClick={onClose}>
              ✕
            </button>
          )}
        </div>
      </div>

      <div className="collaboration-tabs">
        {DESIGNER_TABS.map((tab) => (
          <button
            key={tab.id}
            className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
            {saving[tab.id] && <span className="saving-indicator">●</span>}
          </button>
        ))}
      </div>

      <div className="collaboration-content">
        {lastUpdated[activeTab] && (
          <div className="last-updated">
            Last updated by <span style={{ color: userColor }}>{lastUpdated[activeTab].username}</span> at {lastUpdated[activeTab].time}
          </div>
        )}
        <textarea
          className={`note-textarea ${isQuickNotes ? 'quick-notes' : ''}`}
          value={notes[activeTab] || ''}
          onChange={(e) => handleContentChange(activeTab, e.target.value)}
          onBlur={() => {
            // Force immediate save on blur
            if (saveTimeoutRef.current[activeTab]) {
              clearTimeout(saveTimeoutRef.current[activeTab]);
            }
            saveNote(activeTab, notes[activeTab] || '');
          }}
          placeholder={`Type your notes here... ${isQuickNotes ? '(Quick notes - compact format)' : ''}`}
          style={{ color: userColor }}
        />
      </div>
    </div>
  );
}

