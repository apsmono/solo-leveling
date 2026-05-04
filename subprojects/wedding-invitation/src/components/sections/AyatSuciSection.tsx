import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { AYAT_ARABIC, AYAT_TRANSLATION } from '@/lib/constants';

export function AyatSuciSection() {
  return (
    <section id="ayatsuci" className="py-10 scroll-mt-[var(--nav-offset,5rem)]">
      <div className="container-main">
        <AnimatedSection>
          <Card className="text-center max-w-3xl mx-auto">
            <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">
              Ayat Suci
            </p>
            <h2 className="text-[clamp(1.8rem,3vw,2.6rem)] mb-6">Ayat yang mengiringi langkah kami</h2>
            <p
              lang="ar"
              dir="rtl"
              className="font-serif text-[clamp(1.35rem,4vw,1.85rem)] leading-relaxed text-green-800 mb-6"
            >
              {AYAT_ARABIC}
            </p>
            <p className="text-brown-500 text-[0.98rem] leading-relaxed text-left">
              {AYAT_TRANSLATION}
            </p>
          </Card>
        </AnimatedSection>
      </div>
    </section>
  );
}
