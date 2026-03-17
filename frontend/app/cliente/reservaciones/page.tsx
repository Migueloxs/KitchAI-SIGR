"use client"

import { useState } from "react"
import {
  CalendarDays,
  Clock,
  Users,
  User,
  Mail,
  Phone,
} from "lucide-react"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { StatusBadge } from "@/components/dashboard/status-badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { reservations } from "@/lib/data"

export default function ClienteReservacionesPage() {
  const [showForm, setShowForm] = useState(false)

  return (
    <DashboardLayout
      role="client"
      userName="Juan Perez"
      userRole="Cliente"
      title="Mis Reservaciones"
    >
      {/* Header with New Reservation Button */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          Gestiona tus reservaciones y crea nuevas
        </p>
        <Button
          onClick={() => setShowForm(!showForm)}
          className="rounded-full bg-primary text-primary-foreground hover:bg-primary/90"
        >
          {showForm ? "Ver Reservaciones" : "Nueva Reservacion"}
        </Button>
      </div>

      {showForm ? (
        /* New Reservation Form */
        <div className="mt-6 rounded-xl border border-border bg-card p-8">
          <h2 className="font-serif text-2xl font-bold text-foreground mb-6">Reservar una Mesa</h2>
          <div className="grid gap-6 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <Label htmlFor="date" className="text-sm font-medium text-foreground">
                Fecha
              </Label>
              <div className="relative">
                <CalendarDays className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="date"
                  type="date"
                  className="rounded-lg border-border pl-10"
                />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="time" className="text-sm font-medium text-foreground">
                Hora
              </Label>
              <div className="relative">
                <Clock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="time"
                  type="time"
                  className="rounded-lg border-border pl-10"
                />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="guests" className="text-sm font-medium text-foreground">
                Invitados
              </Label>
              <div className="relative">
                <Users className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Select defaultValue="2">
                  <SelectTrigger className="rounded-lg border-border pl-10">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
                      <SelectItem key={n} value={String(n)}>
                        {n} {n === 1 ? "persona" : "personas"}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="name" className="text-sm font-medium text-foreground">
                Nombre
              </Label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="name"
                  placeholder="Juan Perez"
                  className="rounded-lg border-border pl-10"
                />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="email" className="text-sm font-medium text-foreground">
                Email
              </Label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  placeholder="juan@email.com"
                  className="rounded-lg border-border pl-10"
                />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="phone" className="text-sm font-medium text-foreground">
                Telefono
              </Label>
              <div className="relative">
                <Phone className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                <Input
                  id="phone"
                  type="tel"
                  placeholder="+1 234 567 890"
                  className="rounded-lg border-border pl-10"
                />
              </div>
            </div>
          </div>
          <Button className="mt-8 w-full rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 h-12 text-base font-medium">
            Reservar Ahora
          </Button>
        </div>
      ) : (
        /* Reservations List */
        <div className="mt-6 rounded-xl border border-border bg-card">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Fecha
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Hora
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Invitados
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Estado
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {reservations.map((res, idx) => (
                  <tr key={`${res.id}-${idx}`} className="hover:bg-muted/50 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-foreground">{res.id}</td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">{res.date}</td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">{res.hour}</td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">{res.guests} personas</td>
                    <td className="px-6 py-4">
                      <StatusBadge status={res.status} />
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {res.actions.map((action) => (
                          <Button
                            key={action}
                            size="sm"
                            variant={action === "Confirmar" || action === "Cancelar" ? "default" : "outline"}
                            className={
                              action === "Confirmar"
                                ? "rounded-full bg-success text-success-foreground hover:bg-success/90 text-xs px-3"
                                : action === "Cancelar"
                                  ? "rounded-full bg-destructive text-destructive-foreground hover:bg-destructive/90 text-xs px-3"
                                  : "rounded-full border-border text-xs px-3 bg-transparent"
                            }
                          >
                            {action}
                          </Button>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </DashboardLayout>
  )
}
