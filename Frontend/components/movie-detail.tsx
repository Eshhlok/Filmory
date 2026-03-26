"use client"

import { useEffect } from "react"
import Image from "next/image"
import { X, Star, Calendar, Globe, Users, Clapperboard } from "lucide-react"
import { Button } from "@/components/ui/button"
import type { Movie, Genre, RecommendationType } from "@/lib/types"
import { getCredits } from "@/lib/mock-data"

interface MovieDetailProps {
  movie: Movie
  onClose: () => void
  onRecommend: (movie: Movie, type: RecommendationType, personId?: number) => void
}

export function MovieDetail({ movie, onClose, onRecommend }: MovieDetailProps) {
  const credits = getCredits(movie.id)
  const director = credits?.crew?.find(c => c.job === "Director")
  const topCast = credits?.cast?.slice(0, 5) || []
  const genres: Genre[] = movie.genres || []
  const year = movie.release_date ? new Date(movie.release_date).getFullYear() : "N/A"

  // Prevent body scroll when modal is open
  useEffect(() => {
    document.body.style.overflow = "hidden"
    return () => {
      document.body.style.overflow = ""
    }
  }, [])

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-y-auto">
      <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />
      <div className="relative bg-stone-50 rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden shadow-2xl">
        {/* Backdrop */}
        <div className="relative h-48 sm:h-64">
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
          <div className="absolute inset-0 bg-gradient-to-t from-stone-50 via-stone-50/50 to-transparent" />
          <button
            onClick={onClose}
            className="absolute top-4 right-4 w-10 h-10 rounded-full bg-white/90 hover:bg-white flex items-center justify-center transition-colors shadow-lg"
          >
            <X className="w-5 h-5 text-stone-700" />
          </button>
        </div>

        <div className="px-6 pb-6 -mt-20 relative">
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

            {/* Info */}
            <div className="flex-1 pt-16 sm:pt-20">
              <h2 className="font-serif text-2xl sm:text-3xl text-stone-800 text-balance">{movie.title}</h2>
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

          <div className="mt-6 max-h-[40vh] overflow-y-auto pr-2">
            {/* Overview */}
            <p className="text-stone-600 leading-relaxed">{movie.overview || "No overview available."}</p>

            {/* Genres */}
            {genres.length > 0 && (
              <div className="mt-4">
                <div className="flex flex-wrap gap-2">
                  {genres.map(genre => (
                    <span key={genre.id} className="px-3 py-1 bg-stone-200 text-stone-700 text-sm rounded-full">
                      {genre.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Credits */}
            <div className="mt-5 space-y-3">
              {director && (
                <div className="flex items-center gap-2 text-sm">
                  <Clapperboard className="w-4 h-4 text-stone-400" />
                  <span className="text-stone-500">Director:</span>
                  <span className="text-stone-700 font-medium">{director.name}</span>
                </div>
              )}
              {topCast.length > 0 && (
                <div className="flex items-start gap-2 text-sm">
                  <Users className="w-4 h-4 text-stone-400 mt-0.5" />
                  <span className="text-stone-500">Cast:</span>
                  <span className="text-stone-700">{topCast.map(c => c.name).join(", ")}</span>
                </div>
              )}
            </div>

            {/* Recommendation buttons */}
            <div className="mt-6 pt-5 border-t border-stone-200">
              <p className="text-sm text-stone-500 mb-3">Find similar movies by:</p>
              <div className="flex flex-wrap gap-2">
                <Button
                  onClick={() => onRecommend(movie, "story")}
                  variant="outline"
                  className="bg-white border-stone-300 hover:bg-amber-50 hover:border-amber-300 hover:text-amber-700"
                >
                  Story / Plot
                </Button>
                {topCast.length > 0 && (
                  <Button
                    onClick={() => onRecommend(movie, "cast", topCast[0].id)}
                    variant="outline"
                    className="bg-white border-stone-300 hover:bg-amber-50 hover:border-amber-300 hover:text-amber-700"
                  >
                    Cast ({topCast[0].name})
                  </Button>
                )}
                {director && (
                  <Button
                    onClick={() => onRecommend(movie, "director", director.id)}
                    variant="outline"
                    className="bg-white border-stone-300 hover:bg-amber-50 hover:border-amber-300 hover:text-amber-700"
                  >
                    Director ({director.name})
                  </Button>
                )}
                {genres.length > 0 && (
                  <Button
                    onClick={() => onRecommend(movie, "genre")}
                    variant="outline"
                    className="bg-white border-stone-300 hover:bg-amber-50 hover:border-amber-300 hover:text-amber-700"
                  >
                    Genre ({genres[0].name})
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
