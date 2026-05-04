import { motion } from 'framer-motion';
import { useInvitationStore } from '@/store/useInvitationStore';
import { Button } from '@/components/ui/Button';
import { BRIDE_NAME, COVER_IMAGE_SRC, GROOM_NAME } from '@/lib/constants';

export function OpeningScreen() {
  const { guestName, openInvitation, toggleMusic } = useInvitationStore();

  const handleOpen = () => {
    openInvitation();
    toggleMusic();
  };

  const displayName = guestName?.trim() || 'Tamu Undangan';
  const showCover = Boolean(COVER_IMAGE_SRC.trim());

  return (
    <motion.div
      className="fixed inset-0 z-50 flex flex-col items-center justify-center px-6"
      style={{
        background:
          'radial-gradient(circle at top left, rgba(255,255,255,0.58), transparent 35%), radial-gradient(circle at 82% 10%, rgba(160,119,62,0.24), transparent 24%), radial-gradient(circle at 18% 88%, rgba(46,82,59,0.14), transparent 24%), linear-gradient(180deg, #f8f0e3 0%, #efe2cc 46%, #dcc6a4 100%)',
      }}
      initial={{ opacity: 1 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.8, ease: 'easeInOut' }}
    >
      <div
        className="fixed inset-0 pointer-events-none z-0"
        style={{
          background:
            'linear-gradient(130deg, rgba(255,255,255,0.12), transparent 30%), repeating-linear-gradient(45deg, transparent 0, transparent 26px, rgba(98,71,44,0.03) 26px, rgba(98,71,44,0.03) 28px), repeating-linear-gradient(90deg, transparent 0, transparent 38px, rgba(122,95,70,0.03) 38px, rgba(122,95,70,0.03) 39px)',
        }}
      />

      <motion.div
        className="relative z-10 text-center max-w-md"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, delay: 0.2 }}
      >
        <motion.div
          className="flex justify-center mb-6 text-bronze-500"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <svg viewBox="0 0 120 40" xmlns="http://www.w3.org/2000/svg" className="w-[clamp(132px,16vw,188px)] h-auto opacity-90">
            <path d="M0 20 Q30 0 60 20 Q90 40 120 20" fill="none" stroke="currentColor" strokeWidth="1" opacity="0.4"/>
            <circle cx="20" cy="18" r="2" fill="currentColor" opacity="0.3"/>
            <circle cx="100" cy="22" r="2" fill="currentColor" opacity="0.3"/>
          </svg>
        </motion.div>

        {showCover && (
          <motion.div
            className="mx-auto mb-8 max-h-[min(42vh,280px)] w-full max-w-[280px] overflow-hidden rounded-[28px] shadow-soft border border-[rgba(120,86,55,0.14)]"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, delay: 0.35 }}
          >
            <img
              src={COVER_IMAGE_SRC}
              alt={`Foto sampul undangan pernikahan ${GROOM_NAME} dan ${BRIDE_NAME}`}
              width={560}
              height={700}
              className="h-full w-full object-cover"
              loading="eager"
              decoding="async"
            />
          </motion.div>
        )}

        <motion.p
          className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-3"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          Undangan Pernikahan
        </motion.p>

        <motion.h1
          className="font-serif text-[clamp(2.2rem,5.5vw,3.75rem)] text-green-800 mb-8"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
        >
          {GROOM_NAME} <span className="italic font-medium text-bronze-500">&amp;</span> {BRIDE_NAME}
        </motion.h1>

        <motion.div
          className="mb-10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
        >
          <p className="text-[0.85rem] text-brown-400 mb-2">Kepada Yth.</p>
          <p className="text-[0.85rem] text-brown-400 mb-3">Bapak/Ibu/Saudara/i</p>
          <p className="font-serif text-[1.5rem] text-green-800 font-semibold" aria-live="polite">
            {displayName}
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.0 }}>
          <Button onClick={handleOpen} className="px-8">
            Buka Undangan
          </Button>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
