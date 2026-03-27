"use client"

import { useInView } from "@/hooks/useInView"
import { MovieCard } from "@/components/movie-card"
import type { Movie } from "@/lib/types"

interface AnimatedMovieCardProps {
  movie: Movie
  index: number
  onClick: (movie: Movie) => void
}

export function AnimatedMovieCard({ movie, index, onClick }: AnimatedMovieCardProps) {
  const { ref, isVisible } = useInView()

  return (
    <div
      ref={ref}
      style={{
        opacity: isVisible ? 1 : 0,
        transform: isVisible ? "translateY(0)" : "translateY(20px)",
        transition: `opacity 0.4s ease ${index * 0.05}s, transform 0.4s ease ${index * 0.05}s`,
      }}
    >
      <MovieCard movie={movie} onClick={onClick} />
    </div>
  )
}