import Image from "next/image"
import Link from "next/link"
import { Button } from "@/components/ui/button"

export function HeroSection() {
  return (
    <section className="relative h-[600px] w-full overflow-hidden lg:h-[700px]">
      <Image
        src="/images/hero-restaurant.jpg"
        alt="Ambiente elegante de restaurante"
        fill
        className="object-cover"
        priority
      />
      <div className="absolute inset-0 bg-foreground/50" />
      <div className="relative z-10 flex h-full flex-col items-center justify-center px-6 text-center">
        <p className="mb-4 text-sm font-medium uppercase tracking-[0.3em] text-primary-foreground/80">
          Bienvenido a KitchAI
        </p>
        <h1 className="max-w-3xl font-serif text-4xl font-bold leading-tight text-primary-foreground md:text-5xl lg:text-6xl text-balance">
          Descubre una Experiencia Gastronómica de Primera Clase
        </h1>
        <p className="mt-6 max-w-xl text-primary-foreground/80 leading-relaxed">
          Disfruta de una cocina excepcional en un ambiente sofisticado.
          Reserva tu mesa y vive una experiencia inolvidable.
        </p>
        <div className="mt-8 flex gap-4">
          <Button asChild size="lg" className="rounded-full bg-primary text-primary-foreground hover:bg-primary/90 px-8">
            <Link href="#reservar">Reservar Mesa</Link>
          </Button>
          <Button asChild size="lg" variant="outline" className="rounded-full border-primary-foreground/30 text-primary-foreground hover:bg-primary-foreground/10 px-8 bg-transparent">
            <Link href="#menu">Ver Menu</Link>
          </Button>
        </div>
      </div>
    </section>
  )
}
