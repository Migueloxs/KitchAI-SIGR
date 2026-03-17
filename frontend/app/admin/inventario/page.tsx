"use client"

import { useState } from "react"
import { Plus, Search, AlertTriangle } from "lucide-react"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { StatusBadge } from "@/components/dashboard/status-badge"
import { inventoryItems } from "@/lib/data"

export default function InventarioPage() {
  const [search, setSearch] = useState("")

  const filtered = inventoryItems.filter((item) =>
    item.name.toLowerCase().includes(search.toLowerCase())
  )

  const lowStockCount = inventoryItems.filter(
    (item) => item.status === "Bajo" || item.status === "Critico"
  ).length

  return (
    <DashboardLayout role="admin" userName="Manuel Guzman" userRole="Admin" title="Inventario">
      {/* Alerts */}
      {lowStockCount > 0 && (
        <div className="mb-6 flex items-center gap-3 rounded-lg border border-warning/30 bg-warning/10 p-4">
          <AlertTriangle className="h-5 w-5 text-warning shrink-0" />
          <p className="text-sm text-foreground">
            <span className="font-semibold">{lowStockCount} items</span> con stock bajo o critico.
            Revisa el inventario.
          </p>
        </div>
      )}

      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-sm flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Buscar item..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 rounded-lg border-border"
          />
        </div>
        <Button className="rounded-lg bg-primary text-primary-foreground hover:bg-primary/90">
          <Plus className="mr-2 h-4 w-4" />
          Registrar Movimiento
        </Button>
      </div>

      <div className="mt-6 rounded-xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-muted/50">
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Producto
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Cantidad
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Min. Stock
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Costo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Estado
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((item) => (
                <tr key={item.id} className="hover:bg-muted/50 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-foreground">{item.name}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">
                    {item.quantity} {item.unit}
                  </td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">
                    {item.minStock} {item.unit}
                  </td>
                  <td className="px-6 py-4 text-sm font-medium text-foreground">
                    ${item.cost.toFixed(2)}
                  </td>
                  <td className="px-6 py-4">
                    <StatusBadge status={item.status} />
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
