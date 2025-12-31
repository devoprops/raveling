import { COLORS } from '../constants/colors';

export default function AboutPage() {
  return (
    <div style={{ padding: '2rem', maxWidth: '800px', margin: '0 auto', color: COLORS.TEXT_SECONDARY }}>
      <h1 style={{ color: COLORS.PRIMARY_BLUE }}>About Raveling</h1>
      <p>Raveling is a MUD (Multi-User Dungeon) game with an integrated designer suite for creating game content.</p>
      <p>This page will contain more information about the project.</p>
    </div>
  );
}

