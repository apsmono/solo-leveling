import { AnimatedSection } from '@/components/ui/AnimatedSection';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

export function GuestGuideSection() {
  return (
    <section id="panduan" className="py-10">
      <div className="container-main">
        <div className="grid lg:grid-cols-2 gap-8">
          <AnimatedSection>
            <Card>
              <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Panduan Tamu</p>
              <h2 className="text-[clamp(1.8rem,3vw,2.8rem)]">Panduan kehadiran dan informasi lokasi</h2>
              <p className="text-brown-500 mt-4 max-w-[42rem]">
                Seluruh informasi yang dibutuhkan tamu sebelum hari acara akan kami rangkum di sini.
                Detail lokasi, perjalanan, dan akomodasi dapat diperbarui begitu susunan akhir telah dipastikan.
              </p>
              <Button href="#" className="mt-6 inline-flex" variant="secondary">
                Buka Peta
              </Button>
              <div className="grid lg:grid-cols-3 gap-4 mt-6">
                <article className="p-4 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)]">
                  <h3 className="text-[1rem] mb-4">Kedatangan</h3>
                  <ul className="list-none grid gap-4">
                    <li className="relative pl-[18px] text-brown-500 text-[0.9rem]">
                      <span className="absolute left-0 top-[0.55em] w-[6px] h-[6px] rounded-full bg-bronze-400" />
                      Kami mohon tamu hadir sekitar 30 menit sebelum acara dimulai.
                    </li>
                    <li className="relative pl-[18px] text-brown-500 text-[0.9rem]">
                      <span className="absolute left-0 top-[0.55em] w-[6px] h-[6px] rounded-full bg-bronze-400" />
                      Informasi area parkir dan titik turun tamu akan dibagikan setelah detail venue final ditetapkan.
                    </li>
                  </ul>
                </article>
                <article className="p-4 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)]">
                  <h3 className="text-[1rem] mb-4">Akomodasi</h3>
                  <ul className="list-none grid gap-4">
                    <li className="relative pl-[18px] text-brown-500 text-[0.9rem]">
                      <span className="absolute left-0 top-[0.55em] w-[6px] h-[6px] rounded-full bg-bronze-400" />
                      Silakan memilih penginapan di sekitar area venue setelah lokasi diumumkan secara resmi.
                    </li>
                    <li className="relative pl-[18px] text-brown-500 text-[0.9rem]">
                      <span className="absolute left-0 top-[0.55em] w-[6px] h-[6px] rounded-full bg-bronze-400" />
                      Rekomendasi hotel atau penginapan keluarga dapat kami tambahkan untuk tamu dari luar kota.
                    </li>
                  </ul>
                </article>
                <article className="p-4 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)]">
                  <h3 className="text-[1rem] mb-4">Transportasi</h3>
                  <ul className="list-none grid gap-4">
                    <li className="relative pl-[18px] text-brown-500 text-[0.9rem]">
                      <span className="absolute left-0 top-[0.55em] w-[6px] h-[6px] rounded-full bg-bronze-400" />
                      Mohon menyiapkan transportasi pulang atau layanan perjalanan daring sesuai kebutuhan masing-masing.
                    </li>
                    <li className="relative pl-[18px] text-brown-500 text-[0.9rem]">
                      <span className="absolute left-0 top-[0.55em] w-[6px] h-[6px] rounded-full bg-bronze-400" />
                      Catatan cuaca, alas kaki, atau kebutuhan khusus lainnya akan kami perbarui setelah lokasi dipastikan.
                    </li>
                  </ul>
                </article>
              </div>
            </Card>
          </AnimatedSection>

          <AnimatedSection delay={0.2}>
            <Card>
              <p className="uppercase tracking-[0.22em] text-[0.74rem] text-brown-400 mb-4">Doa dan Tanda Kasih</p>
              <h2 className="text-[clamp(1.8rem,3vw,2.8rem)]">Kehadiran dan doa restu sudah sangat berarti</h2>
              <p className="text-brown-500 mt-4 max-w-[42rem]">
                Bagi kami, kehadiran dan doa restu Bapak/Ibu/Saudara/i merupakan anugerah yang paling berharga.
                Apabila berkenan memberikan tanda kasih, keterangan berikut dapat menjadi panduan.
              </p>
              <div className="grid lg:grid-cols-3 gap-4 mt-6">
                <article className="p-4 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)]">
                  <h3 className="text-[1rem] mb-4">Dana Rumah Tangga</h3>
                  <p className="text-brown-500 text-[0.9rem]">
                    Pilihan sederhana untuk mendukung awal rumah tangga yang sedang kami rintis bersama.
                  </p>
                </article>
                <article className="p-4 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)]">
                  <h3 className="text-[1rem] mb-4">Perjalanan Syukur</h3>
                  <p className="text-brown-500 text-[0.9rem]">
                    Pilihan tanda kasih yang dapat mendukung perjalanan pertama kami sebagai suami dan istri.
                  </p>
                </article>
                <article className="p-4 rounded-[20px] bg-[rgba(255,252,248,0.66)] border border-[rgba(120,86,55,0.12)]">
                  <h3 className="text-[1rem] mb-4">Titip Doa</h3>
                  <p className="text-brown-500 text-[0.9rem]">
                    Doa tulus dan pesan baik dari panjenengan akan selalu kami simpan dengan penuh syukur.
                  </p>
                </article>
              </div>
            </Card>
          </AnimatedSection>
        </div>
      </div>
    </section>
  );
}
