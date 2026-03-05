"use client"

import {
  DollarSign,
  TrendingUp,
  Users,
  ShoppingCart,
} from "lucide-react"
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { KpiCard } from "@/components/dashboard/kpi-card"
import { weeklyData } from "@/lib/data"

const monthlyData = [
  { month: "Ene", revenue: 12500, orders: 320 },
  { month: "Feb", revenue: 14200, orders: 380 },
  { month: "Mar", revenue: 11800, orders: 290 },
  { month: "Abr", revenue: 15600, orders: 410 },
  { month: "May", revenue: 16900, orders: 440 },
  { month: "Jun", revenue: 18200, orders: 480 },
]

const categoryData = [
  { category: "Entradas", sales: 3200 },
  { category: "Principales", sales: 8500 },
  { category: "Postres", sales: 2100 },
  { category: "Bebidas", sales: 4800 },
]

export default function ReportesPage() {
  return (
    <DashboardLayout role="admin" userName="Manuel Guzman" userRole="Admin" title="Reportes">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard title="Ingresos Mensuales" value="$18,200" subtitle="Este mes" icon={DollarSign} />
        <KpiCard title="Crecimiento" value="+12%" subtitle="vs. mes anterior" icon={TrendingUp} />
        <KpiCard title="Clientes Nuevos" value="45" subtitle="Este mes" icon={Users} />
        <KpiCard title="Pedidos Totales" value="480" subtitle="Este mes" icon={ShoppingCart} />
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        {/* Revenue Chart */}
        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="font-serif text-xl font-bold text-foreground mb-6">Ingresos Mensuales</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={monthlyData}>
                <defs>
                  <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(36, 60%, 50%)" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(36, 60%, 50%)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(30, 15%, 90%)" />
                <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(20, 5%, 45%)" }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(20, 5%, 45%)" }} tickFormatter={(v) => `$${v / 1000}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: "hsl(0,0%,100%)", border: "1px solid hsl(30,15%,90%)", borderRadius: "8px", fontSize: "12px" }}
                  formatter={(value: number) => [`$${value.toLocaleString()}`, "Ingresos"]}
                />
                <Area type="monotone" dataKey="revenue" stroke="hsl(36, 60%, 50%)" strokeWidth={2} fill="url(#revenueGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Bar Chart */}
        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="font-serif text-xl font-bold text-foreground mb-6">Ventas por Categoria</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={categoryData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(30, 15%, 90%)" />
                <XAxis dataKey="category" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(20, 5%, 45%)" }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(20, 5%, 45%)" }} tickFormatter={(v) => `$${v / 1000}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: "hsl(0,0%,100%)", border: "1px solid hsl(30,15%,90%)", borderRadius: "8px", fontSize: "12px" }}
                  formatter={(value: number) => [`$${value.toLocaleString()}`, "Ventas"]}
                />
                <Bar dataKey="sales" fill="hsl(36, 60%, 50%)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Weekly Trend */}
      <div className="mt-6 rounded-xl border border-border bg-card p-6">
        <h2 className="font-serif text-xl font-bold text-foreground mb-6">Tendencia Semanal</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={weeklyData}>
              <defs>
                <linearGradient id="weeklyGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(36, 60%, 50%)" stopOpacity={0.2} />
                  <stop offset="95%" stopColor="hsl(36, 60%, 50%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(30, 15%, 90%)" />
              <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(20, 5%, 45%)" }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: "hsl(20, 5%, 45%)" }} tickFormatter={(v) => `$${v}`} />
              <Tooltip
                contentStyle={{ backgroundColor: "hsl(0,0%,100%)", border: "1px solid hsl(30,15%,90%)", borderRadius: "8px", fontSize: "12px" }}
                formatter={(value: number) => [`$${value}`, "Ventas"]}
              />
              <Area type="monotone" dataKey="sales" stroke="hsl(36, 60%, 50%)" strokeWidth={2} fill="url(#weeklyGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </DashboardLayout>
  )
}
