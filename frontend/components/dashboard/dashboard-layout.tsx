"use client"

import React from "react"

import { useState } from "react"
import { SidebarNav } from "./sidebar-nav"
import { Topbar } from "./topbar"

interface DashboardLayoutProps {
  children: React.ReactNode
  role: "admin" | "employee" | "client"
  userName: string
  userRole: string
  title: string
}

export function DashboardLayout({
  children,
  role,
  userName,
  userRole,
  title,
}: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <div className="flex min-h-screen bg-background">
      <SidebarNav
        role={role}
        userName={userName}
        userRole={userRole}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      <div className="flex flex-1 flex-col">
        <Topbar
          title={title}
          userName={userName}
          onMenuClick={() => setSidebarOpen(true)}
        />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  )
}
