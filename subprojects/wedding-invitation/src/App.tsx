import { useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { useInvitationStore } from '@/store/useInvitationStore';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';
import { MusicPlayer } from '@/components/layout/MusicPlayer';
import { ToastHost } from '@/components/ui/ToastHost';
import { OpeningScreen } from '@/components/sections/OpeningScreen';
import { HeroSection } from '@/components/sections/HeroSection';
import { InvitationCard } from '@/components/sections/InvitationCard';
import { CountdownSection } from '@/components/sections/CountdownSection';
import { AyatSuciSection } from '@/components/sections/AyatSuciSection';
import { StorySection } from '@/components/sections/StorySection';
import { EventsSection } from '@/components/sections/EventsSection';
import { GallerySection } from '@/components/sections/GallerySection';
import { LocationSection } from '@/components/sections/LocationSection';
import { RsvpSection } from '@/components/sections/RsvpSection';
import { ThanksSection } from '@/components/sections/ThanksSection';
import { GiftSection } from '@/components/sections/GiftSection';

function App() {
  const { setGuestName, isOpened } = useInvitationStore();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const to = params.get('to');
    if (to) {
      const decoded = decodeURIComponent(to).replace(/\+/g, ' ').trim();
      setGuestName(decoded);
    }
  }, [setGuestName]);

  return (
    <>
      <AnimatePresence mode="wait">{!isOpened && <OpeningScreen key="opening" />}</AnimatePresence>

      {isOpened && (
        <>
          <Navbar />
          <main>
            <HeroSection />
            <InvitationCard />
            <CountdownSection />
            <AyatSuciSection />
            <EventsSection />
            <StorySection />
            <GallerySection />
            <LocationSection />
            <RsvpSection />
            <ThanksSection />
            <GiftSection />
          </main>
          <Footer />
          <MusicPlayer />
          <ToastHost />
        </>
      )}
    </>
  );
}

export default App;
