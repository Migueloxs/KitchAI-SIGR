"use client"

import { useState } from "react"
import { Send, Paperclip, Smile } from "lucide-react"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

interface Message {
  id: number
  sender: "user" | "bot"
  text: string
  quickActions?: string[]
}

const initialMessages: Message[] = [
  {
    id: 1,
    sender: "bot",
    text: "Hola Juan, le damos la bienvenida a KitchAI. En que puedo ayudarte hoy?",
    quickActions: ["Ver Menu", "Consultar Ubicacion", "Formatear Mesa", "Reservar Mesa"],
  },
]

export default function ClienteChatPage() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [input, setInput] = useState("")

  const handleSend = (text?: string) => {
    const msgText = text || input
    if (!msgText.trim()) return

    const userMsg: Message = { id: Date.now(), sender: "user", text: msgText }

    let botResponse = "Entendido. Estoy procesando tu consulta. En un sistema completo, aqui se conectaria con la IA para responder."
    if (msgText === "Ver Menu") {
      botResponse = "Nuestro menu incluye entradas como Caprese Salad ($8.00) y Bruschetta ($6.50), platos principales como Grilled Salmon ($16.00) y Risotto de Hongos ($14.00), y postres como Tiramisu ($7.50). Quieres ver el menu completo?"
    } else if (msgText === "Reservar Mesa") {
      botResponse = "Con gusto te ayudo a reservar. Para que fecha y hora te gustaria la reservacion? Y cuantos invitados seran?"
    } else if (msgText === "Consultar Ubicacion") {
      botResponse = "Nos encontramos en Calle Bonita 4:45, Ciudad Gourmet. Nuestro horario es de Lunes a Domingo, 11:00 AM - 10:00 PM. Te esperamos!"
    }

    const botMsg: Message = {
      id: Date.now() + 1,
      sender: "bot",
      text: botResponse,
    }

    setMessages((prev) => [...prev, userMsg, botMsg])
    setInput("")
  }

  return (
    <DashboardLayout role="client" userName="Juan Perez" userRole="Cliente" title="Chat de Asistencia">
      <div className="flex flex-col h-[calc(100vh-12rem)] rounded-xl border border-border bg-card">
        {/* Chat Header */}
        <div className="flex items-center gap-3 border-b border-border px-6 py-4">
          <Avatar className="h-10 w-10">
            <AvatarFallback className="bg-primary/10 text-primary text-sm font-semibold">AI</AvatarFallback>
          </Avatar>
          <div>
            <p className="text-sm font-semibold text-foreground">Asistente KitchAI</p>
            <p className="text-xs text-success">En linea</p>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="flex flex-col gap-4">
            {messages.map((msg) => (
              <div key={msg.id}>
                <div className={`flex items-start gap-3 ${msg.sender === "user" ? "flex-row-reverse" : ""}`}>
                  <Avatar className="h-8 w-8 shrink-0">
                    <AvatarFallback
                      className={`text-xs font-semibold ${
                        msg.sender === "bot"
                          ? "bg-primary/10 text-primary"
                          : "bg-muted text-muted-foreground"
                      }`}
                    >
                      {msg.sender === "bot" ? "AI" : "JP"}
                    </AvatarFallback>
                  </Avatar>
                  <div
                    className={`max-w-sm rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                      msg.sender === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted text-foreground"
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
                {/* Quick Actions */}
                {msg.quickActions && msg.sender === "bot" && (
                  <div className="mt-3 ml-11 flex flex-wrap gap-2">
                    {msg.quickActions.map((action) => (
                      <button
                        key={action}
                        type="button"
                        onClick={() => handleSend(action)}
                        className="rounded-full border border-primary/30 bg-primary/5 px-4 py-2 text-xs font-medium text-primary hover:bg-primary/10 transition-colors"
                      >
                        {action}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Input */}
        <div className="border-t border-border p-4">
          <form
            onSubmit={(e) => {
              e.preventDefault()
              handleSend()
            }}
            className="flex items-center gap-3"
          >
            <Button type="button" variant="ghost" size="icon" className="shrink-0" aria-label="Adjuntar archivo">
              <Paperclip className="h-4 w-4 text-muted-foreground" />
            </Button>
            <Button type="button" variant="ghost" size="icon" className="shrink-0" aria-label="Emojis">
              <Smile className="h-4 w-4 text-muted-foreground" />
            </Button>
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Escribe tu mensaje..."
              className="flex-1 rounded-full border-border"
            />
            <Button
              type="submit"
              size="icon"
              className="shrink-0 rounded-full bg-primary text-primary-foreground hover:bg-primary/90"
              aria-label="Enviar mensaje"
            >
              <Send className="h-4 w-4" />
            </Button>
          </form>
        </div>
      </div>
    </DashboardLayout>
  )
}
