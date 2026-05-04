import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';

export function StorySection() {
  return (
    <section id="kisah" className="py-10 scroll-mt-[var(--nav-offset,5rem)]">
      <div className="container-main">
        <AnimatedSection>
          <Card>
            <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Kisah Kami</p>
            <h2 className="text-[clamp(1.8rem,3vw,2.8rem)]">Langkah kecil menuju ikatan yang diridhai</h2>
            <p className="text-brown-500 mt-4 max-w-[42rem]">
              Dengan izin Allah SWT, perjalanan kami bertumbuh dari pertemuan-pertemuan sederhana
              menjadi niat yang semakin mantap untuk melangkah bersama. Kami berharap hari pernikahan
              ini terasa teduh, hangat, dan penuh adab, sebagaimana rumah tangga yang ingin kami bangun kelak.
            </p>
          </Card>
        </AnimatedSection>
      </div>
    </section>
  );
}
