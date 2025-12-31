import { useMemo } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import yaml from 'yaml';
import { SkillFormData } from './SkillForm';
import './YAMLPreview.css';

interface YAMLPreviewProps {
  skillConfig: SkillFormData;
}

export default function YAMLPreview({ skillConfig }: YAMLPreviewProps) {
  const yamlString = useMemo(() => {
    try {
      // Convert skill config to YAML format
      const yamlConfig: any = {
        name: skillConfig.name || '',
        short_desc: skillConfig.short_desc || '',
        long_desc: skillConfig.long_desc || '',
        item_type: 'skill',
      };

      // Add category if provided
      if (skillConfig.category) {
        yamlConfig.category = skillConfig.category;
      }

      // Add effect styles
      if (skillConfig.effect_styles && skillConfig.effect_styles.length > 0) {
        yamlConfig.effect_styles = skillConfig.effect_styles.map((style: any) => {
          const styleConfig: any = {
            name: style.name,
            style_type: style.style_type,
            subtype: style.subtype,
            description: style.description,
            process_verb: style.process_verb,
            execution_probability: style.execution_probability,
          };

          // Add effector (backwards compat) or effectors
          if (style.effectors && Array.isArray(style.effectors)) {
            styleConfig.effectors = style.effectors;
          } else if (style.effector) {
            styleConfig.effector = style.effector;
          }

          // Add style attributes
          if (style.style_attributes) {
            styleConfig.style_attributes = style.style_attributes;
          }

          return styleConfig;
        });
      }

      // Add affinities
      if (skillConfig.affinities) {
        yamlConfig.affinities = {
          elemental: skillConfig.affinities.elemental || {},
          race: skillConfig.affinities.race || {},
        };
      }

      // Add detriments
      if (skillConfig.detriments) {
        yamlConfig.detriments = {
          elemental: skillConfig.detriments.elemental || {},
          race: skillConfig.detriments.race || {},
        };
      }

      return yaml.stringify(yamlConfig, { indent: 2 });
    } catch (error) {
      return `Error generating YAML: ${error}`;
    }
  }, [skillConfig]);

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
