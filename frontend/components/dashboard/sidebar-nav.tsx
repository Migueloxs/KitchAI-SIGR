"use client"

import React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Users,
  UtensilsCrossed,
  Package,
  BarChart3,
  Settings,
  ChefHat,
  LogOut,
  ClipboardList,
  MessageSquare,
  CalendarDays,
  X,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

interface NavItem {
  label: string
  href: string
  icon: React.ComponentType<{ className?: string }>
}

const adminNavItems: NavItem[] = [
  { label: "Dashboard", href: "/admin", icon: LayoutDashboard },
  { label: "Empleados", href: "/admin/empleados", icon: Users },
  { label: "Menu", href: "/admin/menu", icon: UtensilsCrossed },
  { label: "Inventario", href: "/admin/inventario", icon: Package },
  { label: "Reportes", href: "/admin/reportes", icon: BarChart3 },
  { label: "Configuracion", href: "/admin/configuracion", icon: Settings },
]

const employeeNavItems: NavItem[] = [
  { label: "Dashboard", href: "/empleado", icon: LayoutDashboard },
  { label: "Pedidos", href: "/empleado/pedidos", icon: ClipboardList },
  { label: "Inventario", href: "/empleado/inventario", icon: Package },
  { label: "Chat de Asistencia", href: "/empleado/chat", icon: MessageSquare },
]

const clientNavItems: NavItem[] = [
  { label: "Dashboard", href: "/cliente", icon: LayoutDashboard },
  { label: "Pedidos", href: "/cliente/pedidos", icon: ClipboardList },
  { label: "Reservaciones", href: "/cliente/reservaciones", icon: CalendarDays }, // Use CalendarDays here
  { label: "Chat de Asistencia", href: "/cliente/chat", icon: MessageSquare },
]

interface SidebarNavProps {
  role: "admin" | "employee" | "client"
  userName: string
  userRole: string
  isOpen?: boolean
  onClose?: () => void
}

export function SidebarNav({ role, userName, userRole, isOpen, onClose }: SidebarNavProps) {
  const pathname = usePathname()

  const navItems = role === "admin" ? adminNavItems : role === "employee" ? employeeNavItems : clientNavItems

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-40 bg-foreground/20 lg:hidden" onClick={onClose} onKeyDown={(e) => e.key === "Escape" && onClose?.()} />
      )}

      <aside
        className={cn(
          "fixed left-0 top-0 z-50 flex h-screen w-64 flex-col border-r border-border bg-card transition-transform lg:translate-x-0 lg:static lg:z-auto",
          isOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="flex items-center justify-between border-b border-border px-6 py-5">
          <Link href="/" className="flex items-center gap-2">
            <ChefHat className="h-7 w-7 text-primary" />
            <span className="text-xl font-serif font-bold text-foreground">KitchAI</span>
          </Link>
          <button
            type="button"
            onClick={onClose}
            className="text-muted-foreground hover:text-foreground lg:hidden"
            aria-label="Cerrar menu"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Nav items */}
        <nav className="flex-1 overflow-y-auto px-4 py-4">
          <div className="flex flex-col gap-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onClose}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  <item.icon className={cn("h-5 w-5", isActive ? "text-primary" : "")} />
                  {item.label}
                </Link>
              )
            })}
          </div>
        </nav>

        {/* User profile */}
        <div className="border-t border-border p-4">
          <div className="flex items-center gap-3">
            <Avatar className="h-10 w-10">
              <AvatarFallback className="bg-primary/10 text-primary text-sm font-semibold">
                {userName.split(" ").map((n) => n[0]).join("")}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-foreground truncate">{userName}</p>
              <p className="text-xs text-muted-foreground">{userRole}</p>
            </div>
          </div>
          <Link
            href="/login"
            className="mt-3 flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
          >
            <LogOut className="h-4 w-4" />
            Cerrar Sesion
          </Link>
        </div>
      </aside>
    </>
  )
}
