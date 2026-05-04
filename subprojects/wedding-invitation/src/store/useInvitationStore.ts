import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { RsvpFormData, RsvpSubmission } from '@/types';
import { OLD_RSVP_KEYS_TO_REMOVE } from '@/lib/constants';

/** Drop legacy persistence keys so old RSVP shapes do not collide */
function purgeLegacyKeys() {
  try {
    for (const key of OLD_RSVP_KEYS_TO_REMOVE) {
      localStorage.removeItem(key);
    }
    localStorage.removeItem('wedding-invitation.wishes-v2');
  } catch {
    // ignore
  }
}

purgeLegacyKeys();

interface InvitationState {
  guestName: string | null;
  setGuestName: (name: string) => void;

  isOpened: boolean;
  openInvitation: () => void;

  isMusicPlaying: boolean;
  toggleMusic: () => void;

  toastMessage: string | null;
  showToast: (message: string) => void;
  dismissToast: () => void;

  rsvpDraft: RsvpFormData | null;
  saveRsvpDraft: (data: RsvpFormData) => void;

  rsvpSubmission: RsvpSubmission | null;
  submitRsvp: (data: RsvpFormData) => void;
  resetRsvp: () => void;
}

export const useInvitationStore = create<InvitationState>()(
  persist(
    (set) => ({
      guestName: null,
      setGuestName: (name) => set({ guestName: name }),

      isOpened: false,
      openInvitation: () => set({ isOpened: true }),

      isMusicPlaying: false,
      toggleMusic: () => set((state) => ({ isMusicPlaying: !state.isMusicPlaying })),

      toastMessage: null,
      showToast: (message) => set({ toastMessage: message }),
      dismissToast: () => set({ toastMessage: null }),

      rsvpDraft: null,
      saveRsvpDraft: (data) => set({ rsvpDraft: data }),

      rsvpSubmission: null,
      submitRsvp: (data) =>
        set({
          rsvpSubmission: { formData: data, submittedAt: new Date().toISOString() },
          rsvpDraft: null,
        }),
      resetRsvp: () => set({ rsvpSubmission: null }),
    }),
    {
      name: 'wedding-invitation.v3',
      partialize: (state) => ({
        rsvpDraft: state.rsvpDraft,
        rsvpSubmission: state.rsvpSubmission,
      }),
    }
  )
);
