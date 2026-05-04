interface SectionTagProps {
  children: string;
}

export function SectionTag({ children }: SectionTagProps) {
  return (
    <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">
      {children}
    </p>
  );
}
