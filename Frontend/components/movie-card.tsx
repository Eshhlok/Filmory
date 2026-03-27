"use client"

import Image from "next/image"
import { Star } from "lucide-react"
import type { Movie } from "@/lib/types"

interface MovieCardProps {
  movie: Movie
  onClick: (movie: Movie) => void
  showRank?: number
}

export function MovieCard({ movie, onClick, showRank }: MovieCardProps) {
  const year = movie.release_date ? new Date(movie.release_date).getFullYear() : "N/A"
  
  return (
    <button
      onClick={() => onClick(movie)}
      className="group text-left w-full"
    >
      <div className="filmory-card relative aspect-[2/3] rounded-lg overflow-hidden bg-stone-200 mb-3">
        {showRank && (
          <div className="absolute top-2 left-2 z-10 w-8 h-8 rounded-full bg-amber-600 text-white font-serif text-lg flex items-center justify-center">
            {showRank}
          </div>
        )}
        {movie.poster_path ? (
          <Image
            src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
            alt={movie.title}
            fill
            className="object-cover transition-transform duration-500 ease-out group-hover:scale-[1.06]"
            sizes="(max-width: 640px) 50vw, (max-width: 1024px) 33vw, 20vw"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-stone-400 font-serif text-sm">
            No Poster
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
      </div>
      <h3 className="font-medium text-stone-800 group-hover:text-amber-700 transition-colors line-clamp-1 text-balance">
        {movie.title}
      </h3>
      <div className="flex items-center gap-2 text-sm text-stone-500 mt-1">
        <span>{year}</span>
        {movie.vote_average > 0 && (
          <>
            <span className="text-stone-300">|</span>
            <span className="flex items-center gap-1">
              <Star className="w-3.5 h-3.5 fill-amber-500 text-amber-500" />
              {movie.vote_average.toFixed(1)}
              
            </span>
          </>
        )}
      </div>
    </button>
  )
}
