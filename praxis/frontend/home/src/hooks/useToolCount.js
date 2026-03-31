import { useState, useEffect } from 'react';

export default function useToolCount() {
  const [count, setCount] = useState(254);
  useEffect(() => {
    fetch('/tools/count')
      .then(r => r.json())
      .then(d => { if (d.count) setCount(d.count); })
      .catch(() => {});
  }, []);
  return count;
}
