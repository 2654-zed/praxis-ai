import { useEffect } from 'react';
import { RoomProvider, useRoomState, useRoomDispatch } from './context/RoomContext';
import AmbientBackground from './components/ambient/AmbientBackground';
import ParticleField from './components/ambient/ParticleField';
import TopBar from './components/verdict/TopBar';
import VerdictPanel from './components/verdict/VerdictPanel';
import EvidencePanel from './components/verdict/EvidencePanel';
import useDecayAlerts from './hooks/useDecayAlerts';

function RoomShell() {
  const { room, error, phase } = useRoomState();
  const dispatch = useRoomDispatch();

  // Auto-create or load most recent room on mount
  useEffect(() => {
    async function init() {
      try {
        let rooms = [];
        try {
          const res = await fetch('/room');
          const ct = res.headers.get('content-type') || '';
          if (res.ok && ct.includes('application/json')) {
            const body = await res.json();
            rooms = body.data || body || [];
          }
        } catch {}

        if (Array.isArray(rooms) && rooms.length > 0) {
          dispatch({ type: 'SET_ROOMS', payload: rooms });
          const latest = rooms[rooms.length - 1];
          dispatch({ type: 'SET_ROOM', payload: latest });
        } else {
          const createRes = await fetch('/room', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name: 'My Room', operator_context: {} }),
          });
          if (createRes.ok) {
            const body = await createRes.json();
            const newRoom = body.data || body;
            dispatch({ type: 'SET_ROOM', payload: newRoom });
          }
        }
      } catch (err) {
        console.warn('Room init failed:', err.message);
      }
    }
    init();
  }, [dispatch]);

  useDecayAlerts(30000);

  return (
    <>
      <AmbientBackground />
      <ParticleField />
      <div className="noise" />
      <div className="relative z-10 flex flex-col h-screen w-screen">
        <TopBar />

        {/* Split Verdict Layout */}
        <div className="flex flex-1 overflow-hidden max-[900px]:flex-col">
          <VerdictPanel />
          <EvidencePanel />
        </div>
      </div>
    </>
  );
}

export default function App() {
  return (
    <RoomProvider>
      <RoomShell />
    </RoomProvider>
  );
}
