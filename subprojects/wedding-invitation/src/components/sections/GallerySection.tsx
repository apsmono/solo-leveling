import { useState } from 'react';
import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { Lightbox } from '@/components/ui/Lightbox';
import { galleryImages } from '@/lib/constants';

export function GallerySection() {
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const [currentIndex, setCurrentIndex] = useState(0);

  const openLightbox = (index: number) => {
    setCurrentIndex(index);
    setLightboxOpen(true);
  };

  const goPrev = () => setCurrentIndex((i) => (i === 0 ? galleryImages.length - 1 : i - 1));
  const goNext = () => setCurrentIndex((i) => (i === galleryImages.length - 1 ? 0 : i + 1));

  return (
    <section id="galeri" className="py-10">
      <div className="container-main">
        <AnimatedSection>
          <Card>
            <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Galeri</p>
            <h2 className="text-[clamp(1.8rem,3vw,2.8rem)]">Jejak perjalanan kami</h2>
            <p className="text-brown-500 mt-4 max-w-[42rem]">
              Beberapa kenangan yang kami simpan sebagai penanda perjalanan menuju hari pernikahan kami.
            </p>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
              {galleryImages.map((img, i) => (
                <article
                  key={i}
                  className="p-4 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)] cursor-pointer hover:shadow-soft transition-shadow"
                  onClick={() => openLightbox(i)}
                >
                  <div
                    className="h-[120px] rounded-[18px] mb-4 relative overflow-hidden"
                    style={{
                      background: `
                        radial-gradient(circle at 24% 24%, rgba(255,248,236,0.35), transparent 26%),
                        repeating-linear-gradient(45deg, rgba(255,233,201,0.08) 0, rgba(255,233,201,0.08) 12px, transparent 12px, transparent 24px),
                        linear-gradient(135deg, rgba(50,92,65,0.82), rgba(175,130,67,0.72))
                      `,
                    }}
                  >
                    <div className="absolute inset-4 rounded-2xl border border-[rgba(255,241,224,0.35)]" />
                  </div>
                  <h3 className="text-[1rem] mb-1">{img.alt}</h3>
                  <p className="text-brown-500 text-[0.9rem]">{img.caption}</p>
                </article>
              ))}
            </div>
          </Card>
        </AnimatedSection>
      </div>

      <Lightbox
        images={galleryImages}
        currentIndex={currentIndex}
        isOpen={lightboxOpen}
        onClose={() => setLightboxOpen(false)}
        onPrev={goPrev}
        onNext={goNext}
      />
    </section>
  );
}
