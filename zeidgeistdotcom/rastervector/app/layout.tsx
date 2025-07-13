import type React from "react"
import type { Metadata } from "next"
import "./globals.css"

export const dynamic = 'force-static'

export const metadata: Metadata = {
  title: "rv0 - Vector Optimization Studio",
  description: "Advanced raster-to-vector conversion engine with hole detection and LAB color accuracy",
  generator: "rv0.dev",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
