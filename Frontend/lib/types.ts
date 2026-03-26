export interface Movie {
  id: number
  title: string
  poster_path: string | null
  backdrop_path: string | null
  overview: string
  release_date: string
  vote_average: number
  vote_count: number
  original_language: string
  genre_ids?: number[]
  genres?: Genre[]
}

export interface Genre {
  id: number
  name: string
}

export interface Person {
  id: number
  name: string
  profile_path: string | null
  known_for_department: string
}

export interface CastMember extends Person {
  character: string
  order: number
}

export interface CrewMember extends Person {
  job: string
  department: string
}

export interface Credits {
  cast: CastMember[]
  crew: CrewMember[]
}

export interface Language {
  iso_639_1: string
  english_name: string
  name: string
}

export type RecommendationType = "story" | "cast" | "director" | "genre"
