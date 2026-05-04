export type AttendanceChoice = 'hadir' | 'tidak-hadir' | 'ragu';

export interface RsvpFormData {
  guestName: string;
  attendance: AttendanceChoice;
  /** Number of guests including the named invitee when attending */
  guestCount: '0' | '1' | '2' | '3' | '4' | '5';
}

export interface RsvpSubmission {
  formData: RsvpFormData;
  submittedAt: string;
}

export interface GalleryImage {
  src: string;
  alt: string;
  caption?: string;
}

export interface ScheduleItemData {
  time: string;
  title: string;
  description: string;
}
