export interface RsvpFormData {
  guestName: string;
  email: string;
  attendance: 'joyfully-accepts' | 'regretfully-declines';
  guestCount: '0' | '1' | '2' | '3' | '4';
  mealPreference: 'chef-selection' | 'vegetarian' | 'vegan';
  dietaryNotes: string;
  songRequest: string;
}

export interface RsvpSubmission {
  formData: RsvpFormData;
  submittedAt: string;
}

export interface Wish {
  id: string;
  name: string;
  message: string;
  createdAt: string;
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

export interface GuideItemData {
  title: string;
  items: string[];
}

export interface RegistryItemData {
  title: string;
  description: string;
}
