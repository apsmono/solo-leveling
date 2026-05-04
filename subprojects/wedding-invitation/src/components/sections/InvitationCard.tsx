import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { WEDDING_DATE_LABEL_LONG } from '@/lib/constants';

export function InvitationCard() {
  return (
    <section className="py-10">
      <div className="container-main">
        <AnimatedSection>
          <Card className="relative animate-drift text-center max-w-2xl mx-auto">
            <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Undangan</p>
            <div className="w-[72px] h-px mx-auto mb-5 bg-gradient-to-r from-transparent via-[rgba(139,94,60,0.45)] to-transparent" />
            <p className="font-serif text-[1.1rem] text-bronze-500 mb-4">{WEDDING_DATE_LABEL_LONG}</p>
            <h3 className="text-[1.15rem] mb-4">Dengan memohon rahmat dan ridha Allah SWT</h3>
            <ul className="list-none mt-6 grid gap-4 text-left">
              <li className="relative pl-5 text-brown-500">
                <span className="absolute left-0 top-[0.55em] w-2 h-2 rounded-full bg-bronze-400" />
                Akad dan resepsi InsyaAllah dilaksanakan sesuai waktu yang tertera pada bagian informasi acara.
              </li>
              <li className="relative pl-5 text-brown-500">
                <span className="absolute left-0 top-[0.55em] w-2 h-2 rounded-full bg-bronze-400" />
                Kehadiran Bapak/Ibu/Saudara/i akan melengkapi kebahagiaan kami dalam suasana hangat dan penuh adab.
              </li>
              <li className="relative pl-5 text-brown-500">
                <span className="absolute left-0 top-[0.55em] w-2 h-2 rounded-full bg-bronze-400" />
                Mohon mengenakan busana sopan dan nyaman dengan nuansa warna lembut, sesuai ketentuan acara.
              </li>
            </ul>
          </Card>
        </AnimatedSection>
      </div>
    </section>
  );
}
