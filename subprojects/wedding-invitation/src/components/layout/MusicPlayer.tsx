import { useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Volume2, VolumeX } from 'lucide-react';
import { useInvitationStore } from '@/store/useInvitationStore';

export function MusicPlayer() {
  const { isMusicPlaying, toggleMusic, isOpened } = useInvitationStore();
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    audioRef.current = new Audio('/music/background.mp3');
    audioRef.current.loop = true;
    audioRef.current.volume = 0.5;

    return () => {
      audioRef.current?.pause();
      audioRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!audioRef.current) return;
    if (isMusicPlaying && isOpened) {
      audioRef.current.play().catch(() => {
        // Browser may block autoplay; user can click toggle
      });
    } else {
      audioRef.current.pause();
    }
  }, [isMusicPlaying, isOpened]);

  if (!isOpened) return null;

  return (
    <motion.button
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      onClick={toggleMusic}
      className="fixed bottom-6 right-6 z-50 w-12 h-12 rounded-full bg-surface border border-[rgba(120,86,55,0.14)] shadow-soft flex items-center justify-center text-green-800 hover:text-bronze-500 transition-colors"
      aria-label={isMusicPlaying ? 'Matikan musik' : 'Putar musik'}
    >
      <AnimatePresence mode="wait">
        {isMusicPlaying ? (
          <motion.div
            key="playing"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="relative"
          >
            <Volume2 className="w-5 h-5" />
            <span className="absolute inset-0 rounded-full border border-bronze-400 animate-ping opacity-30" />
          </motion.div>
        ) : (
          <motion.div
            key="muted"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <VolumeX className="w-5 h-5" />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  );
}
