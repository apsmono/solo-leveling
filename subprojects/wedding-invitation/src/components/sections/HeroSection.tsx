import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Button } from '@/components/ui/Button';
import {
  BRIDE_NAME,
  COVER_IMAGE_SRC,
  GROOM_NAME,
  WEDDING_DATE_LABEL_LONG,
} from '@/lib/constants';

export function HeroSection() {
  const showHeroPhoto = Boolean(COVER_IMAGE_SRC.trim());

  return (
    <section id="beranda" className="text-center pt-14 pb-12 relative scroll-mt-[var(--nav-offset,5rem)]">
      <AnimatedSection>
        <div className="flex justify-center mb-6 text-bronze-500">
          <svg viewBox="0 0 120 40" xmlns="http://www.w3.org/2000/svg" className="w-[clamp(132px,16vw,188px)] h-auto opacity-90">
            <path d="M0 20 Q30 0 60 20 Q90 40 120 20" fill="none" stroke="currentColor" strokeWidth="1" opacity="0.4"/>
            <circle cx="20" cy="18" r="2" fill="currentColor" opacity="0.3"/>
            <circle cx="100" cy="22" r="2" fill="currentColor" opacity="0.3"/>
          </svg>
        </div>
      </AnimatedSection>

      {showHeroPhoto && (
        <AnimatedSection delay={0.05}>
          <div className="mx-auto mb-8 max-w-[min(92vw,340px)] overflow-hidden rounded-[28px] shadow-soft border border-[rgba(120,86,55,0.12)]">
            <img
              src={COVER_IMAGE_SRC}
              alt={`Foto pasangan pengantin ${GROOM_NAME} dan ${BRIDE_NAME}`}
              width={680}
              height={850}
              className="aspect-[4/5] w-full object-cover"
              loading="eager"
              decoding="async"
            />
          </div>
        </AnimatedSection>
      )}

      <AnimatedSection delay={0.1}>
        <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">{WEDDING_DATE_LABEL_LONG}</p>
      </AnimatedSection>

      <AnimatedSection delay={0.2}>
        <h1 className="text-[clamp(2.8rem,8vw,6.75rem)] mb-6">
          {GROOM_NAME} <span className="italic font-medium text-bronze-500">&amp;</span> {BRIDE_NAME}
        </h1>
      </AnimatedSection>

      <AnimatedSection delay={0.3}>
        <p className="max-w-[34rem] mx-auto text-[1.05rem] text-brown-500 leading-relaxed">
          Dengan memohon rahmat dan ridha Allah SWT, kami bermaksud mengundang Bapak/Ibu/Saudara/i untuk hadir pada
          hari bahagia kami. Kehadiran serta doa restu panjenengan akan menjadi kebahagiaan yang sangat kami syukuri.
        </p>
      </AnimatedSection>

      <AnimatedSection delay={0.4}>
        <div className="flex justify-center gap-4 mt-8 flex-wrap">
          <Button href="#rsvp">Isi Konfirmasi</Button>
          <Button variant="secondary" href="#acara">
            Informasi Acara
          </Button>
        </div>
      </AnimatedSection>
    </section>
  );
}
