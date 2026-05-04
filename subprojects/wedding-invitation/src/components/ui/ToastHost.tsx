import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useInvitationStore } from '@/store/useInvitationStore';

/** Fixed toast for copy success and RSVP confirmation */
export function ToastHost() {
  const toastMessage = useInvitationStore((s) => s.toastMessage);
  const dismissToast = useInvitationStore((s) => s.dismissToast);

  useEffect(() => {
    if (!toastMessage) return undefined;
    const id = window.setTimeout(() => dismissToast(), 4000);
    return () => window.clearTimeout(id);
  }, [toastMessage, dismissToast]);

  return (
    <AnimatePresence>
      {toastMessage && (
        <motion.div
          role="status"
          aria-live="polite"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 8 }}
          transition={{ duration: 0.22 }}
          className="fixed bottom-24 left-1/2 z-[60] max-w-[min(92vw,22rem)] -translate-x-1/2 rounded-2xl border border-[rgba(120,86,55,0.18)] bg-surface px-5 py-3 text-center text-[0.92rem] font-medium text-green-800 shadow-soft"
        >
          {toastMessage}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
