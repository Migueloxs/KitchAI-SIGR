import Link from "next/link"
import { ChefHat, Mail } from "lucide-react"

export function Footer() {
  return (
    <footer className="border-t border-border bg-card py-12">
      <div className="mx-auto max-w-7xl px-6">
        <div className="flex flex-col items-center justify-between gap-6 md:flex-row">
          <div className="flex items-center gap-2">
            <ChefHat className="h-6 w-6 text-primary" />
            <span className="font-serif text-lg font-bold text-foreground">KitchAI</span>
          </div>

          <p className="text-sm text-muted-foreground">
            &copy; 2026 KitchAI. Todos los derechos reservados.
          </p>

          <div className="flex items-center gap-4">
            <Link href="mailto:contacto@kitchai.com" className="flex items-center gap-2 text-sm text-muted-foreground hover:text-primary transition-colors">
              <Mail className="h-4 w-4" />
              contacto@kitchai.com
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
