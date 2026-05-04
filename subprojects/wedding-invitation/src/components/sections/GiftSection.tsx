import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useInvitationStore } from '@/store/useInvitationStore';
import { BANK_COPY_TEXT, BANK_DISPLAY_LINE, QRIS_IMAGE_SRC } from '@/lib/constants';

export function GiftSection() {
  const showToast = useInvitationStore((s) => s.showToast);

  const handleCopy = async () => {
    const text = BANK_COPY_TEXT.trim();
    if (!text || text.startsWith('[')) {
      showToast('Mohon atur nomor rekening di pengaturan undangan terlebih dahulu.');
      return;
    }
    try {
      await navigator.clipboard.writeText(text);
      showToast('Berhasil disalin!');
    } catch {
      showToast('Tidak dapat menyalin otomatis. Mohon salin manual.');
    }
  };

  const showQris = QRIS_IMAGE_SRC.trim().length > 0;

  return (
    <section id="hadiah" className="py-10 scroll-mt-[var(--nav-offset,5rem)]">
      <div className="container-main">
        <AnimatedSection>
          <Card className="max-w-2xl mx-auto text-center">
            <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Kirim Hadiah</p>
            <h2 className="text-[clamp(1.8rem,3vw,2.8rem)] mb-4">Tanda kasih (opsional)</h2>
            <p className="text-brown-500 leading-relaxed mb-8">
              Kehadiran dan doa restu Bapak/Ibu/Saudara/i adalah anugerah terindah. Apabila berkenan mengirimkan tanda
              kasih, transfer dapat dilakukan ke rekening berikut.
            </p>

            <div className="rounded-[20px] bg-[rgba(255,252,248,0.72)] border border-[rgba(120,86,55,0.12)] px-6 py-5 text-left mb-6">
              <p className="text-green-800 font-medium text-[1.05rem] leading-snug">{BANK_DISPLAY_LINE}</p>
            </div>

            <Button type="button" onClick={handleCopy} className="mx-auto">
              Salin Nomor Rekening
            </Button>

            {showQris && (
              <div className="mt-10 grid gap-3">
                <p className="text-[0.9rem] text-brown-500">Atau scan QRIS berikut:</p>
                <div className="mx-auto max-w-[220px] rounded-2xl border border-[rgba(120,86,55,0.12)] bg-white p-3 shadow-soft">
                  <img
                    src={QRIS_IMAGE_SRC}
                    alt="Kode QR untuk pembayaran QRIS"
                    width={196}
                    height={196}
                    loading="lazy"
                    decoding="async"
                    className="mx-auto h-auto w-full rounded-lg"
                  />
                </div>
              </div>
            )}
          </Card>
        </AnimatedSection>
      </div>
    </section>
  );
}
