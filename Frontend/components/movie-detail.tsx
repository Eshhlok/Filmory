"use client"

import { useEffect } from "react"
import Image from "next/image"
import { X, Star, Calendar, Globe, Users, Clapperboard } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { Movie, RecommendationType } from "@/lib/types"
import { useInView } from "@/hooks/useInView"

interface MovieDetailProps {
  movie: Movie
  onClose: () => void
  onRecommend: (movie: Movie, type: RecommendationType, personId?: number) => void
}

export function MovieDetail({ movie, onClose, onRecommend }: MovieDetailProps) {
  const director = movie.directors?.[0]
  const topCast = movie.cast?.slice(0, 5) || []
  const genres = movie.genre_names || []
  const year = movie.release_date
    ? new Date(movie.release_date).getFullYear()
    : "N/A"

  const { ref, isVisible } = useInView()

  useEffect(() => {
    document.body.style.overflow = "hidden"
    return () => {
      document.body.style.overflow = ""
    }
  }, [])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">

      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm animate-[fadeIn_.25s_ease-out]"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="relative bg-stone-50 rounded-2xl max-w-3xl w-full h-[85vh] flex flex-col shadow-2xl animate-[modalIn_.28s_cubic-bezier(.22,.61,.36,1)]">

        {/* Backdrop */}
        <div className="relative h-48 sm:h-64 shrink-0">
          {movie.backdrop_path ? (
            <Image
              src={`https://image.tmdb.org/t/p/w1280${movie.backdrop_path}`}
              alt=""
              fill
              className="object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-stone-300 to-stone-400" />
          )}

          <div className="absolute inset-0 bg-gradient-to-t from-stone-50 via-stone-50/60 to-transparent" />

          <button
            onClick={onClose}
            className="absolute top-4 right-4 w-10 h-10 rounded-full bg-white/90 hover:bg-white flex items-center justify-center transition-colors shadow-lg"
          >
            <X className="w-5 h-5 text-stone-700" />
          </button>
        </div>

        {/* Header */}
        <div className="px-6 -mt-20 relative shrink-0">
          <div className="flex gap-5">

            {/* Poster */}
            <div className="shrink-0 w-32 sm:w-40 aspect-[2/3] rounded-lg overflow-hidden shadow-xl bg-stone-200">
              {movie.poster_path ? (
                <Image
                  src={`https://image.tmdb.org/t/p/w500${movie.poster_path}`}
                  alt={movie.title}
                  width={160}
                  height={240}
                  className="object-cover w-full h-full"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-stone-400 font-serif text-sm">
                  No Poster
                </div>
              )}
            </div>

            {/* Title */}
            <div className="flex-1 pt-16 sm:pt-20">
              <h2 className="font-serif text-2xl sm:text-3xl text-stone-800">
                {movie.title}
              </h2>

              <div className="flex flex-wrap items-center gap-3 mt-2 text-sm text-stone-500">
                <span className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  {year}
                </span>

                {movie.vote_average > 0 && (
                  <span className="flex items-center gap-1">
                    <Star className="w-4 h-4 fill-amber-500 text-amber-500" />
                    {movie.vote_average.toFixed(1)}
                  </span>
                )}

                <span className="flex items-center gap-1">
                  <Globe className="w-4 h-4" />
                  {movie.original_language?.toUpperCase()}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Scroll container */}
        <div className="mt-6 px-6 pb-6 overflow-y-auto flex-1">

          {/* Animated content (scroll triggered) */}
          <div
            ref={ref}
            className={`transition-opacity duration-300 ${
              isVisible ? "filmory-stagger opacity-100" : "opacity-0"
            }`}
          >

            {/* Overview */}
            <div>
              <p className="text-stone-600 leading-relaxed">
                {movie.overview || "No overview available."}
              </p>
            </div>

            {/* Genres */}
            {genres.length > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {genres.map((genre) => (
                  <span
                    key={genre}
                    className="px-3 py-1 bg-stone-200 text-stone-700 text-sm rounded-full"
                  >
                    {genre}
                  </span>
                ))}
              </div>
            )}

            {/* Director */}
            {director && (
              <div className="mt-5 flex items-center gap-2 text-sm">
                <Clapperboard className="w-4 h-4 text-stone-400" />
                <span className="text-stone-500">Director:</span>
                <span className="text-stone-700 font-medium">
                  {director}
                </span>
              </div>
            )}

            {/* Cast */}
            {topCast.length > 0 && (
              <div className="flex items-start gap-2 text-sm">
                <Users className="w-4 h-4 text-stone-400 mt-0.5" />
                <span className="text-stone-500">Cast:</span>
                <span className="text-stone-700">
                  {topCast.join(", ")}
                </span>
              </div>
            )}

            {/* Buttons */}
            <div className="mt-6 pt-5 border-t border-stone-200">
              <p className="text-sm text-stone-500 mb-3">
                Find similar movies by:
              </p>

              <div className="flex flex-wrap gap-2">
                <Button onClick={() => onRecommend(movie, "story")} variant="outline" className="cursor-pointer">
                  Story / Plot
                </Button>

                {topCast.length > 0 && (
                  <Button onClick={() => onRecommend(movie, "cast")} variant="outline" className="cursor-pointer">
                    Cast
                  </Button>
                )}

                {director && (
                  <Button onClick={() => onRecommend(movie, "director")} variant="outline" className="cursor-pointer">
                    Director
                  </Button>
                )}

                {genres.length > 0 && (
                  <Button onClick={() => onRecommend(movie, "genre")} variant="outline" className="cursor-pointer">
                    Genre
                  </Button>
                )}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  )
}