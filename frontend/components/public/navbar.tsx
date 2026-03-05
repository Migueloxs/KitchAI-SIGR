"use client"

import Link from "next/link"
import { useState } from "react"
import { Menu, X, ChefHat } from "lucide-react"
import { Button } from "@/components/ui/button"

export function NavbarPublic() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-card/90 backdrop-blur-md border-b border-border">
      <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          <ChefHat className="h-7 w-7 text-primary" />
          <span className="text-xl font-serif font-bold text-foreground">KitchAI</span>
        </Link>

        <div className="hidden items-center gap-8 md:flex">
          <Link href="/" className="text-sm font-medium text-foreground hover:text-primary transition-colors">
            Inicio
          </Link>
          <Link href="#menu" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
            Menu
          </Link>
          <Link href="#reservar" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
            Reservar
          </Link>
          <Link href="#contacto" className="text-sm font-medium text-muted-foreground hover:text-primary transition-colors">
            Contacto
          </Link>
        </div>

        <div className="hidden md:block">
          <Button asChild className="rounded-full bg-primary text-primary-foreground hover:bg-primary/90 px-6">
            <Link href="/login">Reservar Ahora</Link>
          </Button>
        </div>

        <button
          type="button"
          className="md:hidden text-foreground"
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle menu"
        >
          {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </nav>

      {isOpen && (
        <div className="border-t border-border bg-card px-6 py-4 md:hidden">
          <div className="flex flex-col gap-4">
            <Link href="/" className="text-sm font-medium text-foreground" onClick={() => setIsOpen(false)}>
              Inicio
            </Link>
            <Link href="#menu" className="text-sm font-medium text-muted-foreground" onClick={() => setIsOpen(false)}>
              Menu
            </Link>
            <Link href="#reservar" className="text-sm font-medium text-muted-foreground" onClick={() => setIsOpen(false)}>
              Reservar
            </Link>
            <Link href="#contacto" className="text-sm font-medium text-muted-foreground" onClick={() => setIsOpen(false)}>
              Contacto
            </Link>
            <Button asChild className="rounded-full bg-primary text-primary-foreground w-full">
              <Link href="/login">Reservar Ahora</Link>
            </Button>
          </div>
        </div>
      )}
    </header>
  )
}
