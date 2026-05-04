import { useEffect, useState } from 'react';
import { pad } from '@/lib/utils';

interface CountdownResult {
  days: string;
  hours: string;
  minutes: string;
  seconds: string;
}

export function useCountdown(targetDate: Date): CountdownResult {
  const [diff, setDiff] = useState(() =>
    Math.max(targetDate.getTime() - Date.now(), 0)
  );

  useEffect(() => {
    const timer = setInterval(() => {
      setDiff(Math.max(targetDate.getTime() - Date.now(), 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [targetDate]);

  const totalSeconds = Math.floor(diff / 1000);
  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  return {
    days: pad(days),
    hours: pad(hours),
    minutes: pad(minutes),
    seconds: pad(seconds),
  };
}
