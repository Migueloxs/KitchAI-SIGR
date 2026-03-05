"use client"

import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"

export default function ConfiguracionPage() {
  return (
    <DashboardLayout role="admin" userName="Manuel Guzman" userRole="Admin" title="Configuracion">
      <div className="mx-auto max-w-2xl">
        {/* Restaurant Info */}
        <div className="rounded-xl border border-border bg-card p-6">
          <h2 className="font-serif text-xl font-bold text-foreground">Informacion del Restaurante</h2>
          <p className="mt-1 text-sm text-muted-foreground">Configura los datos generales de tu restaurante.</p>
          <Separator className="my-6" />
          <form className="flex flex-col gap-5">
            <div className="flex flex-col gap-2">
              <Label htmlFor="restaurantName">Nombre del Restaurante</Label>
              <Input id="restaurantName" defaultValue="KitchAI" className="rounded-lg border-border" />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="flex flex-col gap-2">
                <Label htmlFor="phone">Telefono</Label>
                <Input id="phone" defaultValue="+1 234 557 880" className="rounded-lg border-border" />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" defaultValue="contacto@kitchai.com" className="rounded-lg border-border" />
              </div>
            </div>
            <div className="flex flex-col gap-2">
              <Label htmlFor="address">Direccion</Label>
              <Input id="address" defaultValue="Calle Bonita 4:45, Ciudad Gourmet" className="rounded-lg border-border" />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="flex flex-col gap-2">
                <Label htmlFor="openTime">Hora de Apertura</Label>
                <Input id="openTime" type="time" defaultValue="11:00" className="rounded-lg border-border" />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="closeTime">Hora de Cierre</Label>
                <Input id="closeTime" type="time" defaultValue="22:00" className="rounded-lg border-border" />
              </div>
            </div>
            <Button className="w-full rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 sm:w-auto">
              Guardar Cambios
            </Button>
          </form>
        </div>

        {/* Notifications */}
        <div className="mt-6 rounded-xl border border-border bg-card p-6">
          <h2 className="font-serif text-xl font-bold text-foreground">Notificaciones</h2>
          <p className="mt-1 text-sm text-muted-foreground">Configura las notificaciones del sistema.</p>
          <Separator className="my-6" />
          <div className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-foreground">Notificaciones por email</p>
                <p className="text-xs text-muted-foreground">Recibe alertas de nuevos pedidos por email.</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-foreground">Alertas de inventario</p>
                <p className="text-xs text-muted-foreground">Notificaciones cuando el stock este bajo.</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-foreground">Reservaciones</p>
                <p className="text-xs text-muted-foreground">Notificaciones de nuevas reservaciones.</p>
              </div>
              <Switch defaultChecked />
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}
