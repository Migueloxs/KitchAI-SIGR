"use client"

import { useState } from "react"
import { Search } from "lucide-react"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { StatusBadge } from "@/components/dashboard/status-badge"

const allOrders = [
  { id: "#0016", table: "Mesa 2", status: "Pendiente", total: 40.0, time: "14:30" },
  { id: "#0015", table: "Mesa 3", status: "Entregado", total: 68.0, time: "14:15" },
  { id: "#0014", table: "Mesa 5", status: "En Proceso", total: 52.0, time: "13:45" },
  { id: "#0013", table: "Para Llevar", status: "Entregado", total: 25.0, time: "13:30" },
  { id: "#0012", table: "Mesa 1", status: "Pendiente", total: 36.0, time: "13:00" },
  { id: "#0011", table: "Mesa 4", status: "Entregado", total: 95.0, time: "12:45" },
]

export default function PedidosPage() {
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState("Todos")

  const statuses = ["Todos", "Pendiente", "En Proceso", "Entregado"]

  const filtered = allOrders.filter((o) => {
    const matchSearch = o.id.includes(search) || o.table.toLowerCase().includes(search.toLowerCase())
    const matchStatus = statusFilter === "Todos" || o.status === statusFilter
    return matchSearch && matchStatus
  })

  return (
    <DashboardLayout role="employee" userName="Maria Gomez" userRole="Mesero" title="Pedidos">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-sm flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Buscar pedido..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 rounded-lg border-border"
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          {statuses.map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => setStatusFilter(s)}
              className={`rounded-full border px-4 py-2 text-sm font-medium transition-colors ${
                statusFilter === s
                  ? "border-primary bg-primary/10 text-primary"
                  : "border-border text-muted-foreground hover:border-primary/50"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-6 rounded-xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-muted/50">
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">Pedido</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">Mesa</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">Estado</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">Total</th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">Hora</th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-muted-foreground">Acciones</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((order) => (
                <tr key={order.id + order.table} className="hover:bg-muted/50 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-foreground">{order.id}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{order.table}</td>
                  <td className="px-6 py-4"><StatusBadge status={order.status} /></td>
                  <td className="px-6 py-4 text-sm font-medium text-foreground">${order.total.toFixed(2)}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{order.time}</td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button size="sm" className="rounded-full bg-primary text-primary-foreground hover:bg-primary/90 text-xs px-4">
                        Actualizar
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
    </DashboardLayout>
  )
}
