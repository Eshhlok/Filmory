"use client"

import { useState, useEffect } from "react"
import { Search, Film, Sparkles, X, BookOpen, Users, Clapperboard, Layers, AlertCircle } from "lucide-react"
import { MovieCard } from "@/components/movie-card"
import { MovieDetail } from "@/components/movie-detail"
import { LoadingScreen } from "@/components/loading-screen"
import { Spinner } from "@/components/ui/spinner"
import type { Movie, RecommendationType } from "@/lib/types"
import { 
  MOVIES, 
  LANGUAGES, 
  searchMovies,  
  getSimilarMovies, 
  getMoviesByDirector, 
  getMoviesByCast,
  getMoviesByGenreFromMovie,
  getCredits 
} from "@/lib/mock-data"

const RECOMMENDATION_MODES = [
  { id: "story" as RecommendationType, label: "Story / Plot", icon: BookOpen, description: "Similar themes and narratives" },
  { id: "cast" as RecommendationType, label: "Cast", icon: Users, description: "Same actors" },
  { id: "director" as RecommendationType, label: "Director", icon: Clapperboard, description: "Same filmmaker" },
  { id: "genre" as RecommendationType, label: "Genre", icon: Layers, description: "Same category" },
]

const LOADING_MESSAGES = [
  "Searching our film vault...",
  "Analyzing cinematic connections...",
  "Finding hidden gems...",
  "Curating your recommendations...",
]

