import { useMemo } from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import yaml from 'yaml';
import { SpellFormData } from './SpellForm';
import './YAMLPreview.css';

interface YAMLPreviewProps {
  spellConfig: SpellFormData;
}

export default function YAMLPreview({ spellConfig }: YAMLPreviewProps) {
  const yamlString = useMemo(() => {
    try {
      // Convert spell config to YAML format
      const yamlConfig: any = {
        name: spellConfig.name || '',
        short_desc: spellConfig.short_desc || '',
        long_desc: spellConfig.long_desc || '',
        item_type: 'spell',
      };

      // Add category and school if provided
      if (spellConfig.category) {
        yamlConfig.category = spellConfig.category;
      }
      if (spellConfig.school) {
        yamlConfig.school = spellConfig.school;
      }

      // Add effect styles
      if (spellConfig.effect_styles && spellConfig.effect_styles.length > 0) {
        yamlConfig.effect_styles = spellConfig.effect_styles.map((style: any) => {
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
      if (spellConfig.affinities) {
        yamlConfig.affinities = {
          elemental: spellConfig.affinities.elemental || {},
          race: spellConfig.affinities.race || {},
        };
      }

      // Add detriments
      if (spellConfig.detriments) {
        yamlConfig.detriments = {
          elemental: spellConfig.detriments.elemental || {},
          race: spellConfig.detriments.race || {},
        };
      }

      return yaml.stringify(yamlConfig, { indent: 2 });
    } catch (error) {
      return `Error generating YAML: ${error}`;
    }
  }, [spellConfig]);

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
