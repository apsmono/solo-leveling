import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useInvitationStore } from '@/store/useInvitationStore';
import { attendanceLabels, mealLabels } from '@/lib/constants';
import { escapeHtml } from '@/lib/utils';

export function ThanksSection() {
  const { rsvpSubmission, resetRsvp } = useInvitationStore();

  if (!rsvpSubmission) return null;

  const { formData } = rsvpSubmission;

  const summaryItems = [
    { label: 'Nama', value: formData.guestName },
    { label: 'Email', value: formData.email },
    { label: 'Kehadiran', value: attendanceLabels[formData.attendance] || formData.attendance },
    { label: 'Jumlah Tamu', value: formData.guestCount },
    { label: 'Menu', value: mealLabels[formData.mealPreference] || formData.mealPreference },
    { label: 'Catatan Makanan', value: formData.dietaryNotes || 'Tidak ada catatan' },
    { label: 'Permintaan Lagu', value: formData.songRequest || 'Tidak ada' },
  ];

  return (
    <section id="thanks" className="py-10">
      <div className="container-main">
        <AnimatedSection>
          <Card className="max-w-[800px] mx-auto">
            <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Ringkasan</p>
            <h2 className="text-[clamp(1.8rem,3vw,2.8rem)]">Terima kasih atas konfirmasinya</h2>
            <p className="text-brown-500 mt-4">
              Ringkasan konfirmasi Anda telah tersimpan di perangkat ini.
            </p>

            <div className="grid md:grid-cols-3 gap-4 my-8">
              {summaryItems.map((item) => (
                <article
                  key={item.label}
                  className="py-4 px-6 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)] grid gap-2"
                >
                  <span className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400">
                    {item.label}
                  </span>
                  <strong
                    className="text-green-800 font-medium"
                    dangerouslySetInnerHTML={{ __html: escapeHtml(item.value) }}
                  />
                </article>
              ))}
            </div>

            <div className="flex flex-wrap gap-4">
              <Button href="#panduan">Lanjut ke Panduan Tamu</Button>
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
