import { useMemo } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import yaml from 'yaml';
import './YAMLPreview.css';

interface YAMLPreviewProps {
  weaponConfig: any;
}

export default function YAMLPreview({ weaponConfig }: YAMLPreviewProps) {
  const yamlString = useMemo(() => {
    try {
      // Convert weapon config to YAML format
      const yamlConfig: any = {
        name: weaponConfig.name || '',
        short_desc: weaponConfig.short_desc || '',
        long_desc: weaponConfig.long_desc || '',
        item_type: 'weapon',
        weight_kg: weaponConfig.weight_kg || 0,
        length_cm: weaponConfig.length_cm || 0,
        width_cm: weaponConfig.width_cm || 0,
        material: weaponConfig.material || '',
      };

      // Add effectors
      if (weaponConfig.effectors && weaponConfig.effectors.length > 0) {
        yamlConfig.effectors = weaponConfig.effectors.map((effector: any) => {
          const effectorConfig: any = {
            effector_type: effector.effector_type,
            effector_name: effector.effector_name,
          };

          // Add effector-specific fields
          if (effector.damage_subtype) effectorConfig.damage_subtype = effector.damage_subtype;
          if (effector.element_type) effectorConfig.element_type = effector.element_type;
          if (effector.base_damage !== undefined) effectorConfig.base_damage = effector.base_damage;
          if (effector.base_restoration !== undefined) effectorConfig.base_restoration = effector.base_restoration;
          if (effector.base_buff !== undefined) effectorConfig.base_buff = effector.base_buff;
          if (effector.base_debuff !== undefined) effectorConfig.base_debuff = effector.base_debuff;
          if (effector.duration !== undefined) effectorConfig.duration = effector.duration;
          if (effector.stackable !== undefined) effectorConfig.stackable = effector.stackable;
          if (effector.attribute_type) effectorConfig.attribute_type = effector.attribute_type;
          if (effector.affected_attributes) effectorConfig.affected_attributes = effector.affected_attributes;
          if (effector.execution_probability !== undefined && effector.execution_probability !== 1.0) {
            effectorConfig.execution_probability = effector.execution_probability;
          }

          // Add distribution parameters
          if (effector.distribution_parameters) {
            effectorConfig.distribution_parameters = effector.distribution_parameters;
          }

          // Add process config
          if (effector.process_config) {
            effectorConfig.process_config = effector.process_config;
          }

          return effectorConfig;
        });
      }

      // Add affinities
      if (weaponConfig.affinities) {
        yamlConfig.affinities = {
          elemental: weaponConfig.affinities.elemental || {},
          race: weaponConfig.affinities.race || {},
        };
      }

      // Add detriments
      if (weaponConfig.detriments) {
        yamlConfig.detriments = {
          elemental: weaponConfig.detriments.elemental || {},
          race: weaponConfig.detriments.race || {},
        };
      }

      // Add auxiliary slots
      if (weaponConfig.auxiliary_slots !== undefined) {
        yamlConfig.auxiliary_slots = weaponConfig.auxiliary_slots;
      }

      // Add size constraints
      if (weaponConfig.size_constraints) {
        yamlConfig.size_constraints = weaponConfig.size_constraints;
      }

      // Add thumbnail path
      if (weaponConfig.thumbnail_path) {
        yamlConfig.thumbnail_path = weaponConfig.thumbnail_path;
      }

      // Add restrictions if any
      if (weaponConfig.restrictions && Object.keys(weaponConfig.restrictions).length > 0) {
        yamlConfig.restrictions = weaponConfig.restrictions;
      }

      return yaml.stringify(yamlConfig, { indent: 2 });
    } catch (error) {
      return `Error generating YAML: ${error}`;
    }
  }, [weaponConfig]);

  return (
    <div className="yaml-preview">
      <div className="yaml-preview-header">
        <h3 className="yaml-preview-title">YAML Preview</h3>
      </div>
      <div className="yaml-preview-content">
        <SyntaxHighlighter
          language="yaml"
          style={vscDarkPlus}
          customStyle={{
            margin: 0,
            borderRadius: '4px',
            background: 'rgba(0, 0, 0, 0.4)',
          }}
        >
          {yamlString}
        </SyntaxHighlighter>
      </div>
    </div>
  );
}

