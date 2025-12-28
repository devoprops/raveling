import { NavLink, useLocation } from 'react-router-dom';
import { useState } from 'react';
import { DESIGNER_NAVIGATION, DesignerNavItem } from '../../utils/constants';
import './Sidebar.css';

export default function Sidebar() {
  const location = useLocation();
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  const toggleSection = (id: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedSections(newExpanded);
  };

  const isSectionExpanded = (id: string) => expandedSections.has(id);

  const isActive = (path: string) => {
    return location.pathname.startsWith(path);
  };

  const renderNavItem = (item: DesignerNavItem, level: number = 0) => {
    const hasSubgroups = item.subgroups && item.subgroups.length > 0;
    const isExpanded = isSectionExpanded(item.id);
    const active = isActive(item.path);

    return (
      <div key={item.id} className={`nav-item level-${level}`}>
        <div className="nav-item-header">
          {hasSubgroups && (
            <button
              className="expand-btn"
              onClick={() => toggleSection(item.id)}
              aria-label={isExpanded ? 'Collapse' : 'Expand'}
            >
              <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>▶</span>
            </button>
          )}
          <NavLink
            to={item.path}
            className={({ isActive }) => `nav-item-link ${isActive ? 'active' : ''}`}
          >
            {item.icon && <span className="nav-icon">{item.icon}</span>}
            <span className="nav-label">{item.label}</span>
          </NavLink>
        </div>
        {hasSubgroups && isExpanded && (
          <div className="nav-subgroups">
            {item.subgroups!.map((subgroup) => renderNavItem(subgroup, level + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <aside className="designer-sidebar">
      <div className="sidebar-header">
        <h2 className="sidebar-title">
          <span className="title-icon">⚒️</span>
          Designer Suite
        </h2>
      </div>
      <nav className="sidebar-nav">
        {DESIGNER_NAVIGATION.map((item) => renderNavItem(item))}
      </nav>
    </aside>
  );
}

