/**
 * Color constants for the Raveling MUD application.
 * Regal blue/green theme with RPG aesthetic.
 */

// Primary Colors
export const COLORS = {
  // Primary Blues
  PRIMARY_BLUE: '#4a90e2',
  PRIMARY_BLUE_LIGHT: '#7db8e8',
  PRIMARY_BLUE_DARK: '#2c5aa0',
  
  // Primary Greens
  PRIMARY_GREEN: '#5cb85c',
  PRIMARY_GREEN_LIGHT: '#7dd87d',
  PRIMARY_GREEN_DARK: '#3d8b3d',
  
  // Additional Blues/Greens
  SKY_BLUE: '#6ab3d3',
  LIME_GREEN: '#8bc34a',
  MEDIUM_BLUE: '#5e9fd4',
  MEDIUM_GREEN: '#66bb6a',
  BRIGHT_BLUE: '#42a5f5',
  BRIGHT_GREEN: '#4caf50',
  
  // Error/Destructive (keep red)
  ERROR: '#e94560',
  ERROR_LIGHT: '#ff6b9d',
  ERROR_DARK: '#c93550',
  
  // Neutral Colors
  BACKGROUND: '#0f1419',
  BACKGROUND_LIGHT: '#1a1a2e',
  BACKGROUND_DARK: '#0a0f14',
  TEXT_PRIMARY: 'rgba(255, 255, 255, 0.87)',
  TEXT_SECONDARY: '#c4c4c4',
  TEXT_MUTED: '#999',
  TEXT_DISABLED: '#666',
  
  // Borders and Overlays
  BORDER: 'rgba(74, 144, 226, 0.3)',
  BORDER_LIGHT: 'rgba(74, 144, 226, 0.2)',
  BORDER_DARK: 'rgba(74, 144, 226, 0.5)',
  OVERLAY: 'rgba(0, 0, 0, 0.3)',
  OVERLAY_LIGHT: 'rgba(0, 0, 0, 0.2)',
  OVERLAY_DARK: 'rgba(0, 0, 0, 0.5)',
  OVERLAY_DARKER: 'rgba(0, 0, 0, 0.8)',
  
  // Element Colors (for damage types, etc.)
  ELEMENT_EARTH: '#8b4513',
  ELEMENT_WATER: '#4169e1',
  ELEMENT_AIR: '#87ceeb',
  ELEMENT_FIRE: '#ff4500',
  
  // Damage Colors
  DAMAGE_PHYSICAL: '#808080',
} as const;

// RGBA variants for common colors
export const COLORS_RGBA = {
  PRIMARY_BLUE_10: 'rgba(74, 144, 226, 0.1)',
  PRIMARY_BLUE_20: 'rgba(74, 144, 226, 0.2)',
  PRIMARY_BLUE_30: 'rgba(74, 144, 226, 0.3)',
  PRIMARY_BLUE_40: 'rgba(74, 144, 226, 0.4)',
  PRIMARY_BLUE_50: 'rgba(74, 144, 226, 0.5)',
  PRIMARY_BLUE_60: 'rgba(74, 144, 226, 0.6)',
  
  PRIMARY_GREEN_10: 'rgba(92, 184, 92, 0.1)',
  PRIMARY_GREEN_20: 'rgba(92, 184, 92, 0.2)',
  PRIMARY_GREEN_30: 'rgba(92, 184, 92, 0.3)',
  
  ERROR_10: 'rgba(233, 69, 96, 0.1)',
  ERROR_20: 'rgba(233, 69, 96, 0.2)',
  ERROR_30: 'rgba(233, 69, 96, 0.3)',
  ERROR_40: 'rgba(233, 69, 96, 0.4)',
  ERROR_50: 'rgba(233, 69, 96, 0.5)',
  ERROR_60: 'rgba(233, 69, 96, 0.6)',
} as const;

// Regal color palette for user colors (collaboration notes)
export const REGAL_COLORS = [
  COLORS.PRIMARY_BLUE,
  COLORS.PRIMARY_GREEN,
  COLORS.PRIMARY_BLUE_LIGHT,
  COLORS.PRIMARY_GREEN_LIGHT,
  COLORS.PRIMARY_BLUE_DARK,
  COLORS.PRIMARY_GREEN_DARK,
  COLORS.SKY_BLUE,
  COLORS.LIME_GREEN,
  COLORS.MEDIUM_BLUE,
  COLORS.MEDIUM_GREEN,
  COLORS.BRIGHT_BLUE,
  COLORS.BRIGHT_GREEN,
] as const;

// Element color mapping
export const ELEMENT_COLORS: Record<string, string> = {
  Earth: COLORS.ELEMENT_EARTH,
  Water: COLORS.ELEMENT_WATER,
  Air: COLORS.ELEMENT_AIR,
  Fire: COLORS.ELEMENT_FIRE,
};

