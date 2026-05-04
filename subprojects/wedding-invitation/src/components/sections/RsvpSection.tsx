import { useState, useEffect, useCallback } from 'react';
import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useInvitationStore } from '@/store/useInvitationStore';
import { defaultRsvpForm, WHATSAPP_RSVP_E164 } from '@/lib/constants';
import type { RsvpFormData } from '@/types';
import { buildRsvpWhatsAppBody, whatsappRsvpUrl } from '@/lib/rsvpWhatsApp';

interface RsvpErrors {
  guestName?: string;
}

export function RsvpSection() {
  const { guestName, rsvpDraft, rsvpSubmission, saveRsvpDraft, submitRsvp, showToast } =
    useInvitationStore();
  const [formData, setFormData] = useState<RsvpFormData>(defaultRsvpForm);
  const [errors, setErrors] = useState<RsvpErrors>({});

  useEffect(() => {
    const initial = rsvpDraft || defaultRsvpForm;
    setFormData({
      ...initial,
      guestName: initial.guestName || guestName || '',
    });
  }, [rsvpDraft, guestName]);

  /** Keep guest count consistent with attendance choice */
  useEffect(() => {
    setFormData((prev) => {
      if (prev.attendance === 'tidak-hadir' && prev.guestCount !== '0') {
        return { ...prev, guestCount: '0' };
      }
      if (prev.attendance !== 'tidak-hadir' && prev.guestCount === '0') {
        return { ...prev, guestCount: '1' };
      }
      return prev;
    });
  }, [formData.attendance]);

  useEffect(() => {
    if (!rsvpSubmission) {
      const timeout = setTimeout(() => {
        saveRsvpDraft(formData);
      }, 400);
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
    if (!formData.guestName.trim()) newErrors.guestName = 'Mohon lengkapi data terlebih dahulu';

    const adjusted: RsvpFormData = {
      ...formData,
      guestCount: formData.attendance === 'tidak-hadir' ? '0' : formData.guestCount,
    };

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      showToast('Mohon lengkapi data terlebih dahulu');
      return;
    }

    const wa = WHATSAPP_RSVP_E164.replace(/\D/g, '');
    if (!wa || wa.length < 10) {
      showToast('Nomor WhatsApp panitia belum diatur. Hubungi pengundang secara langsung.');
      return;
    }

    const body = buildRsvpWhatsAppBody(adjusted);
    const url = whatsappRsvpUrl(wa, body);
    window.open(url, '_blank', 'noopener,noreferrer');

    submitRsvp(adjusted);
    showToast('Konfirmasi berhasil dikirim. Terima kasih!');
  };

  if (rsvpSubmission) return null;

  return (
    <section id="rsvp" className="py-10 scroll-mt-[var(--nav-offset,5rem)]">
      <div className="container-main">
        <AnimatedSection>
          <Card className="max-w-[560px] mx-auto">
            <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4 text-center">
              Konfirmasi Kehadiran
            </p>
            <h2 className="text-[clamp(1.8rem,3vw,2.6rem)] text-center mb-4">Mohon konfirmasi kehadiran</h2>
            <p className="text-brown-500 text-center text-[0.95rem] mb-8">
              Formulir ini akan membuka WhatsApp dengan pesan yang sudah terisi. Pastikan WhatsApp terpasang di
              perangkat Anda.
            </p>

            <form onSubmit={handleSubmit} className="grid gap-6 text-left">
              <div className="grid gap-2">
                <label htmlFor="guestName" className="text-[0.9rem] font-medium text-green-800">
                  Nama
                </label>
                <input
                  id="guestName"
                  type="text"
                  value={formData.guestName}
                  onChange={(e) => updateField('guestName', e.target.value)}
                  placeholder="Nama lengkap Anda"
                  autoComplete="name"
                  className="w-full py-3.5 px-4 rounded-[18px] border border-[rgba(120,86,55,0.16)] bg-[rgba(255,255,255,0.72)] font-inherit text-green-800 transition-all duration-180 focus:outline-none focus:border-bronze-500 focus:shadow-[0_0_0_3px_rgba(138,90,47,0.1)]"
                />
                {errors.guestName && <small className="text-[#a14e42] text-[0.8rem]">{errors.guestName}</small>}
              </div>

              <div className="grid gap-2">
                <label htmlFor="attendance" className="text-[0.9rem] font-medium text-green-800">
                  Kehadiran
                </label>
                <select
                  id="attendance"
                  value={formData.attendance}
                  onChange={(e) =>
                    updateField('attendance', e.target.value as RsvpFormData['attendance'])
                  }
                  className="w-full py-3.5 px-4 rounded-[18px] border border-[rgba(120,86,55,0.16)] bg-[rgba(255,255,255,0.72)] font-inherit text-green-800 transition-all duration-180 focus:outline-none focus:border-bronze-500 focus:shadow-[0_0_0_3px_rgba(138,90,47,0.1)] appearance-none"
                >
                  <option value="hadir">Hadir</option>
                  <option value="tidak-hadir">Tidak Hadir</option>
                  <option value="ragu">Masih Ragu</option>
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
                  {formData.attendance === 'tidak-hadir' ? (
                    <option value="0">0</option>
                  ) : (
                    <>
                      <option value="1">1</option>
                      <option value="2">2</option>
                      <option value="3">3</option>
                      <option value="4">4</option>
                      <option value="5">5</option>
                    </>
                  )}
                </select>
              </div>

              <div className="pt-2">
                <Button type="submit" className="w-full justify-center">
                  Kirim Konfirmasi
                </Button>
              </div>
            </form>
          </Card>
        </AnimatedSection>
      </div>
    </section>
  );
}
