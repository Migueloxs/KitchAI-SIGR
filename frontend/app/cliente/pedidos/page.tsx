"use client"

import { Eye } from "lucide-react"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { StatusBadge } from "@/components/dashboard/status-badge"
import { Button } from "@/components/ui/button"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

const allClientOrders = [
  { id: "#0016", date: "09 Feb, 2026", items: "Caprese Salad, Grilled Salmon", total: 24.0, status: "En Proceso" },
  { id: "#0015", date: "08 Feb, 2026", items: "Risotto de Hongos, Tiramisu", total: 21.5, status: "Entregado" },
  { id: "#0014", date: "05 Feb, 2026", items: "Bruschetta, Panna Cotta", total: 12.5, status: "Entregado" },
  { id: "#0013", date: "01 Feb, 2026", items: "Grilled Salmon, Tiramisu", total: 23.5, status: "Entregado" },
  { id: "#0012", date: "28 Ene, 2026", items: "Caprese Salad", total: 8.0, status: "Entregado" },
  { id: "#0011", date: "25 Ene, 2026", items: "Risotto de Hongos, Bruschetta", total: 20.5, status: "Cancelada" },
]

export default function ClientePedidosPage() {
  return (
    <DashboardLayout
      role="client"
      userName="Juan Perez"
      userRole="Cliente"
      title="Mis Pedidos"
    >
      {/* Filters */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm text-muted-foreground">
          Mostrando <span className="font-medium text-foreground">{allClientOrders.length}</span> pedidos
        </p>
        <div className="flex items-center gap-3">
          <Select defaultValue="all">
            <SelectTrigger className="w-[150px] rounded-lg border-border text-sm">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Todos</SelectItem>
              <SelectItem value="proceso">En Proceso</SelectItem>
              <SelectItem value="entregado">Entregado</SelectItem>
              <SelectItem value="cancelada">Cancelada</SelectItem>
            </SelectContent>
          </Select>
          <Select defaultValue="recent">
            <SelectTrigger className="w-[150px] rounded-lg border-border text-sm">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="recent">Mas reciente</SelectItem>
              <SelectItem value="oldest">Mas antiguo</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Orders Table */}
      <div className="mt-6 rounded-xl border border-border bg-card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
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
              {allClientOrders.map((order, idx) => (
                <tr key={`${order.id}-${idx}`} className="hover:bg-muted/50 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-foreground">{order.id}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{order.date}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground max-w-[250px] truncate">{order.items}</td>
                  <td className="px-6 py-4 text-sm font-medium text-foreground">${order.total.toFixed(2)}</td>
                  <td className="px-6 py-4">
                    <StatusBadge status={order.status} />
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Ver detalles del pedido">
                      <Eye className="h-4 w-4 text-muted-foreground" />
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Order Summary */}
      <div className="mt-8 grid gap-4 sm:grid-cols-3">
        <div className="rounded-xl border border-border bg-card p-6 text-center">
          <p className="text-sm text-muted-foreground">Total Gastado</p>
          <p className="mt-2 text-2xl font-bold text-foreground">$110.00</p>
          <p className="mt-1 text-xs text-muted-foreground">Ultimo mes</p>
        </div>
        <div className="rounded-xl border border-border bg-card p-6 text-center">
          <p className="text-sm text-muted-foreground">Pedidos Completados</p>
          <p className="mt-2 text-2xl font-bold text-foreground">4</p>
          <p className="mt-1 text-xs text-muted-foreground">Este mes</p>
        </div>
        <div className="rounded-xl border border-border bg-card p-6 text-center">
          <p className="text-sm text-muted-foreground">Plato Favorito</p>
          <p className="mt-2 text-2xl font-bold text-foreground">Salmon</p>
          <p className="mt-1 text-xs text-muted-foreground">Mas pedido</p>
        </div>
      </div>
    </DashboardLayout>
  )
}
