"use client"

import { Bell, Menu } from "lucide-react"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"

interface TopbarProps {
  title: string
  userName: string
  onMenuClick?: () => void
}

export function Topbar({ title, userName, onMenuClick }: TopbarProps) {
  return (
    <header className="sticky top-0 z-30 flex items-center justify-between border-b border-border bg-card px-6 py-4">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          onClick={onMenuClick}
          aria-label="Abrir menu"
        >
          <Menu className="h-5 w-5" />
        </Button>
        <h1 className="text-xl font-serif font-bold text-foreground md:text-2xl">{title}</h1>
      </div>

      <div className="flex items-center gap-4">
        <span className="hidden text-sm font-medium text-foreground sm:block">{userName}</span>
        <Avatar className="h-9 w-9">
          <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
            {userName.split(" ").map((n) => n[0]).join("")}
          </AvatarFallback>
        </Avatar>
        <Button variant="ghost" size="icon" className="relative" aria-label="Notificaciones">
          <Bell className="h-5 w-5 text-muted-foreground" />
          <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-primary" />
        </Button>
      </div>
    </header>
  )
}
