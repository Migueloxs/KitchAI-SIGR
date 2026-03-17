"use client"

import React from "react"

import Link from "next/link"
import Image from "next/image"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { ChefHat, Eye, EyeOff, Mail, Lock, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export default function LoginPage() {
  const router = useRouter()
  const [showPassword, setShowPassword] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setTimeout(() => {
      if (email.includes("admin")) {
        router.push("/admin")
      } else if (email.includes("empleado")) {
        router.push("/empleado")
      } else {
        router.push("/cliente")
      }
    }, 600)
  }

  const handleDemoLogin = (role: string) => {
    setEmail(`${role}@kitchai.com`)
    setPassword("demo1234")
    setIsLoading(true)
    setTimeout(() => {
      if (role === "admin") router.push("/admin")
      else if (role === "empleado") router.push("/empleado")
      else router.push("/cliente")
    }, 600)
  }

  return (
    <div className="flex min-h-screen bg-background">
      {/* Left - Image panel */}
      <div className="hidden w-[55%] lg:block">
        <div className="relative h-full overflow-hidden">
          <Image
            src="/images/hero-restaurant.jpg"
            alt="Restaurante elegante"
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-t from-foreground/70 via-foreground/30 to-foreground/10" />
          <div className="relative z-10 flex h-full flex-col justify-between p-10">
            <Link href="/" className="flex items-center gap-2.5">
              <ChefHat className="h-8 w-8 text-card" />
              <span className="font-serif text-2xl font-bold text-card">KitchAI</span>
            </Link>
            <div className="max-w-lg">
              <p className="mb-3 text-sm font-medium uppercase tracking-widest text-primary">
                Bienvenido de nuevo
              </p>
              <h2 className="font-serif text-4xl font-bold leading-tight text-card">
                Gestiona tu restaurante de forma inteligente
              </h2>
              <p className="mt-4 text-lg leading-relaxed text-card/80">
                Accede a tu panel para controlar pedidos, reservaciones, inventario y mucho mas con la ayuda de inteligencia artificial.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Right - Login form */}
      <div className="flex w-full flex-col lg:w-[45%]">
        {/* Mobile header */}
        <div className="flex items-center justify-between p-6 lg:hidden">
          <Link href="/" className="flex items-center gap-2">
            <ChefHat className="h-7 w-7 text-primary" />
            <span className="font-serif text-xl font-bold text-foreground">KitchAI</span>
          </Link>
          <Link href="/register" className="text-sm font-medium text-primary hover:underline">
            Registrate
          </Link>
        </div>

        <div className="flex flex-1 flex-col items-center justify-center px-6 py-8 lg:px-12">
          <div className="w-full max-w-[420px]">
            {/* Desktop logo area */}
            <div className="mb-8 hidden lg:block">
              <p className="text-sm text-muted-foreground">
                Accede a tu cuenta
              </p>
            </div>

            <h1 className="font-serif text-3xl font-bold text-foreground">
              Iniciar Sesion
            </h1>
            <p className="mt-2 text-muted-foreground leading-relaxed">
              Ingresa tus credenciales para continuar
            </p>

            {/* Demo role buttons */}
            <div className="mt-6 flex flex-col gap-2">
              <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Acceso rapido demo
              </p>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => handleDemoLogin("admin")}
                  disabled={isLoading}
                  className="flex flex-col items-center gap-1 rounded-lg border border-border bg-card px-3 py-3 text-center transition-all hover:border-primary hover:bg-primary/5 disabled:opacity-50"
                >
                  <span className="text-xs font-semibold text-foreground">Admin</span>
                  <span className="text-[10px] text-muted-foreground">Panel completo</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleDemoLogin("empleado")}
                  disabled={isLoading}
                  className="flex flex-col items-center gap-1 rounded-lg border border-border bg-card px-3 py-3 text-center transition-all hover:border-primary hover:bg-primary/5 disabled:opacity-50"
                >
                  <span className="text-xs font-semibold text-foreground">Empleado</span>
                  <span className="text-[10px] text-muted-foreground">Pedidos y cocina</span>
                </button>
                <button
                  type="button"
                  onClick={() => handleDemoLogin("cliente")}
                  disabled={isLoading}
                  className="flex flex-col items-center gap-1 rounded-lg border border-border bg-card px-3 py-3 text-center transition-all hover:border-primary hover:bg-primary/5 disabled:opacity-50"
                >
                  <span className="text-xs font-semibold text-foreground">Cliente</span>
                  <span className="text-[10px] text-muted-foreground">Reservaciones</span>
                </button>
              </div>
            </div>

            {/* Divider */}
            <div className="my-6 flex items-center gap-4">
              <div className="h-px flex-1 bg-border" />
              <span className="text-xs font-medium text-muted-foreground">o con email</span>
              <div className="h-px flex-1 bg-border" />
            </div>

            {/* Form */}
            <form onSubmit={handleLogin} className="flex flex-col gap-5">
              <div className="flex flex-col gap-2">
                <Label htmlFor="email" className="text-sm font-medium text-foreground">
                  Email
                </Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="correo@ejemplo.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="h-11 rounded-lg border-border bg-card pl-10"
                    required
                  />
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password" className="text-sm font-medium text-foreground">
                    Contrasena
                  </Label>
                  <Link
                    href="/forgot-password"
                    className="text-xs font-medium text-primary hover:underline"
                  >
                    Olvidaste tu contrasena?
                  </Link>
                </div>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="Ingresa tu contrasena"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="h-11 rounded-lg border-border bg-card pl-10 pr-10"
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground transition-colors hover:text-foreground"
                    aria-label={showPassword ? "Ocultar contrasena" : "Mostrar contrasena"}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              <Button
                type="submit"
                disabled={isLoading}
                className="h-12 w-full rounded-lg bg-primary text-primary-foreground transition-all hover:bg-primary/90 disabled:opacity-70"
              >
                {isLoading ? (
                  <span className="flex items-center gap-2">
                    <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Ingresando...
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    Iniciar Sesion
                    <ArrowRight className="h-4 w-4" />
                  </span>
                )}
              </Button>
            </form>

            <p className="mt-8 text-center text-sm text-muted-foreground">
              {"No tienes una cuenta? "}
              <Link
                href="/register"
                className="font-semibold text-primary hover:underline"
              >
                Crea tu cuenta aqui
              </Link>
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-center border-t border-border px-6 py-4">
          <p className="text-xs text-muted-foreground">
            {"2026 KitchAI. Todos los derechos reservados."}
          </p>
        </div>
      </div>
    </div>
  )
}
