import { useState, useRef } from 'react';
import { SpellForm, SpellFormData } from '../../components/spells';
import YAMLPreview from '../../components/spells/YAMLPreview';
import NotesButton from '../../components/collaboration/NotesButton';
import './designer-page.css';
import './weapons-designer.css';

export default function SpellsDesigner() {
  const [spellConfig, setSpellConfig] = useState<SpellFormData>({
    name: '',
    short_desc: '',
    long_desc: '',
    effect_styles: [],
    category: '',
    school: '',
  });

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFormChange = (data: SpellFormData) => {
    setSpellConfig(data);
  };

  const handleSave = () => {
    const dataStr = JSON.stringify(spellConfig, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${spellConfig.name || 'spell'}_config.json`;
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
        setSpellConfig(loadedConfig);
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
            <h1 className="page-title">✨ Spells Designer</h1>
            <p className="page-subtitle">Create and manage spell configurations</p>
          </div>
          <div className="weapon-actions">
            <NotesButton designerType="spells" />
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
            <SpellForm initialData={spellConfig} onChange={handleFormChange} />
          </div>
          <div className="weapons-designer-preview-section">
            <YAMLPreview spellConfig={spellConfig} />
          </div>
        </div>
      </div>
    </div>
  );
}

