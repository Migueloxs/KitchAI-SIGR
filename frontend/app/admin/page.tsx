"use client"

import Link from "next/link"
import {
  DollarSign,
  CalendarDays,
  ClipboardList,
  ChevronRight,
  Pencil,
  Trash2,
  Package,
} from "lucide-react"
import {
  Area,
  AreaChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { KpiCard } from "@/components/dashboard/kpi-card"
import { StatusBadge } from "@/components/dashboard/status-badge"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { recentOrders, employees, weeklyData, recentActivity } from "@/lib/data"

export default function AdminDashboard() {
  return (
    <DashboardLayout
      role="admin"
      userName="Manuel Guzman"
      userRole="Admin"
      title="Dashboard"
    >
      {/* KPI Cards */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          title="Ventas del Dia"
          value="$1,482"
          subtitle="Ultimos 7 dias"
          icon={DollarSign}
        />
        <KpiCard
          title="Reservaciones"
          value="15"
          subtitle="Reservar del dia"
          icon={CalendarDays}
        />
        <KpiCard
          title="Pedidos Activos"
          value="8"
          subtitle="Pedidos activos"
          icon={ClipboardList}
        />
        <KpiCard
          title="Inventario Bajo Stock"
          value="7"
          subtitle="Items bajo stock"
          icon={Package}
        />
      </div>

      {/* Recent Orders */}
      <div className="mt-8 rounded-xl border border-border bg-card">
        <div className="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="font-serif text-xl font-bold text-foreground">Pedidos Recientes</h2>
          <div className="flex items-center gap-3">
            <Select defaultValue="7days">
              <SelectTrigger className="w-[160px] rounded-lg border-border text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="7days">Ultimos 7 dias</SelectItem>
                <SelectItem value="30days">Ultimos 30 dias</SelectItem>
                <SelectItem value="today">Hoy</SelectItem>
              </SelectContent>
            </Select>
            <Select defaultValue="export">
              <SelectTrigger className="w-[120px] rounded-lg border-border text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="export">Exportar</SelectItem>
                <SelectItem value="csv">CSV</SelectItem>
                <SelectItem value="pdf">PDF</SelectItem>
              </SelectContent>
            </Select>
          </div>
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
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Accion
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
                  <td className="px-6 py-4">
                    <Button
                      size="sm"
                      className="rounded-full bg-primary text-primary-foreground hover:bg-primary/90 text-xs px-4"
                    >
                      {order.action}
                    </Button>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Editar pedido">
                        <Pencil className="h-4 w-4 text-muted-foreground" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Eliminar pedido">
                        <Trash2 className="h-4 w-4 text-muted-foreground" />
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex justify-center border-t border-border p-4">
          <Button variant="outline" className="rounded-full border-border text-sm bg-transparent" asChild>
            <Link href="/admin/pedidos">
              Ver Todos <ChevronRight className="ml-1 h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>

      {/* Bottom Grid: Employees + Chart + Activity */}
      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        {/* Employees Table */}
        <div className="rounded-xl border border-border bg-card">
          <div className="flex items-center justify-between p-6">
            <h2 className="font-serif text-xl font-bold text-foreground">Empleados Recientes</h2>
            <Select defaultValue="action">
              <SelectTrigger className="w-[120px] rounded-full border-border text-sm">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="action">Acciones</SelectItem>
                <SelectItem value="add">Agregar</SelectItem>
                <SelectItem value="export">Exportar</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-t border-border">
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Nombre
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Rol
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-muted-foreground">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {employees.map((emp) => (
                  <tr key={emp.id} className="hover:bg-muted/50 transition-colors">
                    <td className="px-6 py-4 text-sm font-medium text-foreground">{emp.name}</td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">{emp.role}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Editar empleado">
                          <Pencil className="h-4 w-4 text-muted-foreground" />
                        </Button>
                        <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Eliminar empleado">
                          <Trash2 className="h-4 w-4 text-muted-foreground" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="flex justify-center border-t border-border p-4">
            <Button variant="outline" className="rounded-full border-border text-sm bg-transparent" asChild>
              <Link href="/admin/empleados">
                Ver Empleados <ChevronRight className="ml-1 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>

        {/* Weekly Report */}
        <div className="rounded-xl border border-border bg-card">
          <div className="flex items-center justify-between p-6">
            <h2 className="font-serif text-xl font-bold text-foreground">Informe Semanal</h2>
          </div>
          <div className="px-6">
            <div className="flex items-center gap-2 mb-4">
              <DollarSign className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-foreground">Ventas</span>
              <span className="text-sm font-bold text-foreground">$9,278 Semanales</span>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={weeklyData}>
                  <defs>
                    <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="hsl(36, 60%, 50%)" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="hsl(36, 60%, 50%)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis
                    dataKey="day"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: "hsl(20, 5%, 45%)" }}
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: "hsl(20, 5%, 45%)" }}
                    tickFormatter={(value) => `$${value}`}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "hsl(0, 0%, 100%)",
                      border: "1px solid hsl(30, 15%, 90%)",
                      borderRadius: "8px",
                      fontSize: "12px",
                    }}
                    formatter={(value: number) => [`$${value}`, "Ventas"]}
                  />
                  <Area
                    type="monotone"
                    dataKey="sales"
                    stroke="hsl(36, 60%, 50%)"
                    strokeWidth={2}
                    fill="url(#salesGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="flex items-center justify-between border-t border-border p-4 px-6">
            <div className="flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-primary" />
              <span className="text-sm text-muted-foreground">Ventas $9,278 Semanales</span>
            </div>
            <Button className="rounded-full bg-primary text-primary-foreground hover:bg-primary/90 text-sm" asChild>
              <Link href="/admin/reportes">
                Ver Reportes <ChevronRight className="ml-1 h-4 w-4" />
              </Link>
            </Button>
          </div>
        </div>
      </div>

      {/* Activity Feed */}
      <div className="mt-8 rounded-xl border border-border bg-card p-6">
        <h2 className="font-serif text-xl font-bold text-foreground mb-6">Actividad Reciente</h2>
        <div className="flex flex-col gap-5">
          {recentActivity.map((activity) => (
            <div key={activity.id} className="flex items-start gap-4">
              <Avatar className="h-10 w-10 shrink-0">
                <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
                  {activity.user.split(" ").map((n) => n[0]).join("")}
                </AvatarFallback>
              </Avatar>
              <div>
                <p className="text-sm text-foreground">
                  <span className="font-semibold">{activity.user}</span>{" "}
                  {activity.action} {activity.detail}
                </p>
                {activity.time && (
                  <p className="mt-1 text-xs text-muted-foreground">{activity.time}</p>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </DashboardLayout>
  )
}
