import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { VENUE_AKAD, VENUE_RESEPSI } from '@/lib/constants';

function MapEmbed({ title, embedUrl }: { title: string; embedUrl: string }) {
  return (
    <div className="overflow-hidden rounded-[20px] border border-[rgba(120,86,55,0.12)] bg-[rgba(255,252,248,0.5)]">
      <iframe
        title={title}
        src={embedUrl}
        className="aspect-[4/3] w-full border-0"
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
        allowFullScreen
      />
    </div>
  );
}

export function LocationSection() {
  return (
    <section id="lokasi" className="py-10 scroll-mt-[var(--nav-offset,5rem)]">
      <div className="container-main">
        <AnimatedSection>
          <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4 text-center">
            Lokasi
          </p>
          <h2 className="text-[clamp(1.8rem,3vw,2.8rem)] text-center mb-4">Petunjuk menuju venue</h2>
          <p className="text-brown-500 text-center max-w-2xl mx-auto mb-10">
            Silakan gunakan peta berikut untuk menuju lokasi akad dan resepsi. Semoga perjalanan Bapak/Ibu/Saudara/i
            senantiasa diberi kelancaran.
          </p>
        </AnimatedSection>

        <div className="grid lg:grid-cols-2 gap-8">
          <AnimatedSection>
            <Card>
              <h3 className="text-[1.35rem] mb-2">{VENUE_AKAD.title}</h3>
              <p className="text-bronze-500 text-[0.85rem] uppercase tracking-[0.18em] mb-3">
                {VENUE_AKAD.scheduleLabel}
              </p>
              <p className="text-brown-500 mb-4 whitespace-pre-line">{VENUE_AKAD.addressLine}</p>
              <MapEmbed title={`Peta ${VENUE_AKAD.title}`} embedUrl={VENUE_AKAD.embedUrl} />
              <Button
                href={VENUE_AKAD.directionsUrl}
                external
                className="mt-5 w-full justify-center sm:w-auto"
              >
                Petunjuk Lokasi
              </Button>
            </Card>
          </AnimatedSection>

          <AnimatedSection delay={0.12}>
            <Card>
              <h3 className="text-[1.35rem] mb-2">{VENUE_RESEPSI.title}</h3>
              <p className="text-bronze-500 text-[0.85rem] uppercase tracking-[0.18em] mb-3">
                {VENUE_RESEPSI.scheduleLabel}
              </p>
              <p className="text-brown-500 mb-4 whitespace-pre-line">{VENUE_RESEPSI.addressLine}</p>
              <MapEmbed title={`Peta ${VENUE_RESEPSI.title}`} embedUrl={VENUE_RESEPSI.embedUrl} />
              <Button
                href={VENUE_RESEPSI.directionsUrl}
                external
                className="mt-5 w-full justify-center sm:w-auto"
              >
                Petunjuk Lokasi
              </Button>
            </Card>
          </AnimatedSection>
        </div>
      </div>
    </section>
  );
}
