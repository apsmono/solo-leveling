import { useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import { useInvitationStore } from '@/store/useInvitationStore';
import { Navbar } from '@/components/layout/Navbar';
import { Footer } from '@/components/layout/Footer';
import { MusicPlayer } from '@/components/layout/MusicPlayer';
import { OpeningScreen } from '@/components/sections/OpeningScreen';
import { HeroSection } from '@/components/sections/HeroSection';
import { InvitationCard } from '@/components/sections/InvitationCard';
import { CountdownSection } from '@/components/sections/CountdownSection';
import { StorySection } from '@/components/sections/StorySection';
import { EventsSection } from '@/components/sections/EventsSection';
import { GallerySection } from '@/components/sections/GallerySection';
import { GuestGuideSection } from '@/components/sections/GuestGuideSection';
import { RsvpSection } from '@/components/sections/RsvpSection';
import { ThanksSection } from '@/components/sections/ThanksSection';
import { WishesSection } from '@/components/sections/WishesSection';

function App() {
  const { setGuestName, isOpened } = useInvitationStore();

  // Parse guest name from URL query param
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const to = params.get('to');
    if (to) {
      const decoded = decodeURIComponent(to).trim();
      setGuestName(decoded);
    }
  }, [setGuestName]);

  return (
    <>
      <AnimatePresence mode="wait">
        {!isOpened && <OpeningScreen key="opening" />}
      </AnimatePresence>

      {isOpened && (
        <>
          <Navbar />
          <main>
            <HeroSection />
            <InvitationCard />
            <CountdownSection />
            <StorySection />
            <EventsSection />
            <GallerySection />
            <GuestGuideSection />
            <RsvpSection />
            <ThanksSection />
            <WishesSection />
          </main>
          <Footer />
          <MusicPlayer />
        </>
      )}
    </>
  );
}

export default App;
