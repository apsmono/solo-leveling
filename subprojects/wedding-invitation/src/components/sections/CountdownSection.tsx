import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { useCountdown } from '@/hooks/useCountdown';
import { WEDDING_DATE } from '@/lib/constants';

export function CountdownSection() {
  const { days, hours, minutes, seconds } = useCountdown(WEDDING_DATE);

  const cells = [
    { value: days, label: 'Hari' },
    { value: hours, label: 'Jam' },
    { value: minutes, label: 'Menit' },
    { value: seconds, label: 'Detik' },
  ];

  return (
    <section className="py-10">
      <div className="container-main">
        <AnimatedSection>
          <Card className="text-center">
            <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Hitung Mundur</p>
            <h2 className="text-[clamp(1.8rem,3vw,2.8rem)]">Menuju hari yang kami nantikan</h2>
            <p className="text-brown-500 mt-4 max-w-[42rem] mx-auto">
              Hitung mundur menuju hari yang kami nantikan. Informasi acara, lokasi, dan konfirmasi kehadiran dapat
              diakses melalui tautan undangan ini.
            </p>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mt-8">
              {cells.map((cell) => (
                <div
                  key={cell.label}
                  className="py-6 px-4 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)]"
                >
                  <strong className="block text-[2rem] font-serif text-green-800 mb-1">{cell.value}</strong>
                  <span className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400">{cell.label}</span>
                </div>
              ))}
            </div>
          </Card>
        </AnimatedSection>
      </div>
    </section>
  );
}
