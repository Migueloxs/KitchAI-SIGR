"use client"

import React from "react"

import Link from "next/link"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { ChefHat, Eye, EyeOff } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function RegisterPage() {
  const router = useRouter()
  const [showPassword, setShowPassword] = useState(false)

  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault()
    router.push("/cliente")
  }

  return (
    <div className="flex min-h-screen">
      <div className="hidden w-1/2 lg:block">
        <div
          className="relative h-full bg-cover bg-center"
          style={{ backgroundImage: "url(/images/reservation-ambience.jpg)" }}
        >
          <div className="absolute inset-0 bg-foreground/40" />
          <div className="relative z-10 flex h-full flex-col justify-end p-12">
            <h2 className="max-w-md font-serif text-3xl font-bold text-primary-foreground leading-tight">
              Unete a KitchAI
            </h2>
            <p className="mt-4 max-w-md text-primary-foreground/80 leading-relaxed">
              Crea tu cuenta para reservar mesas, ver el menu y disfrutar de una experiencia personalizada.
            </p>
          </div>
        </div>
      </div>

      <div className="flex w-full flex-col items-center justify-center px-6 lg:w-1/2">
        <div className="w-full max-w-md">
          <Link href="/" className="mb-8 flex items-center gap-2">
            <ChefHat className="h-8 w-8 text-primary" />
            <span className="text-2xl font-serif font-bold text-foreground">KitchAI</span>
          </Link>

          <h1 className="font-serif text-2xl font-bold text-foreground">Crear Cuenta</h1>
          <p className="mt-2 text-muted-foreground">
            Completa tus datos para registrarte como cliente
          </p>

          <form onSubmit={handleRegister} className="mt-8 flex flex-col gap-5">
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="flex flex-col gap-2">
                <Label htmlFor="firstName">Nombre</Label>
                <Input id="firstName" placeholder="Juan" className="rounded-lg border-border" required />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="lastName">Apellido</Label>
                <Input id="lastName" placeholder="Perez" className="rounded-lg border-border" required />
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" placeholder="correo@ejemplo.com" className="rounded-lg border-border" required />
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="phone">Telefono</Label>
              <Input id="phone" type="tel" placeholder="+1 234 567 890" className="rounded-lg border-border" />
            </div>

            <div className="flex flex-col gap-2">
              <Label htmlFor="password">Contrasena</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="********"
                  className="rounded-lg border-border pr-10"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                  aria-label={showPassword ? "Ocultar contrasena" : "Mostrar contrasena"}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 py-6"
            >
              Crear Cuenta
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            Ya tienes una cuenta?{" "}
            <Link href="/login" className="text-primary font-medium hover:underline">
              Inicia Sesion
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
