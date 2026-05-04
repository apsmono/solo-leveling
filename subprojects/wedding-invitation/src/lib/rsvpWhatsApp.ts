import type { RsvpFormData } from '@/types';
import { attendanceLabels, BRIDE_NAME, GROOM_NAME } from '@/lib/constants';

/** Builds the Indonesian RSVP body sent via WhatsApp wa.me */
export function buildRsvpWhatsAppBody(data: RsvpFormData): string {
  const kehadiran = attendanceLabels[data.attendance] ?? data.attendance;
  return [
    'Assalamu’alaikum warahmatullahi wabarakatuh,',
    '',
    `Berikut konfirmasi kehadiran untuk pernikahan ${GROOM_NAME} & ${BRIDE_NAME}:`,
    '',
    `Nama: ${data.guestName}`,
    `Kehadiran: ${kehadiran}`,
    `Jumlah tamu: ${data.guestCount}`,
    '',
    'Terima kasih.',
  ].join('\n');
}

export function whatsappRsvpUrl(phoneE164: string, body: string): string {
  const trimmed = phoneE164.replace(/\D/g, '');
  return `https://wa.me/${trimmed}?text=${encodeURIComponent(body)}`;
}
