import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useInvitationStore } from '@/store/useInvitationStore';
import { attendanceLabels } from '@/lib/constants';
import { escapeHtml } from '@/lib/utils';

export function ThanksSection() {
  const { rsvpSubmission, resetRsvp } = useInvitationStore();

  if (!rsvpSubmission) return null;

  const { formData } = rsvpSubmission;

  const summaryItems = [
    { label: 'Nama', value: formData.guestName },
    { label: 'Kehadiran', value: attendanceLabels[formData.attendance] || formData.attendance },
    { label: 'Jumlah Tamu', value: formData.guestCount },
  ];

  return (
    <section id="thanks" className="py-10 scroll-mt-[var(--nav-offset,5rem)]">
      <div className="container-main">
        <AnimatedSection>
          <Card className="max-w-[640px] mx-auto">
            <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Terima kasih</p>
            <h2 className="text-[clamp(1.8rem,3vw,2.8rem)]">Konfirmasi telah dicatat</h2>
            <p className="text-brown-500 mt-4">
              Ringkasan berikut tersimpan di perangkat Anda. Jika WhatsApp terbuka, pesan juga dapat dikirim ulang dari
              riwayat chat.
            </p>

            <div className="grid sm:grid-cols-3 gap-4 my-8">
              {summaryItems.map((item) => (
                <article
                  key={item.label}
                  className="py-4 px-5 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)] grid gap-2"
                >
                  <span className="uppercase tracking-[0.22em] text-[0.72rem] text-brown-400">{item.label}</span>
                  <strong
                    className="text-green-800 font-medium text-[0.98rem]"
                    dangerouslySetInnerHTML={{ __html: escapeHtml(item.value) }}
                  />
                </article>
              ))}
            </div>

            <p className="text-brown-500 text-[0.95rem] leading-relaxed mb-6">
              Merupakan suatu kehormatan bagi kami apabila Bapak/Ibu/Saudara/i berkenan hadir dan memberikan doa restu.
            </p>

            <div className="flex flex-wrap gap-4">
              <Button href="#hadiah" variant="secondary">
                Lanjut ke Kirim Hadiah
              </Button>
              <Button variant="secondary" onClick={resetRsvp}>
                Ubah Konfirmasi
              </Button>
            </div>
          </Card>
        </AnimatedSection>
      </div>
    </section>
  );
}
