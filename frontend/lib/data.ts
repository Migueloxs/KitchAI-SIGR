// Mock data for KitchAI restaurant management system

export const menuItems = [
  {
    id: 1,
    name: "Caprese Salad",
    description: "Rodaja de tomate fresco, mozzarella de búfala, albahaca y balsámico.",
    price: 8.0,
    category: "Entradas",
    image: "/images/caprese-salad.jpg",
    available: true,
  },
  {
    id: 2,
    name: "Grilled Salmon",
    description: "Filete de salmón a la parrilla servido con espárragos y papas al romero.",
    price: 16.0,
    category: "Platos Principales",
    image: "/images/grilled-salmon.jpg",
    available: true,
  },
  {
    id: 3,
    name: "Tiramisú",
    description: "Postre clásico italiano con capas de bizcocho, mascarpone y café.",
    price: 7.5,
    category: "Postres",
    image: "/images/caprese-salad.jpg",
    available: true,
  },
  {
    id: 4,
    name: "Bruschetta Clásica",
    description: "Pan tostado con tomate fresco, ajo, albahaca y aceite de oliva.",
    price: 6.5,
    category: "Entradas",
    image: "/images/grilled-salmon.jpg",
    available: true,
  },
  {
    id: 5,
    name: "Risotto de Hongos",
    description: "Arroz arborio cremoso con mezcla de hongos silvestres y parmesano.",
    price: 14.0,
    category: "Platos Principales",
    image: "/images/caprese-salad.jpg",
    available: true,
  },
  {
    id: 6,
    name: "Panna Cotta",
    description: "Crema italiana con salsa de frutos rojos y menta fresca.",
    price: 6.0,
    category: "Postres",
    image: "/images/grilled-salmon.jpg",
    available: false,
  },
]

export const recentOrders = [
  { id: "#0016", table: "Mesa 2", status: "Pendiente", total: 40.0, action: "Servir" },
  { id: "#0015", table: "Mesa 3", status: "Entregado", total: 68.0, action: "En Proceso" },
  { id: "#0014", table: "Mesa 5", status: "En Proceso", total: 52.0, action: "Entregado" },
  { id: "#0013", table: "Para Llevar", status: "Entregado", total: 25.0, action: "Servir" },
]

export const employees = [
  { id: 1, name: "María Gómez", role: "Mesero", salary: 40.0, avatar: "" },
  { id: 2, name: "Jonathan Pérez", role: "Cocina", salary: 68.0, avatar: "" },
  { id: 3, name: "Gabriela Martinez", role: "Cajero", salary: 52.0, avatar: "" },
  { id: 4, name: "Roberto Silva", role: "Admin", salary: 25.0, avatar: "" },
]

export const weeklyData = [
  { day: "LUN", sales: 120 },
  { day: "MAR", sales: 350 },
  { day: "MIÉ", sales: 850 },
  { day: "JUE", sales: 1050 },
  { day: "VIE", sales: 980 },
  { day: "SÁB", sales: 1100 },
  { day: "DOM", sales: 1350 },
]

export const recentActivity = [
  {
    id: 1,
    user: "Darío Contreras",
    action: "registró",
    detail: "Cuavo orden (#0016)",
    time: "Mesa 2:42",
    avatar: "",
  },
  {
    id: 2,
    user: "Roberto Silva",
    action: "registró",
    detail: "entrega de Exlrega (Lechuga)",
    time: "",
    avatar: "",
  },
  {
    id: 3,
    user: "Gabriela Martinez",
    action: "procesó",
    detail: "Activo (#0016)",
    time: "Mesa 3, 02",
    avatar: "",
  },
  {
    id: 4,
    user: "Manuel Guzmán",
    action: "agregó a",
    detail: "Jonathan Pérez (#0016)",
    time: "Mesa 3:00:00",
    avatar: "",
  },
]

export const reservations = [
  {
    id: "#3012",
    date: "$1.01, 2022",
    hour: "$5.00 PM",
    guests: 3,
    status: "Pendiente",
    actions: ["Ver Detalles", "Editar", "Confirmar"],
  },
  {
    id: "#3012",
    date: "$5.03, 2022",
    hour: "$5.00 PM",
    guests: 2,
    status: "Confirmada",
    actions: ["Ver Detalles", "Editar", "Cancelar"],
  },
  {
    id: "#3012",
    date: "$3.03, 2022",
    hour: "$5.00 PM",
    guests: 2,
    status: "Confirmada",
    actions: ["Ver Detalles", "Editar", "Reservar"],
  },
]

export const inventoryItems = [
  { id: 1, name: "Tomates", quantity: 50, unit: "kg", minStock: 20, cost: 3.5, status: "Normal" },
  { id: 2, name: "Salmón", quantity: 8, unit: "kg", minStock: 10, cost: 25.0, status: "Bajo" },
  { id: 3, name: "Mozzarella", quantity: 15, unit: "kg", minStock: 5, cost: 12.0, status: "Normal" },
  { id: 4, name: "Lechuga", quantity: 3, unit: "kg", minStock: 10, cost: 2.5, status: "Crítico" },
  { id: 5, name: "Aceite de Oliva", quantity: 20, unit: "L", minStock: 5, cost: 8.0, status: "Normal" },
  { id: 6, name: "Pasta", quantity: 30, unit: "kg", minStock: 10, cost: 4.0, status: "Normal" },
]
