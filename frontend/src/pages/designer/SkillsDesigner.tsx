import { useState, useRef } from 'react';
import { SkillForm, SkillFormData } from '../../components/skills';
import YAMLPreview from '../../components/skills/YAMLPreview';
import NotesButton from '../../components/collaboration/NotesButton';
import './designer-page.css';
import './weapons-designer.css';

export default function SkillsDesigner() {
  const [skillConfig, setSkillConfig] = useState<SkillFormData>({
    name: '',
    short_desc: '',
    long_desc: '',
    effect_styles: [],
    category: '',
  });

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFormChange = (data: SkillFormData) => {
    setSkillConfig(data);
  };

  const handleSave = () => {
    const dataStr = JSON.stringify(skillConfig, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${skillConfig.name || 'skill'}_config.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handleLoad = () => {
    fileInputRef.current?.click();
  };

  const handleFileLoad = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const loadedConfig = JSON.parse(e.target?.result as string);
        setSkillConfig(loadedConfig);
      } catch (error) {
        alert('Failed to load config file. Please check the file format.');
      }
    };
    reader.readAsText(file);
    
    // Reset input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="designer-page">
      <div className="page-header">
        <div className="weapons-designer-header">
          <div>
            <h1 className="page-title">⚔️ Skills Designer</h1>
            <p className="page-subtitle">Create and manage skill configurations</p>
          </div>
          <div className="weapon-actions">
            <NotesButton designerType="skills" />
            <button onClick={handleSave} className="save-btn">
              Save
            </button>
            <button onClick={handleLoad} className="load-btn">
              Load
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept=".json"
              onChange={handleFileLoad}
              style={{ display: 'none' }}
            />
          </div>
        </div>
      </div>
      <div className="weapons-designer-content">
        <div className="weapons-designer-main">
          <div className="weapons-designer-form-section">
            <SkillForm initialData={skillConfig} onChange={handleFormChange} />
          </div>
          <div className="weapons-designer-preview-section">
            <YAMLPreview skillConfig={skillConfig} />
          </div>
        </div>
      </div>
    </div>
  );
}

