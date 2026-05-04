import type { Wish } from '@/types';

interface WishCardProps {
  wish: Wish;
}

export function WishCard({ wish }: WishCardProps) {
  const date = new Date(wish.createdAt).toLocaleDateString('id-ID', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });

  return (
    <article className="p-5 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)]">
      <div className="flex items-center justify-between mb-3">
        <h4 className="font-serif font-semibold text-green-800">{wish.name}</h4>
        <span className="text-[0.75rem] text-brown-400">{date}</span>
      </div>
      <p className="text-brown-500 text-[0.95rem] leading-relaxed">{wish.message}</p>
    </article>
  );
}
