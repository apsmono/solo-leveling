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
    <section id="galeri" className="py-10 scroll-mt-[var(--nav-offset,5rem)]">
      <div className="container-main">
        <AnimatedSection>
          <Card>
            <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Galeri</p>
            <h2 className="text-[clamp(1.8rem,3vw,2.8rem)]">Jejak pre-wedding kami</h2>
            <p className="text-brown-500 mt-4 max-w-[42rem]">
              Beberapa momen kami abadikan sebelum hari pernikahan. Sentuh foto untuk memperbesar.
            </p>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
              {galleryImages.map((img, i) => (
                <article
                  key={i}
                  className="p-3 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)] cursor-pointer hover:shadow-soft transition-shadow"
                >
                  <button
                    type="button"
                    onClick={() => openLightbox(i)}
                    className="w-full text-left border-none bg-transparent p-0 font-inherit cursor-pointer"
                  >
                    <div className="h-[200px] rounded-[18px] mb-4 relative overflow-hidden bg-cream-200">
                      <img
                        src={img.src}
                        alt={img.alt}
                        width={800}
                        height={600}
                        loading="lazy"
                        decoding="async"
                        className="h-full w-full object-cover"
                        sizes="(max-width: 768px) 100vw, 33vw"
                      />
                    </div>
                    <h3 className="text-[1rem] mb-1 text-green-800">Kenangan {i + 1}</h3>
                    {img.caption && <p className="text-brown-500 text-[0.9rem]">{img.caption}</p>}
                  </button>
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
