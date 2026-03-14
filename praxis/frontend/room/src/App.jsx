import { useEffect } from 'react';
import { RoomProvider, useRoomState, useRoomDispatch, PHASES } from './context/RoomContext';
import AmbientBackground from './components/ambient/AmbientBackground';
import ParticleField from './components/ambient/ParticleField';
import TopBar from './components/verdict/TopBar';
import VerdictPanel from './components/verdict/VerdictPanel';
import EvidencePanel from './components/verdict/EvidencePanel';
import CommandBar from './components/verdict/CommandBar';
import useDecayAlerts from './hooks/useDecayAlerts';

function RoomShell() {
  const { room, phase, differentialResult } = useRoomState();
  const dispatch = useRoomDispatch();

  const hasResults = !!differentialResult || phase === PHASES.ELIMINATING || phase === PHASES.EXECUTING;

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

  // Pick up query from URL params (when navigating from homepage)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const q = params.get('q');
    if (q) {
      // Clear URL params without reload
      window.history.replaceState({}, '', '/room');
      dispatch({ type: 'SET_QUERY', payload: q });
    }
  }, [dispatch]);

  useDecayAlerts(30000);

  return (
    <>
      <AmbientBackground />
      <ParticleField />
      <div className="noise" />
      <div className="relative z-10 flex flex-col h-screen w-screen">
        {hasResults ? (
          <>
            <TopBar />
            <div className="flex flex-1 overflow-hidden max-[900px]:flex-col">
              <VerdictPanel />
              <EvidencePanel />
            </div>
          </>
        ) : (
          <>
            {/* Minimal top bar for empty state */}
            <div
              className="relative z-30 flex items-center gap-4 px-5 py-2.5 border-b border-white/[0.06]"
              style={{ background: 'rgba(10,10,15,0.5)', backdropFilter: 'blur(30px)' }}
            >
              <a href="/" className="text-white/30 hover:text-white/60 text-sm transition-colors">{'\u2190'} Praxis</a>
              <span className="text-white/10">|</span>
              <span className="text-sm text-white/40 font-medium">Room</span>
            </div>
            <CommandBar />
          </>
        )}
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
