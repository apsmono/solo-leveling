import type { RsvpFormData } from '@/types';

export const WEDDING_DATE = new Date('2026-06-01T00:00:00+07:00');

export const RSVP_DRAFT_KEY = 'wedding-invitation.rsvp-draft-v2';
export const RSVP_SUBMITTED_KEY = 'wedding-invitation.rsvp-submitted-v2';
export const WISHES_KEY = 'wedding-invitation.wishes-v2';

// Old keys for migration
export const OLD_RSVP_DRAFT_KEY = 'wedding-invitation.rsvp-draft';
export const OLD_RSVP_SUBMITTED_KEY = 'wedding-invitation.rsvp-submitted';

export const defaultRsvpForm: RsvpFormData = {
  guestName: '',
  email: '',
  attendance: 'joyfully-accepts',
  guestCount: '1',
  mealPreference: 'chef-selection',
  dietaryNotes: '',
  songRequest: '',
};

export const attendanceLabels: Record<string, string> = {
  'joyfully-accepts': 'InsyaAllah hadir',
  'regretfully-declines': 'Dengan hormat berhalangan hadir',
};

export const mealLabels: Record<string, string> = {
  'chef-selection': 'Menu pilihan panitia',
  vegetarian: 'Menu vegetarian',
  vegan: 'Menu vegan',
};

export const scheduleItems = [
  {
    time: '3:30 PM',
    title: 'Kedatangan Tamu',
    description: 'Penerimaan tamu dan penyambutan keluarga dimulai dengan suasana yang tenang dan tertata.',
  },
  {
    time: '4:30 PM',
    title: 'Akad dan Doa Bersama',
    description: 'Momen inti acara akan dilangsungkan secara khidmat bersama keluarga, kerabat, dan sahabat terdekat.',
  },
  {
    time: '6:00 PM',
    title: 'Jamuan dan Silaturahmi',
    description: 'Setelah prosesi utama, tamu dipersilakan menikmati jamuan sambil bersilaturahmi bersama keluarga besar.',
  },
  {
    time: '8:00 PM',
    title: 'Penutup Acara',
    description: 'Acara ditutup dengan suasana santai, ucapan syukur, dan kebersamaan yang hangat.',
  },
];

export const galleryImages = [
  {
    src: '/images/gallery/photo1.jpg',
    alt: 'Langkah Pertama Bersama',
    caption: 'Perjalanan sederhana yang kemudian menjadi kebiasaan manis yang selalu kami rindukan.',
  },
  {
    src: '/images/gallery/photo2.jpg',
    alt: 'Niat yang Dimantapkan',
    caption: 'Sebuah momen yang menguatkan niat, disertai doa dan harapan untuk masa depan yang baik.',
  },
  {
    src: '/images/gallery/photo3.jpg',
    alt: 'Ruang Cerita Kami',
    caption: 'Sudut sederhana tempat banyak rencana baik kami mulai dibicarakan dengan tenang.',
  },
];
