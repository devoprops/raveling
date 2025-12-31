import { useState, useRef } from 'react';
import { WeaponForm, WeaponFormData } from '../../components/weapons';
import PreviewTabs from '../../components/weapons/PreviewTabs';
import NotesButton from '../../components/collaboration/NotesButton';
import { createDefaultAffinities, createDefaultDetriments } from '../../utils/constants';
import './designer-page.css';
import './weapons-designer.css';

export default function WeaponsDesigner() {
  const [weaponConfig, setWeaponConfig] = useState<WeaponFormData>({
    name: '',
    short_desc: '',
    long_desc: '',
    weight_kg: 0,
    length_cm: 0,
    width_cm: 0,
    material: '',
    effectors: [],
    affinities: createDefaultAffinities(),
    detriments: createDefaultDetriments(),
    auxiliary_slots: 0,
    size_constraints: [0, 100],
    thumbnail_path: '',
    restrictions: {},
  });

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFormChange = (data: WeaponFormData) => {
    setWeaponConfig(data);
  };

  const handleSave = () => {
    const dataStr = JSON.stringify(weaponConfig, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${weaponConfig.name || 'weapon'}_config.json`;
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
        setWeaponConfig(loadedConfig);
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
            <h1 className="page-title">⚔️ Weapons Designer</h1>
            <p className="page-subtitle">Create and manage weapon configurations</p>
          </div>
          <div className="weapon-actions">
            <NotesButton designerType="weapons" />
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
            <WeaponForm initialData={weaponConfig} onChange={handleFormChange} />
          </div>
          <div className="weapons-designer-preview-section">
            <PreviewTabs weaponConfig={weaponConfig} />
          </div>
        </div>
      </div>
    </div>
  );
}

