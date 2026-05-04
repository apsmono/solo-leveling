import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { RsvpFormData, RsvpSubmission, Wish } from '@/types';
import {
  RSVP_DRAFT_KEY,
  RSVP_SUBMITTED_KEY,
  OLD_RSVP_DRAFT_KEY,
  OLD_RSVP_SUBMITTED_KEY,
  defaultRsvpForm,
} from '@/lib/constants';

function migrateOldData() {
  try {
    const oldDraft = localStorage.getItem(OLD_RSVP_DRAFT_KEY);
    const oldSubmitted = localStorage.getItem(OLD_RSVP_SUBMITTED_KEY);

    if (oldDraft && !localStorage.getItem(RSVP_DRAFT_KEY)) {
      const parsed = JSON.parse(oldDraft);
      localStorage.setItem(RSVP_DRAFT_KEY, JSON.stringify({ ...defaultRsvpForm, ...parsed }));
    }
    if (oldSubmitted && !localStorage.getItem(RSVP_SUBMITTED_KEY)) {
      const parsed = JSON.parse(oldSubmitted);
      localStorage.setItem(
        RSVP_SUBMITTED_KEY,
        JSON.stringify({
          formData: { ...defaultRsvpForm, ...(parsed.formData || parsed) },
          submittedAt: new Date().toISOString(),
        })
      );
    }

    localStorage.removeItem(OLD_RSVP_DRAFT_KEY);
    localStorage.removeItem(OLD_RSVP_SUBMITTED_KEY);
  } catch {
    // silently ignore migration errors
  }
}

migrateOldData();

interface InvitationState {
  guestName: string | null;
  setGuestName: (name: string) => void;

  isOpened: boolean;
  openInvitation: () => void;

  isMusicPlaying: boolean;
  toggleMusic: () => void;

  rsvpDraft: RsvpFormData | null;
  saveRsvpDraft: (data: RsvpFormData) => void;

  rsvpSubmission: RsvpSubmission | null;
  submitRsvp: (data: RsvpFormData) => void;
  resetRsvp: () => void;

  wishes: Wish[];
  addWish: (wish: Omit<Wish, 'id' | 'createdAt'>) => void;
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

      rsvpDraft: null,
      saveRsvpDraft: (data) => set({ rsvpDraft: data }),

      rsvpSubmission: null,
      submitRsvp: (data) =>
        set({
          rsvpSubmission: { formData: data, submittedAt: new Date().toISOString() },
          rsvpDraft: null,
        }),
      resetRsvp: () => set({ rsvpSubmission: null }),

      wishes: [],
      addWish: (wish) =>
        set((state) => ({
          wishes: [
            {
              ...wish,
              id: `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
              createdAt: new Date().toISOString(),
            },
            ...state.wishes,
          ],
        })),
    }),
    {
      name: 'wedding-invitation.store',
      partialize: (state) => ({
        rsvpDraft: state.rsvpDraft,
        rsvpSubmission: state.rsvpSubmission,
        wishes: state.wishes,
      }),
    }
  )
);
