import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';

export function InvitationCard() {
  return (
    <section className="py-10">
      <div className="container-main">
        <AnimatedSection>
          <Card className="relative animate-drift text-center max-w-2xl mx-auto">
            <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Undangan</p>
            <div className="w-[72px] h-px mx-auto mb-5 bg-gradient-to-r from-transparent via-[rgba(139,94,60,0.45)] to-transparent" />
            <p className="font-serif text-[1.1rem] text-bronze-500 mb-4">Senin, 1 Juni 2026</p>
            <h3 className="text-[1.15rem] mb-4">Dengan memohon rahmat dan ridha Allah SWT</h3>
            <ul className="list-none mt-6 grid gap-4 text-left">
              <li className="relative pl-5 text-brown-500">
                <span className="absolute left-0 top-[0.55em] w-2 h-2 rounded-full bg-bronze-400" />
                Akad dan rangkaian syukuran akan diselenggarakan secara khidmat bersama keluarga terdekat.
              </li>
              <li className="relative pl-5 text-brown-500">
                <span className="absolute left-0 top-[0.55em] w-2 h-2 rounded-full bg-bronze-400" />
                Jamuan hangat, silaturahmi, serta kebersamaan sederhana akan mengiringi acara kami.
              </li>
              <li className="relative pl-5 text-brown-500">
                <span className="absolute left-0 top-[0.55em] w-2 h-2 rounded-full bg-bronze-400" />
                Busana sopan dan anggun bernuansa lembut sangat kami harapkan.
              </li>
            </ul>
            <p className="font-serif text-[0.92rem] tracking-[0.08em] text-[rgba(62,91,64,0.56)] lowercase mt-6 text-right">
              mugi pinaringan berkah
            </p>
          </Card>
        </AnimatedSection>
      </div>
    </section>
  );
}
