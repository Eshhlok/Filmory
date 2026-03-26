"use client"

import { Film } from "lucide-react"

export function LoadingScreen() {
  return (
    <div className="fixed inset-0 z-50 bg-stone-100">
      {/* Decorative blurred shapes */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full bg-amber-200/40 blur-3xl animate-pulse" />
        <div className="absolute bottom-1/3 right-1/4 w-80 h-80 rounded-full bg-stone-300/30 blur-3xl animate-pulse delay-300" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full bg-amber-100/50 blur-2xl animate-pulse delay-150" />
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4">
        {/* Logo */}
        <div className="mb-8 animate-bounce">
          <div className="w-20 h-20 rounded-full bg-amber-600 flex items-center justify-center shadow-lg shadow-amber-600/20">
            <Film className="w-10 h-10 text-white" />
          </div>
        </div>

        {/* Title */}
        <h1 className="font-serif text-4xl sm:text-5xl text-stone-800 mb-3 text-center">
          Filmory
        </h1>
        
        {/* Tagline */}
        <p className="text-stone-500 text-lg mb-10 text-center max-w-md">
          Discovering the perfect film for your mood...
        </p>

        {/* Loading bar */}
        <div className="w-64 h-1.5 bg-stone-200 rounded-full overflow-hidden">
          <div className="h-full bg-gradient-to-r from-amber-500 to-amber-600 rounded-full animate-loading-bar" />
        </div>

        {/* Loading text */}
        <p className="mt-4 text-stone-400 text-sm animate-pulse">
          Preparing your recommendations
        </p>
      </div>
    </div>
  )
}
