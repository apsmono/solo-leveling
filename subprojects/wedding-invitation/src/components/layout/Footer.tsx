import { BRIDE_NAME, GROOM_NAME } from '@/lib/constants';

export function Footer() {
  return (
    <footer className="text-center py-12 pb-16 text-brown-400 text-[0.95rem] max-w-[56rem] mx-auto px-8">
      <p className="leading-relaxed">
        Merupakan suatu kehormatan bagi kami apabila Bapak/Ibu/Saudara/i berkenan hadir dan memberikan doa restu.
      </p>
      <p className="mt-4 leading-relaxed">Terima kasih atas perhatian dan doa restunya.</p>
      <p className="font-serif text-[1.25rem] text-green-800 mt-6">
        {GROOM_NAME} &amp; {BRIDE_NAME}
      </p>
    </footer>
  );
}
