import { useState, useEffect } from 'react';
import axios from 'axios';
import { getUserColor, assignColorToUser } from '../utils/userColors';
import { useAuth } from './useAuth';
import { COLORS } from '../constants/colors';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function useUserColor() {
  const { user } = useAuth();
  const [userColor, setUserColor] = useState<string>(COLORS.PRIMARY_BLUE); // Default royal blue
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }

    const fetchUserColor = async () => {
      try {
        const token = localStorage.getItem('auth_token') || localStorage.getItem('token');
        const response = await axios.get(`${API_URL}/api/collaboration/user-color`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        const color = response.data.user_color;
        if (color) {
          setUserColor(color);
        } else {
          // No color set, generate and save one
          const newColor = assignColorToUser();
          await axios.put(
            `${API_URL}/api/collaboration/user-color`,
            { user_color: newColor },
            { headers: { Authorization: `Bearer ${token}` } }
          );
          setUserColor(newColor);
        }
      } catch (error) {
        console.error('Failed to fetch user color:', error);
        // Fallback to consistent color based on user ID
        const fallbackColor = getUserColor(user.id, null);
        setUserColor(fallbackColor);
      } finally {
        setLoading(false);
      }
    };

    fetchUserColor();
  }, [user]);

  const updateUserColor = async (newColor: string) => {
    if (!user) return;

    try {
      const token = localStorage.getItem('auth_token');
      await axios.put(
        `${API_URL}/api/collaboration/user-color`,
        { user_color: newColor },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setUserColor(newColor);
    } catch (error) {
      console.error('Failed to update user color:', error);
      throw error;
    }
  };

  return { userColor, updateUserColor, loading };
}

