"use client"

import { useState } from "react"
import { Send } from "lucide-react"
import { DashboardLayout } from "@/components/dashboard/dashboard-layout"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"

interface Message {
  id: number
  sender: "user" | "bot"
  text: string
}

const initialMessages: Message[] = [
  { id: 1, sender: "bot", text: "Hola, soy el asistente de KitchAI. En que puedo ayudarte hoy?" },
]

const quickActions = [
  "Ver Menu",
  "Consultar Inventario",
  "Estado de Pedidos",
  "Procedimientos",
]

export default function EmpleadoChatPage() {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [input, setInput] = useState("")

  const handleSend = () => {
    if (!input.trim()) return
    const userMsg: Message = { id: Date.now(), sender: "user", text: input }
    const botMsg: Message = {
      id: Date.now() + 1,
      sender: "bot",
      text: "Entendido. Estoy procesando tu consulta. En un sistema completo, aqui se conectaria con la IA para responder tu pregunta.",
    }
    setMessages([...messages, userMsg, botMsg])
    setInput("")
  }

  return (
    <DashboardLayout role="employee" userName="Maria Gomez" userRole="Mesero" title="Chat de Asistencia">
      <div className="flex flex-col h-[calc(100vh-12rem)] rounded-xl border border-border bg-card">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="flex flex-col gap-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex items-start gap-3 ${msg.sender === "user" ? "flex-row-reverse" : ""}`}
              >
                <Avatar className="h-8 w-8 shrink-0">
                  <AvatarFallback
                    className={`text-xs font-semibold ${
                      msg.sender === "bot"
                        ? "bg-primary/10 text-primary"
                        : "bg-muted text-muted-foreground"
                    }`}
                  >
                    {msg.sender === "bot" ? "AI" : "MG"}
                  </AvatarFallback>
                </Avatar>
                <div
                  className={`max-w-md rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                    msg.sender === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-muted text-foreground"
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="border-t border-border px-6 py-3">
          <div className="flex flex-wrap gap-2">
            {quickActions.map((action) => (
              <button
                key={action}
                type="button"
                onClick={() => {
                  setInput(action)
                }}
                className="rounded-full border border-primary/30 bg-primary/5 px-3 py-1.5 text-xs font-medium text-primary hover:bg-primary/10 transition-colors"
              >
                {action}
              </button>
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
