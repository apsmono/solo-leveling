import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { VENUE_AKAD, VENUE_RESEPSI } from '@/lib/constants';

export function EventsSection() {
  return (
    <section id="acara" className="py-10 scroll-mt-[var(--nav-offset,5rem)]">
      <div className="container-main">
        <AnimatedSection>
          <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4 text-center">
            Informasi Acara
          </p>
          <h2 className="text-[clamp(1.8rem,3vw,2.8rem)] text-center mb-4">Waktu dan rangkaian</h2>
          <p className="text-brown-500 text-center max-w-2xl mx-auto mb-12">
            Dengan memohon rahmat Allah SWT, rangkaian akad dan resepsi InsyaAllah akan dilaksanakan sesuai ketentuan
            berikut. Mohon kehadiran tepat waktu demi kelancaran acara.
          </p>
        </AnimatedSection>

        <div className="grid lg:grid-cols-2 gap-8">
          <AnimatedSection>
            <Card>
              <span className="inline-block uppercase tracking-[0.22em] text-[0.74rem] text-bronze-500 mb-3">
                {VENUE_AKAD.title}
              </span>
              <h3 className="text-[1.45rem] mb-4 text-green-800">{VENUE_AKAD.scheduleLabel}</h3>
              <p className="text-brown-500 whitespace-pre-line leading-relaxed">{VENUE_AKAD.addressLine}</p>
              <div className="mt-6 p-4 rounded-[18px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.1)] text-[0.92rem] text-brown-500">
                <strong className="text-green-800 block mb-1">Catatan</strong>
                Busana muslim dan sopan sangat kami hargai. Mohon hadir sedikit lebih awal untuk persiapan tempat duduk.
              </div>
            </Card>
          </AnimatedSection>

          <AnimatedSection delay={0.12}>
            <Card>
              <span className="inline-block uppercase tracking-[0.22em] text-[0.74rem] text-bronze-500 mb-3">
                {VENUE_RESEPSI.title}
              </span>
              <h3 className="text-[1.45rem] mb-4 text-green-800">{VENUE_RESEPSI.scheduleLabel}</h3>
              <p className="text-brown-500 whitespace-pre-line leading-relaxed">{VENUE_RESEPSI.addressLine}</p>
              <div className="mt-6 p-4 rounded-[18px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.1)] text-[0.92rem] text-brown-500">
                <strong className="text-green-800 block mb-1">Jamuan</strong>
                Tamu dipersilakan menikmati hidangan dan silaturahmi dalam suasana hangat bersama keluarga.
              </div>
            </Card>
          </AnimatedSection>
        </div>
      </div>
    </section>
  );
}
