import { cn } from "@/lib/utils"

const variants: Record<string, string> = {
  Pendiente: "bg-warning/15 text-warning border-warning/30",
  "En Proceso": "bg-info/15 text-info border-info/30",
  Entregado: "bg-success/15 text-success border-success/30",
  Confirmada: "bg-success/15 text-success border-success/30",
  Cancelada: "bg-destructive/15 text-destructive border-destructive/30",
  Servir: "bg-primary/15 text-primary border-primary/30",
  Normal: "bg-success/15 text-success border-success/30",
  Bajo: "bg-warning/15 text-warning border-warning/30",
  "Critico": "bg-destructive/15 text-destructive border-destructive/30",
}

interface StatusBadgeProps {
  status: string
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium",
        variants[status] || "bg-muted text-muted-foreground border-border",
        className
      )}
    >
      {status}
    </span>
  )
}
