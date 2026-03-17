"use client"

import Link from "next/link"
import {
  ClipboardList,
  CalendarDays,
  AlertTriangle,
  ChevronRight,
} from "lucide-react"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { KpiCard } from "@/components/dashboard/kpi-card"
import { StatusBadge } from "@/components/dashboard/status-badge"
import { Button } from "@/components/ui/button"
import { recentOrders, inventoryItems } from "@/lib/data"

const lowStockItems = inventoryItems.filter(
  (i) => i.status === "Bajo" || i.status === "Critico"
)

export default function EmpleadoDashboard() {
  return (
    <DashboardLayout
      role="employee"
      userName="Maria Gomez"
      userRole="Mesero"
      title="Dashboard"
    >
      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-3">
        <KpiCard title="Pedidos" value="5" subtitle="Pedidos activos" icon={ClipboardList} />
        <KpiCard title="Reservas para Hoy" value="12" subtitle="Reservas confirmadas" icon={CalendarDays} />
        <KpiCard title="Nivel de Inventario" value="8" subtitle="Items bajo stock" icon={AlertTriangle} />
      </div>

      {/* Active Orders */}
      <div className="mt-8 rounded-xl border border-border bg-card">
        <div className="flex items-center justify-between p-6">
          <h2 className="font-serif text-xl font-bold text-foreground">Pedidos Activos</h2>
          <Button variant="outline" size="sm" className="rounded-full border-border text-sm bg-transparent">
            + Inventarios
          </Button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-t border-border">
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Pedido
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Mesa
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Total
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {recentOrders.map((order) => (
                <tr key={order.id + order.table} className="hover:bg-muted/50 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-foreground">{order.id}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{order.table}</td>
                  <td className="px-6 py-4">
                    <StatusBadge status={order.status} />
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-foreground">
                    ${order.total.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button size="sm" className="rounded-full bg-primary text-primary-foreground hover:bg-primary/90 text-xs px-4">
                        {order.action}
                      </Button>
                      <Button size="sm" variant="outline" className="rounded-full border-border text-xs px-4 bg-transparent">
                        Detalles
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Bottom Grid */}
      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        {/* Low Stock Alerts */}
        <div className="rounded-xl border border-border bg-card">
          <div className="p-6">
            <h2 className="font-serif text-xl font-bold text-foreground">Alertas de Inventario</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-t border-border">
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Producto
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Cantidad
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Estado
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {lowStockItems.map((item) => (
                  <tr key={item.id} className="hover:bg-muted/50 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-foreground">{item.name}</td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">
                      {item.quantity} {item.unit}
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={item.status} />
                    </td>
                  </tr>
                ))}
                {lowStockItems.length === 0 && (
                  <tr>
                    <td colSpan={3} className="px-6 py-8 text-center text-sm text-muted-foreground">
                      Todo el inventario esta en niveles normales.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="font-serif text-xl font-bold text-foreground mb-6">Acciones Rapidas</h2>
          <div className="flex flex-col gap-3">
            <Button variant="outline" className="justify-between rounded-lg border-border h-12 bg-transparent" asChild>
              <Link href="/empleado/pedidos">
                Ver todos los pedidos <ChevronRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button variant="outline" className="justify-between rounded-lg border-border h-12 bg-transparent" asChild>
              <Link href="/empleado/inventario">
                Registrar movimiento de inventario <ChevronRight className="h-4 w-4" />
              </Link>
            </Button>
            <Button variant="outline" className="justify-between rounded-lg border-border h-12 bg-transparent" asChild>
              <Link href="/empleado/chat">
                Chat de asistencia <ChevronRight className="h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
