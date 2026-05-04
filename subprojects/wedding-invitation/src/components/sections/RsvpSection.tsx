import { useState, useEffect, useCallback } from 'react';
import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useInvitationStore } from '@/store/useInvitationStore';
import { defaultRsvpForm } from '@/lib/constants';
import type { RsvpFormData } from '@/types';

interface RsvpErrors {
  guestName?: string;
  email?: string;
}

export function RsvpSection() {
  const { guestName, rsvpDraft, rsvpSubmission, saveRsvpDraft, submitRsvp } = useInvitationStore();
  const [formData, setFormData] = useState<RsvpFormData>(defaultRsvpForm);
  const [errors, setErrors] = useState<RsvpErrors>({});

  // Initialize from draft or pre-fill guest name
  useEffect(() => {
    const initial = rsvpDraft || defaultRsvpForm;
    setFormData({
      ...initial,
      guestName: initial.guestName || guestName || '',
    });
  }, [rsvpDraft, guestName]);

  // Auto-save draft
  useEffect(() => {
    if (!rsvpSubmission) {
      const timeout = setTimeout(() => {
        saveRsvpDraft(formData);
      }, 500);
      return () => clearTimeout(timeout);
    }
  }, [formData, rsvpSubmission, saveRsvpDraft]);

  const updateField = useCallback(<K extends keyof RsvpFormData>(field: K, value: RsvpFormData[K]) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setErrors((prev) => ({ ...prev, [field]: undefined }));
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: RsvpErrors = {};
    if (!formData.guestName.trim()) newErrors.guestName = 'Mohon isi nama lengkap Anda.';
    if (!formData.email.trim() || !formData.email.includes('@')) {
      newErrors.email = 'Mohon isi alamat email yang valid.';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Normalize guest count if declining
    const data = { ...formData };
    if (data.attendance === 'regretfully-declines') {
      data.guestCount = '0';
    }

    submitRsvp(data);
  };

  if (rsvpSubmission) return null;

  return (
    <section id="rsvp" className="py-10">
      <div className="container-main">
        <AnimatedSection>
          <Card className="max-w-[800px] mx-auto">
            <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">
              Konfirmasi Kehadiran
            </p>
            <h2 className="text-[clamp(1.8rem,3vw,2.8rem)]">Mohon konfirmasi kehadiran</h2>
            <p className="text-brown-500 mt-4">
              Kami memohon kesediaan Bapak/Ibu/Saudara/i untuk mengisi konfirmasi kehadiran
              melalui formulir berikut. Data konfirmasi akan tersimpan di perangkat ini.
            </p>

            <form onSubmit={handleSubmit} className="mt-8 grid md:grid-cols-2 gap-6 text-left">
              <div className="grid gap-2">
                <label htmlFor="guestName" className="text-[0.9rem] font-medium text-green-800">
                  Nama Tamu
                </label>
                <input
                  id="guestName"
                  type="text"
                  value={formData.guestName}
                  onChange={(e) => updateField('guestName', e.target.value)}
                  placeholder="Nama lengkap Anda"
                  className="w-full py-3.5 px-4 rounded-[18px] border border-[rgba(120,86,55,0.16)] bg-[rgba(255,255,255,0.72)] font-inherit text-green-800 transition-all duration-180 focus:outline-none focus:border-bronze-500 focus:shadow-[0_0_0_3px_rgba(138,90,47,0.1)]"
                />
                {errors.guestName && <small className="text-[#a14e42] text-[0.8rem]">{errors.guestName}</small>}
              </div>

              <div className="grid gap-2">
                <label htmlFor="email" className="text-[0.9rem] font-medium text-green-800">
                  Alamat Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => updateField('email', e.target.value)}
                  placeholder="email@contoh.com"
                  className="w-full py-3.5 px-4 rounded-[18px] border border-[rgba(120,86,55,0.16)] bg-[rgba(255,255,255,0.72)] font-inherit text-green-800 transition-all duration-180 focus:outline-none focus:border-bronze-500 focus:shadow-[0_0_0_3px_rgba(138,90,47,0.1)]"
                />
                {errors.email && <small className="text-[#a14e42] text-[0.8rem]">{errors.email}</small>}
              </div>

              <div className="grid gap-2">
                <label htmlFor="attendance" className="text-[0.9rem] font-medium text-green-800">
                  Kehadiran
                </label>
                <select
                  id="attendance"
                  value={formData.attendance}
                  onChange={(e) => updateField('attendance', e.target.value as RsvpFormData['attendance'])}
                  className="w-full py-3.5 px-4 rounded-[18px] border border-[rgba(120,86,55,0.16)] bg-[rgba(255,255,255,0.72)] font-inherit text-green-800 transition-all duration-180 focus:outline-none focus:border-bronze-500 focus:shadow-[0_0_0_3px_rgba(138,90,47,0.1)] appearance-none"
                >
                  <option value="joyfully-accepts">InsyaAllah hadir</option>
                  <option value="regretfully-declines">Dengan hormat berhalangan hadir</option>
                </select>
              </div>

              <div className="grid gap-2">
                <label htmlFor="guestCount" className="text-[0.9rem] font-medium text-green-800">
                  Jumlah Tamu
                </label>
                <select
                  id="guestCount"
                  value={formData.guestCount}
                  onChange={(e) => updateField('guestCount', e.target.value as RsvpFormData['guestCount'])}
                  className="w-full py-3.5 px-4 rounded-[18px] border border-[rgba(120,86,55,0.16)] bg-[rgba(255,255,255,0.72)] font-inherit text-green-800 transition-all duration-180 focus:outline-none focus:border-bronze-500 focus:shadow-[0_0_0_3px_rgba(138,90,47,0.1)] appearance-none"
                >
                  <option value="1">1</option>
                  <option value="2">2</option>
                  <option value="3">3</option>
                  <option value="4">4</option>
                </select>
              </div>

              <div className="grid gap-2">
                <label htmlFor="mealPreference" className="text-[0.9rem] font-medium text-green-800">
                  Pilihan Menu
                </label>
                <select
                  id="mealPreference"
                  value={formData.mealPreference}
                  onChange={(e) => updateField('mealPreference', e.target.value as RsvpFormData['mealPreference'])}
                  className="w-full py-3.5 px-4 rounded-[18px] border border-[rgba(120,86,55,0.16)] bg-[rgba(255,255,255,0.72)] font-inherit text-green-800 transition-all duration-180 focus:outline-none focus:border-bronze-500 focus:shadow-[0_0_0_3px_rgba(138,90,47,0.1)] appearance-none"
                >
                  <option value="chef-selection">Menu pilihan panitia</option>
                  <option value="vegetarian">Menu vegetarian</option>
                  <option value="vegan">Menu vegan</option>
                </select>
              </div>

              <div className="grid gap-2">
                <label htmlFor="songRequest" className="text-[0.9rem] font-medium text-green-800">
                  Permintaan Lagu
                </label>
                <input
                  id="songRequest"
                  type="text"
                  value={formData.songRequest}
                  onChange={(e) => updateField('songRequest', e.target.value)}
                  placeholder="Judul lagu dan artis"
                  className="w-full py-3.5 px-4 rounded-[18px] border border-[rgba(120,86,55,0.16)] bg-[rgba(255,255,255,0.72)] font-inherit text-green-800 transition-all duration-180 focus:outline-none focus:border-bronze-500 focus:shadow-[0_0_0_3px_rgba(138,90,47,0.1)]"
                />
              </div>

              <div className="grid gap-2 md:col-span-2">
                <label htmlFor="dietaryNotes" className="text-[0.9rem] font-medium text-green-800">
                  Catatan Makanan
                </label>
                <textarea
                  id="dietaryNotes"
                  value={formData.dietaryNotes}
                  onChange={(e) => updateField('dietaryNotes', e.target.value)}
                  rows={4}
                  placeholder="Alergi atau kebutuhan khusus lainnya"
                  className="w-full py-3.5 px-4 rounded-[18px] border border-[rgba(120,86,55,0.16)] bg-[rgba(255,255,255,0.72)] font-inherit text-green-800 transition-all duration-180 focus:outline-none focus:border-bronze-500 focus:shadow-[0_0_0_3px_rgba(138,90,47,0.1)] resize-y"
                />
              </div>

              <div className="flex flex-wrap gap-4 mt-4 md:col-span-2">
                <Button type="submit">Lanjut ke Ringkasan</Button>
                <Button variant="secondary" href="mailto:?subject=Pertanyaan%20Undangan">
                  Ajukan Pertanyaan
                </Button>
              </div>
            </form>
          </Card>
        </AnimatedSection>
      </div>
    </section>
  );
}
