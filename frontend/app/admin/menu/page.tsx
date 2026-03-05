"use client"

import { useState } from "react"
import Image from "next/image"
import { Plus, Pencil, Trash2, Search } from "lucide-react"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { StatusBadge } from "@/components/dashboard/status-badge"
import { menuItems as initialMenu } from "@/lib/data"

const categories = ["Todos", "Entradas", "Platos Principales", "Postres"]

export default function MenuPage() {
  const [items, setItems] = useState(initialMenu)
  const [search, setSearch] = useState("")
  const [activeCategory, setActiveCategory] = useState("Todos")

  const filtered = items.filter((item) => {
    const matchSearch = item.name.toLowerCase().includes(search.toLowerCase())
    const matchCat = activeCategory === "Todos" || item.category === activeCategory
    return matchSearch && matchCat
  })

  return (
    <DashboardLayout role="admin" userName="Manuel Guzman" userRole="Admin" title="Menu">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-sm flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Buscar plato..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 rounded-lg border-border"
          />
        </div>
        <Button className="rounded-lg bg-primary text-primary-foreground hover:bg-primary/90">
          <Plus className="mr-2 h-4 w-4" />
          Agregar Plato
        </Button>
      </div>

      <div className="mt-4 flex gap-2 flex-wrap">
        {categories.map((cat) => (
          <button
            key={cat}
            type="button"
            onClick={() => setActiveCategory(cat)}
            className={`rounded-full border px-4 py-2 text-sm font-medium transition-colors ${
              activeCategory === cat
                ? "border-primary bg-primary/10 text-primary"
                : "border-border text-muted-foreground hover:border-primary/50"
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((item) => (
          <div
            key={item.id}
            className="group overflow-hidden rounded-xl border border-border bg-card transition-shadow hover:shadow-md"
          >
            <div className="relative aspect-[4/3] overflow-hidden">
              <Image
                src={item.image || "/placeholder.svg"}
                alt={item.name}
                fill
                className="object-cover transition-transform group-hover:scale-105"
              />
              <div className="absolute top-3 right-3">
                <StatusBadge status={item.available ? "Normal" : "Critico"} />
              </div>
            </div>
            <div className="p-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-serif text-lg font-semibold text-foreground">{item.name}</h3>
                  <p className="mt-1 text-xs text-muted-foreground">{item.category}</p>
                </div>
                <span className="text-lg font-bold text-primary">${item.price.toFixed(2)}</span>
              </div>
              <p className="mt-2 text-sm text-muted-foreground leading-relaxed line-clamp-2">
                {item.description}
              </p>
              <div className="mt-4 flex items-center justify-end gap-2">
                <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Editar plato">
                  <Pencil className="h-4 w-4 text-muted-foreground" />
                </Button>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8"
                  onClick={() => setItems(items.filter((i) => i.id !== item.id))}
                  aria-label="Eliminar plato"
                >
                  <Trash2 className="h-4 w-4 text-muted-foreground" />
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </DashboardLayout>
  )
}
