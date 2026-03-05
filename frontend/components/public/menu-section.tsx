"use client"

import Image from "next/image"
import { useState } from "react"
import { menuItems } from "@/lib/data"
import { Button } from "@/components/ui/button"

const categories = ["Entradas", "Platos Principales", "Postres"]

export function MenuSection() {
  const [activeCategory, setActiveCategory] = useState("Entradas")

  const filtered = menuItems.filter((item) => item.category === activeCategory)

  return (
    <section id="menu" className="bg-background py-20">
      <div className="mx-auto max-w-7xl px-6">
        <div className="grid gap-12 lg:grid-cols-2">
          <div>
            <h2 className="font-serif text-3xl font-bold text-foreground md:text-4xl">
              Nuestro Menu
            </h2>

            <div className="mt-6 flex gap-2">
              {categories.map((cat) => (
                <button
                  key={cat}
                  type="button"
                  onClick={() => setActiveCategory(cat)}
                  className={`rounded-full border px-5 py-2 text-sm font-medium transition-colors ${
                    activeCategory === cat
                      ? "border-primary bg-primary/10 text-primary"
                      : "border-border text-muted-foreground hover:border-primary/50 hover:text-foreground"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            <div className="mt-8 grid gap-6 sm:grid-cols-2">
              {filtered.map((item) => (
                <div key={item.id} className="group">
                  <div className="relative aspect-[4/3] overflow-hidden rounded-lg">
                    <Image
                      src={item.image || "/placeholder.svg"}
                      alt={item.name}
                      fill
                      className="object-cover transition-transform group-hover:scale-105"
                    />
                  </div>
                  <h3 className="mt-3 font-serif text-lg font-semibold text-foreground">
                    {item.name}
                  </h3>
                  <p className="mt-1 text-sm text-muted-foreground leading-relaxed">
                    {item.description}
                  </p>
                  <p className="mt-2 text-lg font-semibold text-foreground">
                    ${item.price.toFixed(2)}
                  </p>
                </div>
              ))}
            </div>

            <Button className="mt-8 w-full rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 sm:w-auto px-8">
              Ver Menu Completo
            </Button>
          </div>

          <div className="hidden lg:block">
            <div className="relative aspect-[3/4] overflow-hidden rounded-2xl">
              <Image
                src="/images/restaurant-ambience.jpg"
                alt="Ambiente elegante y acogedor"
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
