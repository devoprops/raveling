import { useState } from 'react';
import { WeaponForm, YAMLPreview, AnalysisTools, WeaponFormData } from '../../components/weapons';
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
    affinities: {
      elemental: { Earth: 1.0, Water: 1.0, Air: 1.0, Fire: 1.0 },
      race: {},
    },
    detriments: {
      elemental: { Earth: 1.0, Water: 1.0, Air: 1.0, Fire: 1.0 },
      race: {},
    },
    auxiliary_slots: 0,
    size_constraints: null,
    thumbnail_path: '',
    restrictions: {},
  });

  const handleFormChange = (data: WeaponFormData) => {
    setWeaponConfig(data);
  };

  return (
    <div className="designer-page">
      <div className="page-header">
        <h1 className="page-title">⚔️ Weapons Designer</h1>
        <p className="page-subtitle">Create and manage weapon configurations</p>
      </div>
      <div className="weapons-designer-content">
        <div className="weapons-designer-main">
          <div className="weapons-designer-form-section">
            <WeaponForm initialData={weaponConfig} onChange={handleFormChange} />
          </div>
          <div className="weapons-designer-preview-section">
            <YAMLPreview weaponConfig={weaponConfig} />
            <AnalysisTools weaponConfig={weaponConfig} />
          </div>
        </div>
      </div>
    </div>
  );
}

