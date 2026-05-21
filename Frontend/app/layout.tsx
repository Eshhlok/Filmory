import type { Metadata } from 'next'
import { DM_Serif_Display, Inter } from 'next/font/google'
import { Analytics } from '@vercel/analytics/next'
import './globals.css'

const _serif = DM_Serif_Display({ subsets: ["latin"], weight: "400" });
const _sans = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: 'Filmory - Your Curated Cinema Catalogue',
  description: 'Discover your next favorite film with intelligent, personalized recommendations',
  generator: 'v0.app',
  icons: {
    icon:  '/favicon.ico',
    apple: '/apple-touch-icon.png',
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        {children}
        <Analytics />
      </body>
    </html>
  )
}
