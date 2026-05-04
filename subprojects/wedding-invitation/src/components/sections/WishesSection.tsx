import { useState } from 'react';
import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { WishCard } from '@/components/ui/WishCard';
import { useInvitationStore } from '@/store/useInvitationStore';

export function WishesSection() {
  const { wishes, addWish } = useInvitationStore();
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');
  const [errors, setErrors] = useState<{ name?: string; message?: string }>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newErrors: { name?: string; message?: string } = {};
    if (!name.trim()) newErrors.name = 'Mohon isi nama Anda.';
    if (!message.trim()) newErrors.message = 'Mohon isi ucapan Anda.';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    addWish({ name: name.trim(), message: message.trim() });
    setName('');
    setMessage('');
    setErrors({});
  };

  return (
    <section id="ucapan" className="py-10">
      <div className="container-main">
        <AnimatedSection>
          <Card className="max-w-[800px] mx-auto">
            <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Ucapan dan Doa</p>
            <h2 className="text-[clamp(1.8rem,3vw,2.8rem)]">Kirimkan ucapan dan doa restu</h2>
            <p className="text-brown-500 mt-4">
              Pesan dan doa tulus dari Bapak/Ibu/Saudara/i akan menjadi kebahagiaan tersendiri bagi kami.
            </p>

            <form onSubmit={handleSubmit} className="mt-8 grid gap-5">
              <div className="grid gap-2">
                <label htmlFor="wishName" className="text-[0.9rem] font-medium text-green-800">
                  Nama
                </label>
                <input
                  id="wishName"
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Nama Anda"
                  className="w-full py-3.5 px-4 rounded-[18px] border border-[rgba(120,86,55,0.16)] bg-[rgba(255,255,255,0.72)] font-inherit text-green-800 transition-all duration-180 focus:outline-none focus:border-bronze-500 focus:shadow-[0_0_0_3px_rgba(138,90,47,0.1)]"
                />
                {errors.name && <small className="text-[#a14e42] text-[0.8rem]">{errors.name}</small>}
              </div>

              <div className="grid gap-2">
                <label htmlFor="wishMessage" className="text-[0.9rem] font-medium text-green-800">
                  Ucapan
                </label>
                <textarea
                  id="wishMessage"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  rows={4}
                  placeholder="Tulis ucapan dan doa restu Anda..."
                  className="w-full py-3.5 px-4 rounded-[18px] border border-[rgba(120,86,55,0.16)] bg-[rgba(255,255,255,0.72)] font-inherit text-green-800 transition-all duration-180 focus:outline-none focus:border-bronze-500 focus:shadow-[0_0_0_3px_rgba(138,90,47,0.1)] resize-y"
                />
                {errors.message && <small className="text-[#a14e42] text-[0.8rem]">{errors.message}</small>}
              </div>

              <div>
                <Button type="submit">Kirim Ucapan</Button>
              </div>
            </form>
          </Card>
        </AnimatedSection>

        {wishes.length > 0 && (
          <AnimatedSection delay={0.2}>
            <div className="max-w-[800px] mx-auto mt-8 grid gap-4">
              {wishes.map((wish) => (
                <WishCard key={wish.id} wish={wish} />
              ))}
            </div>
          </AnimatedSection>
        )}
      </div>
    </section>
  );
}
