"use client"

import Link from "next/link"
import {
  ClipboardList,
  CalendarDays,
  MessageSquare,
  ChevronRight,
} from "lucide-react"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { KpiCard } from "@/components/dashboard/kpi-card"
import { StatusBadge } from "@/components/dashboard/status-badge"
import { Button } from "@/components/ui/button"
import { reservations } from "@/lib/data"

const clientOrders = [
  { id: "#0016", date: "09 Feb, 2026", items: "Caprese Salad, Grilled Salmon", total: 24.0, status: "En Proceso" },
  { id: "#0015", date: "08 Feb, 2026", items: "Risotto de Hongos, Tiramisu", total: 21.5, status: "Entregado" },
  { id: "#0014", date: "05 Feb, 2026", items: "Bruschetta, Panna Cotta", total: 12.5, status: "Entregado" },
]

export default function ClienteDashboard() {
  return (
    <DashboardLayout
      role="client"
      userName="Juan Perez"
      userRole="Cliente"
      title="Dashboard"
    >
      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        <KpiCard title="Mis Pedidos" value="3" subtitle="Pedidos recientes" icon={ClipboardList} />
        <KpiCard title="Reservaciones" value="2" subtitle="Reservaciones activas" icon={CalendarDays} />
        <KpiCard title="Mensajes" value="5" subtitle="Conversaciones" icon={MessageSquare} />
      </div>

      {/* Recent Orders */}
      <div className="mt-8 rounded-xl border border-border bg-card">
        <div className="flex items-center justify-between p-6">
          <h2 className="font-serif text-xl font-bold text-foreground">Mis Pedidos Recientes</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-t border-border">
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Pedido
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Fecha
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Items
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Total
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
              {clientOrders.map((order) => (
                <tr key={order.id + order.date} className="hover:bg-muted/50 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-foreground">{order.id}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{order.date}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground max-w-[200px] truncate">{order.items}</td>
                  <td className="px-6 py-4 text-sm font-medium text-foreground">${order.total.toFixed(2)}</td>
                  <td className="px-6 py-4">
                    <StatusBadge status={order.status} />
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Button size="sm" variant="outline" className="rounded-full border-border text-xs px-4 bg-transparent">
                      Ver Detalles
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="flex justify-center border-t border-border p-4">
          <Button variant="outline" className="rounded-full border-border text-sm bg-transparent" asChild>
            <Link href="/cliente/pedidos">
              Ver Todos <ChevronRight className="ml-1 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>

      {/* Reservations Preview */}
      <div className="mt-8 rounded-xl border border-border bg-card">
        <div className="flex items-center justify-between p-6">
          <h2 className="font-serif text-xl font-bold text-foreground">Mis Reservaciones</h2>
          <Button className="rounded-full bg-primary text-primary-foreground hover:bg-primary/90 text-sm" asChild>
            <Link href="/cliente/reservaciones">
              Nueva Reservacion
            </Link>
          </Button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-t border-border">
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
                  <td className="px-6 py-4 text-sm font-medium text-foreground">{res.date}</td>
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

      {/* Quick Actions */}
      <div className="mt-8 rounded-xl border border-border bg-card p-6">
        <h2 className="font-serif text-xl font-bold text-foreground mb-6">Acciones Rapidas</h2>
        <div className="grid gap-3 sm:grid-cols-3">
          <Button variant="outline" className="justify-between rounded-lg border-border h-12 bg-transparent" asChild>
            <Link href="/cliente/reservaciones">
              Reservar Mesa <CalendarDays className="h-4 w-4" />
            </Link>
          </Button>
          <Button variant="outline" className="justify-between rounded-lg border-border h-12 bg-transparent" asChild>
            <Link href="/cliente/pedidos">
              Ver Pedidos <ClipboardList className="h-4 w-4" />
            </Link>
          </Button>
          <Button variant="outline" className="justify-between rounded-lg border-border h-12 bg-transparent" asChild>
            <Link href="/cliente/chat">
              Chat de Asistencia <MessageSquare className="h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>
    </DashboardLayout>
  )
}
