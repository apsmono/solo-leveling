import { useState, useEffect } from 'react';
import { useScrollSpy } from '@/hooks/useScrollSpy';
import { useInvitationStore } from '@/store/useInvitationStore';
import { cn } from '@/lib/utils';
import { Menu, X } from 'lucide-react';

const navLinks = [
  { href: '#beranda', label: 'Beranda' },
  { href: '#kisah', label: 'Kisah' },
  { href: '#acara', label: 'Acara' },
  { href: '#galeri', label: 'Galeri' },
  { href: '#panduan', label: 'Panduan' },
  { href: '#rsvp', label: 'RSVP' },
  { href: '#ucapan', label: 'Ucapan' },
];

const sectionIds = ['beranda', 'kisah', 'acara', 'galeri', 'panduan', 'rsvp', 'ucapan'];

export function Navbar() {
  const { isOpened } = useInvitationStore();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const activeId = useScrollSpy(sectionIds, 120);

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
        <a href="#beranda" className="font-serif font-semibold text-[1.1rem] text-green-800">
          Amalia &amp; Arif
        </a>

        {/* Desktop nav */}
        <ul className="hidden lg:flex items-center gap-6 list-none">
          {navLinks.map((link) => (
            <li key={link.href}>
              <a
                href={link.href}
                onClick={() => setMobileOpen(false)}
                className={cn(
                  'text-[0.9rem] font-medium py-2 transition-colors duration-180',
                  activeId === link.href.slice(1)
                    ? 'text-bronze-500'
                    : 'text-brown-600 hover:text-bronze-500'
                )}
              >
                {link.label}
              </a>
            </li>
          ))}
        </ul>

        {/* Mobile toggle */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="lg:hidden flex flex-col gap-1 bg-none border-none cursor-pointer p-2"
          aria-label={mobileOpen ? 'Tutup menu' : 'Buka menu'}
        >
          {mobileOpen ? (
            <X className="w-6 h-6 text-green-800" />
          ) : (
            <Menu className="w-6 h-6 text-green-800" />
          )}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="lg:hidden absolute top-16 left-0 right-0 bg-[rgba(255,251,244,0.95)] backdrop-blur-md border-b border-[rgba(103,75,47,0.12)] p-6">
          <ul className="flex flex-col gap-4 list-none">
            {navLinks.map((link) => (
              <li key={link.href}>
                <a
                  href={link.href}
                  onClick={() => setMobileOpen(false)}
                  className={cn(
                    'text-[0.95rem] font-medium block py-1 transition-colors',
                    activeId === link.href.slice(1)
                      ? 'text-bronze-500'
                      : 'text-brown-600 hover:text-bronze-500'
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
