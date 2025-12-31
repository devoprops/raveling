/**
 * User color utilities for collaboration notes.
 * Generates colors from a regal blue/green palette.
 */

import { REGAL_COLORS } from '../constants/colors';

/**
 * Generate a random color from the regal palette.
 */
export function generateRandomColor(): string {
  const index = Math.floor(Math.random() * REGAL_COLORS.length);
  return REGAL_COLORS[index] as string;
}

/**
 * Hash a string to a consistent number.
 */
function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash);
}

/**
 * Get user color from database if set, otherwise generate consistent color based on user ID.
 */
export function getUserColor(userId: number | string, userColorFromDB: string | null | undefined): string {
  if (userColorFromDB) {
    return userColorFromDB;
  }
  
  // Generate consistent color based on user ID
  const hash = hashString(String(userId));
  const index = hash % REGAL_COLORS.length;
  return REGAL_COLORS[index];
}

/**
 * Assign a random color to a user (to be saved to database).
 */
export function assignColorToUser(): string {
  return generateRandomColor();
}

