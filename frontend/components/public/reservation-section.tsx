"use client"

import Image from "next/image"
import { useState } from "react"
import { CalendarDays, Users, User, Mail, Phone } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export function ReservationSection() {
  const [submitted, setSubmitted] = useState(false)

  return (
    <section id="reservar" className="bg-card py-20">
      <div className="mx-auto max-w-7xl px-6">
        <h2 className="text-center font-serif text-3xl font-bold text-foreground md:text-4xl">
          Reservar una Mesa
        </h2>

        <div className="mt-12 grid gap-12 lg:grid-cols-2">
          <div className="rounded-2xl border border-border bg-card p-8 shadow-sm">
            {submitted ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-success/10">
                  <CalendarDays className="h-8 w-8 text-success" />
                </div>
                <h3 className="font-serif text-xl font-bold text-foreground">Reserva Confirmada</h3>
                <p className="mt-2 text-muted-foreground">Te enviaremos un correo con los detalles.</p>
                <Button
                  className="mt-6 rounded-full bg-primary text-primary-foreground hover:bg-primary/90"
                  onClick={() => setSubmitted(false)}
                >
                  Hacer otra reserva
                </Button>
              </div>
            ) : (
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  setSubmitted(true)
                }}
                className="flex flex-col gap-5"
              >
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="relative">
                    <CalendarDays className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      type="date"
                      className="pl-10 rounded-lg border-border"
                      required
                    />
                  </div>
                  <Select>
                    <SelectTrigger className="rounded-lg border-border">
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4 text-muted-foreground" />
                        <SelectValue placeholder="Invitados" />
                      </div>
                    </SelectTrigger>
                    <SelectContent>
                      {[1, 2, 3, 4, 5, 6, 7, 8].map((n) => (
                        <SelectItem key={n} value={String(n)}>
                          {n} {n === 1 ? "invitado" : "invitados"}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Nombre"
                      className="pl-10 rounded-lg border-border"
                      required
                    />
                  </div>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      type="email"
                      placeholder="Email"
                      className="pl-10 rounded-lg border-border"
                      required
                    />
                  </div>
                </div>

                <div className="relative">
                  <Phone className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    type="tel"
                    placeholder="+1 234 567 890"
                    className="pl-10 rounded-lg border-border"
                  />
                </div>

                <Select>
                  <SelectTrigger className="rounded-lg border-border">
                    <SelectValue placeholder="Hora" />
                  </SelectTrigger>
                  <SelectContent>
                    {["11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM", "5:00 PM", "6:00 PM", "7:00 PM", "8:00 PM", "9:00 PM"].map((time) => (
                      <SelectItem key={time} value={time}>
                        {time}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>

                <Button
                  type="submit"
                  className="w-full rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 py-6 text-base"
                >
                  Reservar Ahora
                </Button>
              </form>
            )}
          </div>

          <div className="hidden lg:block">
            <div className="relative aspect-[4/3] overflow-hidden rounded-2xl">
              <Image
                src="/images/reservation-ambience.jpg"
                alt="Ambiente elegante y acogedor del restaurante"
                fill
                className="object-cover"
              />
            </div>
            <h3 className="mt-6 font-serif text-2xl font-bold text-foreground">
              Ambiente Elegante y Acogedor
            </h3>
            <p className="mt-2 text-muted-foreground leading-relaxed">
              Disfruta de una atmosfera sofisticada y un servicio de alta calidad, ideal para cenas
              romanticas y reuniones especiales.
            </p>
          </div>
        </div>
      </div>
    </section>
  )
}
