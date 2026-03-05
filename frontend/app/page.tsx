import { NavbarPublic } from "@/components/public/navbar"
import { HeroSection } from "@/components/public/hero-section"
import { PressSection } from "@/components/public/press-section"
import { MenuSection } from "@/components/public/menu-section"
import { ReservationSection } from "@/components/public/reservation-section"
import { ContactSection } from "@/components/public/contact-section"
import { Footer } from "@/components/public/footer"

export default function Page() {
  return (
    <main>
      <NavbarPublic />
      <HeroSection />
      <PressSection />
      <MenuSection />
      <ReservationSection />
      <ContactSection />
      <Footer />
    </main>
  )
}
