import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { scheduleItems } from '@/lib/constants';

export function EventsSection() {
  return (
    <section id="acara" className="py-10">
      <div className="container-main">
        <div className="grid lg:grid-cols-2 gap-8">
          <AnimatedSection>
            <Card>
              <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Informasi</p>
              <h2 className="text-[clamp(1.8rem,3vw,2.8rem)]">Hal yang perlu diketahui</h2>
              <div className="grid gap-4 mt-6">
                <article className="py-4 px-6 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)]">
                  <span className="block uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-1">Busana</span>
                  <strong className="text-green-800 font-medium">
                    Busana formal, sopan, dan nyaman dengan nuansa warna lembut sangat kami anjurkan.
                  </strong>
                </article>
                <article className="py-4 px-6 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)]">
                  <span className="block uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-1">Ramah Tamah</span>
                  <strong className="text-green-800 font-medium">
                    Jamuan sederhana, silaturahmi keluarga, dan suasana hangat akan menemani rangkaian acara.
                  </strong>
                </article>
                <article className="py-4 px-6 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)]">
                  <span className="block uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-1">Catatan</span>
                  <strong className="text-green-800 font-medium">
                    Kami memohon kehadiran tamu sekitar 30 menit lebih awal agar acara dapat dimulai dengan tertib.
                  </strong>
                </article>
              </div>
            </Card>
          </AnimatedSection>

          <AnimatedSection delay={0.2}>
            <Card>
              <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Susunan Acara</p>
              <h2 className="text-[clamp(1.8rem,3vw,2.8rem)]">Rangkaian acara InsyaAllah</h2>
              <ol className="list-none mt-6 grid gap-4">
                {scheduleItems.map((item, i) => (
                  <li
                    key={i}
                    className="grid lg:grid-cols-[96px_1fr] gap-4 items-start py-4 border-t border-[rgba(120,86,55,0.12)] first:border-t-0 first:pt-0"
                  >
                    <p className="m-0 text-bronze-500 uppercase tracking-[0.22em] text-[0.74rem] font-semibold">
                      {item.time}
                    </p>
                    <div>
                      <h3 className="text-[1.15rem] mb-1">{item.title}</h3>
                      <p className="text-brown-500 text-[0.95rem]">{item.description}</p>
                    </div>
                  </li>
                ))}
              </ol>
            </Card>
          </AnimatedSection>
        </div>
      </div>
    </section>
  );
}
