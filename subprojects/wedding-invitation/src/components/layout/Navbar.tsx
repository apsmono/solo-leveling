import { useState, useEffect, useMemo } from 'react';
import { useScrollSpy } from '@/hooks/useScrollSpy';
import { useInvitationStore } from '@/store/useInvitationStore';
import { cn } from '@/lib/utils';
import { BRIDE_NAME, GROOM_NAME } from '@/lib/constants';
import { Menu, X } from 'lucide-react';

const navLinks = [
  { href: '#beranda', label: 'Beranda' },
  { href: '#ayatsuci', label: 'Ayat Suci' },
  { href: '#acara', label: 'Acara' },
  { href: '#kisah', label: 'Kisah' },
  { href: '#galeri', label: 'Galeri' },
  { href: '#lokasi', label: 'Lokasi' },
  { href: '#rsvp', label: 'Konfirmasi' },
  { href: '#hadiah', label: 'Hadiah' },
] as const;

const sectionIds = ['beranda', 'ayatsuci', 'acara', 'kisah', 'galeri', 'lokasi', 'rsvp', 'hadiah'];

export function Navbar() {
  const { isOpened } = useInvitationStore();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const stableIds = useMemo(() => [...sectionIds], []);
  const activeId = useScrollSpy(stableIds, 120);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  if (!isOpened) return null;

  return (
    <nav
      className={cn(
        'sticky top-0 z-40 bg-[rgba(255,251,244,0.85)] backdrop-blur-md border-b border-[rgba(103,75,47,0.12)] transition-shadow duration-200',
        scrolled && 'shadow-[0_2px_12px_rgba(55,41,24,0.08)]'
      )}
    >
      <div className="container-main flex items-center justify-between h-16">
        <a href="#beranda" className="font-serif font-semibold text-[1.05rem] text-green-800 truncate max-w-[11rem] sm:max-w-none">
          {GROOM_NAME} &amp; {BRIDE_NAME}
        </a>

        <ul className="hidden lg:flex items-center gap-3 list-none flex-wrap justify-end max-w-[52%] 2xl:max-w-none">
          {navLinks.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                className={cn(
                  'text-[0.78rem] font-medium py-2 transition-colors duration-180 whitespace-nowrap',
                  activeId === link.href.slice(1) ? 'text-bronze-500' : 'text-brown-600 hover:text-bronze-500'
                )}
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        <button
          type="button"
          onClick={() => setMobileOpen(!mobileOpen)}
          className="lg:hidden flex flex-col gap-1 bg-transparent border-none cursor-pointer p-2"
          aria-label={mobileOpen ? 'Tutup menu' : 'Buka menu'}
        >
          {mobileOpen ? <X className="w-6 h-6 text-green-800" /> : <Menu className="w-6 h-6 text-green-800" />}
        </button>
      </div>

      {mobileOpen && (
        <div className="lg:hidden absolute top-16 left-0 right-0 bg-[rgba(255,251,244,0.96)] backdrop-blur-md border-b border-[rgba(103,75,47,0.12)] p-6 max-h-[min(70vh,calc(100dvh-4rem))] overflow-y-auto">
          <ul className="flex flex-col gap-3 list-none">
            {navLinks.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className={cn(
                    'text-[0.95rem] font-medium block py-2 transition-colors',
                    activeId === link.href.slice(1) ? 'text-bronze-500' : 'text-brown-600 hover:text-bronze-500'
                  )}
                >
                  {link.label}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </nav>
  );
}
