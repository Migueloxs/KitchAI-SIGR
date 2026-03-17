"use client"

import { useState } from "react"
import { Plus, Pencil, Trash2, Search } from "lucide-react"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface Employee {
  id: number
  name: string
  role: string
  email: string
  phone: string
  salary: number
}

const initialEmployees: Employee[] = [
  { id: 1, name: "Maria Gomez", role: "Mesero", email: "maria@kitchai.com", phone: "+1 234 567", salary: 2500 },
  { id: 2, name: "Jonathan Perez", role: "Cocina", email: "jonathan@kitchai.com", phone: "+1 234 568", salary: 2800 },
  { id: 3, name: "Gabriela Martinez", role: "Cajero", email: "gabriela@kitchai.com", phone: "+1 234 569", salary: 2400 },
  { id: 4, name: "Roberto Silva", role: "Admin", email: "roberto@kitchai.com", phone: "+1 234 570", salary: 3500 },
  { id: 5, name: "Dario Contreras", role: "Mesero", email: "dario@kitchai.com", phone: "+1 234 571", salary: 2500 },
]

export default function EmpleadosPage() {
  const [employees, setEmployees] = useState<Employee[]>(initialEmployees)
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)

  const filtered = employees.filter(
    (e) =>
      e.name.toLowerCase().includes(search.toLowerCase()) ||
      e.role.toLowerCase().includes(search.toLowerCase())
  )

  const handleDelete = (id: number) => {
    setEmployees(employees.filter((e) => e.id !== id))
  }

  return (
    <DashboardLayout role="admin" userName="Manuel Guzman" userRole="Admin" title="Empleados">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-sm flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Buscar empleado..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-10 rounded-lg border-border"
          />
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="rounded-lg bg-primary text-primary-foreground hover:bg-primary/90">
              <Plus className="mr-2 h-4 w-4" />
              Agregar Empleado
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle className="font-serif">Nuevo Empleado</DialogTitle>
            </DialogHeader>
            <form
              className="flex flex-col gap-4 mt-4"
              onSubmit={(e) => {
                e.preventDefault()
                const fd = new FormData(e.currentTarget)
                const newEmp: Employee = {
                  id: Date.now(),
                  name: fd.get("name") as string,
                  role: fd.get("role") as string,
                  email: fd.get("email") as string,
                  phone: fd.get("phone") as string,
                  salary: Number(fd.get("salary")),
                }
                setEmployees([...employees, newEmp])
                setDialogOpen(false)
              }}
            >
              <div className="flex flex-col gap-2">
                <Label htmlFor="name">Nombre</Label>
                <Input id="name" name="name" required className="rounded-lg border-border" />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="role">Rol</Label>
                <Select name="role" required>
                  <SelectTrigger className="rounded-lg border-border">
                    <SelectValue placeholder="Seleccionar rol" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Mesero">Mesero</SelectItem>
                    <SelectItem value="Cocina">Cocina</SelectItem>
                    <SelectItem value="Cajero">Cajero</SelectItem>
                    <SelectItem value="Admin">Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="flex flex-col gap-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" name="email" type="email" required className="rounded-lg border-border" />
                </div>
                <div className="flex flex-col gap-2">
                  <Label htmlFor="phone">Telefono</Label>
                  <Input id="phone" name="phone" className="rounded-lg border-border" />
                </div>
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="salary">Salario</Label>
                <Input id="salary" name="salary" type="number" required className="rounded-lg border-border" />
              </div>
              <Button type="submit" className="w-full rounded-lg bg-primary text-primary-foreground hover:bg-primary/90">
                Guardar Empleado
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="mt-6 rounded-xl border border-border bg-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border bg-muted/50">
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Empleado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Rol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Salario
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {filtered.map((emp) => (
                <tr key={emp.id} className="hover:bg-muted/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <Avatar className="h-9 w-9">
                        <AvatarFallback className="bg-primary/10 text-primary text-xs font-semibold">
                          {emp.name.split(" ").map((n) => n[0]).join("")}
                        </AvatarFallback>
                      </Avatar>
                      <span className="text-sm font-medium text-foreground">{emp.name}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{emp.role}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{emp.email}</td>
                  <td className="px-6 py-4 text-sm font-medium text-foreground">
                    ${emp.salary.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <Button variant="ghost" size="icon" className="h-8 w-8" aria-label="Editar">
                        <Pencil className="h-4 w-4 text-muted-foreground" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8"
                        onClick={() => handleDelete(emp.id)}
                        aria-label="Eliminar"
                      >
                        <Trash2 className="h-4 w-4 text-muted-foreground" />
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