export default function Home() {
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingRecommendations, setIsLoadingRecommendations] = useState(false)
  const [loadingMessage, setLoadingMessage] = useState(LOADING_MESSAGES[0])
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedLanguage, setSelectedLanguage] = useState("")
  const [selectedMovie, setSelectedMovie] = useState<Movie | null>(null)
  const [selectedMode, setSelectedMode] = useState<RecommendationType>("story")
  const [sourceMovie, setSourceMovie] = useState<Movie | null>(null)
  const [recommendations, setRecommendations] = useState<Movie[]>([])
  const [isFallbackResults, setIsFallbackResults] = useState(false)
  const [personInfo, setPersonInfo] = useState<{ id: number; name: string } | null>(null)
  const [searchResults, setSearchResults] = useState<Movie[]>([])

  // Simulate initial loading (data fetching from DB)
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 2500)
    return () => clearTimeout(timer)
  }, [])

  // Update search results when query changes
  useEffect(() => {
    if (searchQuery.trim()) {
      const results = searchMovies(searchQuery, selectedLanguage || undefined)
      setSearchResults(results)
    } else {
      setSearchResults([])
    }
  }, [searchQuery, selectedLanguage])

  // Cycle through loading messages
  useEffect(() => {
    if (!isLoadingRecommendations) return
    let index = 0
    const interval = setInterval(() => {
      index = (index + 1) % LOADING_MESSAGES.length
      setLoadingMessage(LOADING_MESSAGES[index])
    }, 1200)
    return () => clearInterval(interval)
  }, [isLoadingRecommendations])

  // Get recommendations when source movie and mode are selected
  const getRecommendations = async (movie: Movie, mode: RecommendationType) => {
    setIsLoadingRecommendations(true)
    setLoadingMessage(LOADING_MESSAGES[0])
    setIsFallbackResults(false)

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000))

    const credits = getCredits(movie.id)
    const director = credits?.crew?.find(c => c.job === "Director")
    const topCast = credits?.cast?.[0]

    let results: Movie[] = []
    let isFallback = false

    switch (mode) {
      case "story":
        results = getSimilarMovies(movie, selectedLanguage || undefined)
        setPersonInfo(null)
        break
      case "director":
        if (director) {
          results = getMoviesByDirector(director.id, movie.id, selectedLanguage || undefined)
          setPersonInfo({ id: director.id, name: director.name })
        }
        break
      case "cast":
        if (topCast) {
          results = getMoviesByCast(topCast.id, movie.id, selectedLanguage || undefined)
          setPersonInfo({ id: topCast.id, name: topCast.name })
        }
        break
      case "genre":
        results = getMoviesByGenreFromMovie(movie, selectedLanguage || undefined)
        setPersonInfo(null)
        break
    }

    // Check if movie wasn't in our main database - simulate fallback
    const isInDatabase = MOVIES.some(m => m.id === movie.id)
    if (!isInDatabase || results.length === 0) {
      // Provide fallback results - just grab some movies
      if (results.length === 0) {
        results = MOVIES.slice(0, 8)
        isFallback = true
      }
    }

    setRecommendations(results)
    setIsFallbackResults(isFallback)
    setIsLoadingRecommendations(false)
  }

  const handleSelectSourceMovie = (movie: Movie) => {
    setSourceMovie(movie)
    setSearchQuery(movie.title)
    setSearchResults([])
    getRecommendations(movie, selectedMode)
  }

  const handleModeChange = (mode: RecommendationType) => {
    setSelectedMode(mode)
    if (sourceMovie) {
      getRecommendations(sourceMovie, mode)
    }
  }

  const handleLanguageChange = (lang: string) => {
    setSelectedLanguage(lang)
    if (sourceMovie) {
      getRecommendations(sourceMovie, selectedMode)
    }
  }

  const clearAll = () => {
    setSourceMovie(null)
    setRecommendations([])
    setSearchQuery("")
    setSearchResults([])
    setPersonInfo(null)
    setIsFallbackResults(false)
  }

  const getRecommendationLabel = () => {
    if (!sourceMovie) return ""
    switch (selectedMode) {
      case "story":
        return `Movies similar to "${sourceMovie.title}"`
      case "cast":
        return personInfo ? `Movies starring ${personInfo.name}` : `Movies with same cast as "${sourceMovie.title}"`
      case "director":
        return personInfo ? `Movies directed by ${personInfo.name}` : `Movies by same director as "${sourceMovie.title}"`
      case "genre":
        return `Movies in the same genre as "${sourceMovie.title}"`
    }
  }

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <div className="min-h-screen bg-stone-100">
      {/* Header */}
      <header className="sticky top-0 z-40 bg-stone-100/95 backdrop-blur-sm border-b border-stone-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4">
          <div className="flex items-center justify-between gap-4">
            <button onClick={clearAll} className="flex items-center gap-2 group">
              <div className="w-10 h-10 rounded-full bg-amber-600 flex items-center justify-center">
                <Film className="w-5 h-5 text-white" />
              </div>
              <span className="font-serif text-2xl text-stone-800 group-hover:text-amber-700 transition-colors hidden sm:block">
                Filmory
              </span>
            </button>

            {/* Language filter in header */}
            <select
              value={selectedLanguage}
              onChange={(e) => handleLanguageChange(e.target.value)}
              disabled={isLoadingRecommendations}
              className="hidden sm:block px-3 py-2 bg-white border border-stone-300 rounded-lg text-sm text-stone-700 focus:outline-none focus:border-amber-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <option value="">All Languages</option>
              {LANGUAGES.map(lang => (
                <option key={lang.iso_639_1} value={lang.iso_639_1}>
                  {lang.english_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-8">
        {/* Hero / Search Section */}
        <div className="text-center mb-10">
          <h1 className="font-serif text-4xl sm:text-5xl text-stone-800 mb-3 text-balance">
            Find Your Next Favorite Film
          </h1>
          <p className="text-stone-500 text-lg max-w-xl mx-auto">
            Search for a movie you love, choose how you want to explore, and discover perfect recommendations.
          </p>
        </div>

        {/* Search Input */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-stone-400" />
            <input
              type="text"
              placeholder="Enter a movie name..."
              value={searchQuery}
              disabled={isLoadingRecommendations}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                if (sourceMovie && e.target.value !== sourceMovie.title) {
                  setSourceMovie(null)
                  setRecommendations([])
                  setIsFallbackResults(false)
                }
              }}
              className="w-full pl-12 pr-4 py-4 bg-white border border-stone-300 rounded-2xl text-stone-800 text-lg placeholder:text-stone-400 focus:outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
            />
            {searchQuery && !isLoadingRecommendations && (
              <button 
                onClick={clearAll}
                className="absolute right-4 top-1/2 -translate-y-1/2 p-1 hover:bg-stone-100 rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-stone-400" />
              </button>
            )}
          </div>

          {/* Search Results Dropdown */}
          {searchResults.length > 0 && !sourceMovie && (
            <div className="mt-2 bg-white border border-stone-200 rounded-xl shadow-lg overflow-hidden max-h-80 overflow-y-auto">
              {searchResults.map(movie => (
                <button
                  key={movie.id}
                  onClick={() => handleSelectSourceMovie(movie)}
                  className="w-full flex items-center gap-4 p-3 hover:bg-amber-50 transition-colors text-left border-b border-stone-100 last:border-b-0"
                >
                  <div className="w-12 h-16 rounded bg-stone-200 overflow-hidden shrink-0">
                    {movie.poster_path && (
                      <img 
                        src={`https://image.tmdb.org/t/p/w92${movie.poster_path}`}
                        alt={movie.title}
                        className="w-full h-full object-cover"
                      />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-stone-800 truncate">{movie.title}</p>
                    <p className="text-sm text-stone-500">
                      {movie.release_date ? new Date(movie.release_date).getFullYear() : "N/A"}
                      {movie.vote_average > 0 && ` • ${movie.vote_average.toFixed(1)} rating`}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Mobile Language Filter */}
          <div className="sm:hidden mt-4">
            <select
              value={selectedLanguage}
              onChange={(e) => handleLanguageChange(e.target.value)}
              disabled={isLoadingRecommendations}
              className="w-full px-3 py-2 bg-white border border-stone-300 rounded-lg text-sm text-stone-700 focus:outline-none focus:border-amber-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <option value="">All Languages</option>
              {LANGUAGES.map(lang => (
                <option key={lang.iso_639_1} value={lang.iso_639_1}>
                  {lang.english_name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Recommendation Mode Selector */}
        <div className="max-w-3xl mx-auto mb-10">
          <p className="text-center text-stone-500 text-sm mb-4">Choose recommendation mode</p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {RECOMMENDATION_MODES.map(mode => {
              const Icon = mode.icon
              const isActive = selectedMode === mode.id
              return (
                <button
                  key={mode.id}
                  onClick={() => handleModeChange(mode.id)}
                  disabled={isLoadingRecommendations}
                  className={`p-4 rounded-xl border-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed ${
                    isActive 
                      ? "border-amber-500 bg-amber-50" 
                      : "border-stone-200 bg-white hover:border-amber-300 hover:bg-amber-50/50"
                  }`}
                >
                  <Icon className={`w-6 h-6 mx-auto mb-2 ${isActive ? "text-amber-600" : "text-stone-400"}`} />
                  <p className={`font-medium text-sm ${isActive ? "text-amber-700" : "text-stone-700"}`}>
                    {mode.label}
                  </p>
                  <p className="text-xs text-stone-400 mt-1 hidden sm:block">{mode.description}</p>
                </button>
              )
            })}
          </div>
        </div>

        {/* Loading State for Recommendations */}
        {isLoadingRecommendations && (
          <div className="py-20 text-center">
            <div className="inline-flex flex-col items-center gap-4">
              <div className="relative">
                <div className="w-16 h-16 rounded-full bg-amber-100 flex items-center justify-center">
                  <Spinner className="w-8 h-8 text-amber-600" />
                </div>
                <div className="absolute inset-0 rounded-full border-2 border-amber-300 animate-ping opacity-30" />
              </div>
              <div>
                <p className="text-stone-700 font-medium text-lg">{loadingMessage}</p>
                <p className="text-stone-400 text-sm mt-1">This may take a moment</p>
              </div>
            </div>
          </div>
        )}

        {/* Results Section */}
        {sourceMovie && recommendations.length > 0 && !isLoadingRecommendations && (
          <>
            {/* Fallback Notice */}
            {isFallbackResults && (
              <div className="mb-4 p-4 bg-stone-200/60 border border-stone-300 rounded-xl flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-stone-500 shrink-0 mt-0.5" />
                <div>
                  <p className="text-stone-700 font-medium text-sm">Limited match for this title</p>
                  <p className="text-stone-500 text-sm mt-0.5">
                    We couldn&apos;t find an exact match for &quot;{sourceMovie.title}&quot; in our database. 
                    The recommendations below are based on general popularity and may not be closely related to your selection.
                  </p>
                </div>
              </div>
            )}

            {/* Recommendation banner */}
            <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Sparkles className="w-5 h-5 text-amber-600" />
                <span className="text-amber-800 font-medium">{getRecommendationLabel()}</span>
              </div>
              <button
                onClick={clearAll}
                className="p-1.5 hover:bg-amber-100 rounded-full transition-colors"
              >
                <X className="w-4 h-4 text-amber-700" />
              </button>
            </div>

            {/* Movie grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 sm:gap-6">
              {recommendations.map((movie) => (
                <MovieCard 
                  key={movie.id} 
                  movie={movie} 
                  onClick={setSelectedMovie}
                />
              ))}
            </div>
          </>
        )}

        {/* Empty state - when no source movie selected */}
        {!sourceMovie && !searchQuery && !isLoadingRecommendations && (
          <div className="text-center py-16">
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-stone-200 flex items-center justify-center">
              <Film className="w-10 h-10 text-stone-400" />
            </div>
            <h3 className="font-serif text-2xl text-stone-700 mb-2">Start Your Discovery</h3>
            <p className="text-stone-500 max-w-md mx-auto">
              Enter a movie you enjoy in the search box above, select your preferred recommendation mode, and we&apos;ll find similar films for you.
            </p>
          </div>
        )}

        {/* No results state */}
        {sourceMovie && recommendations.length === 0 && !isLoadingRecommendations && (
          <div className="text-center py-16">
            <Film className="w-16 h-16 text-stone-300 mx-auto mb-4" />
            <p className="text-stone-500 text-lg">No recommendations found</p>
            <p className="text-stone-400 mt-1">Try a different mode or language filter</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-stone-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-8 text-center text-stone-500 text-sm">
          <p>Built with love for film enthusiasts.</p>
        </div>
      </footer>

      {/* Movie detail modal */}
      {selectedMovie && (
        <MovieDetail
          movie={selectedMovie}
          onClose={() => setSelectedMovie(null)}
          onRecommend={(movie, type) => {
            setSelectedMovie(null)
            setSourceMovie(movie)
            setSearchQuery(movie.title)
            setSelectedMode(type)
            getRecommendations(movie, type)
          }}
        />
      )}
    </div>
  )
}
