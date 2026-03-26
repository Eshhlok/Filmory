import type { Movie, Genre, Language, CastMember, CrewMember } from "./types"

export const GENRES: Genre[] = [
  { id: 28, name: "Action" },
  { id: 12, name: "Adventure" },
  { id: 16, name: "Animation" },
  { id: 35, name: "Comedy" },
  { id: 80, name: "Crime" },
  { id: 18, name: "Drama" },
  { id: 14, name: "Fantasy" },
  { id: 27, name: "Horror" },
  { id: 10749, name: "Romance" },
  { id: 878, name: "Science Fiction" },
  { id: 53, name: "Thriller" },
  { id: 10752, name: "War" },
]

export const LANGUAGES: Language[] = [
  { iso_639_1: "en", english_name: "English", name: "English" },
  { iso_639_1: "es", english_name: "Spanish", name: "Español" },
  { iso_639_1: "fr", english_name: "French", name: "Français" },
  { iso_639_1: "de", english_name: "German", name: "Deutsch" },
  { iso_639_1: "ja", english_name: "Japanese", name: "日本語" },
  { iso_639_1: "ko", english_name: "Korean", name: "한국어" },
  { iso_639_1: "zh", english_name: "Chinese", name: "中文" },
  { iso_639_1: "hi", english_name: "Hindi", name: "हिन्दी" },
  { iso_639_1: "it", english_name: "Italian", name: "Italiano" },
  { iso_639_1: "pt", english_name: "Portuguese", name: "Português" },
]

export const MOVIES: Movie[] = [
  {
    id: 1,
    title: "Inception",
    poster_path: "/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
    backdrop_path: "/8ZTVqvKDQ8emSGUEMjsS4yHAwrp.jpg",
    overview: "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets is offered a chance to regain his old life as payment for a task considered to be impossible: inception.",
    release_date: "2010-07-16",
    vote_average: 8.4,
    vote_count: 35000,
    original_language: "en",
    genre_ids: [28, 878, 12],
    genres: [{ id: 28, name: "Action" }, { id: 878, name: "Science Fiction" }, { id: 12, name: "Adventure" }]
  },
  {
    id: 2,
    title: "The Shawshank Redemption",
    poster_path: "/9cqNxx0GxF0bflZmeSMuL5tnGzr.jpg",
    backdrop_path: "/kXfqcdQKsToO0OUXHcrrNCHDBzO.jpg",
    overview: "Framed in the 1940s for the double murder of his wife and her lover, upstanding banker Andy Dufresne begins a new life at the Shawshank prison, where he puts his accounting skills to work for an pointy warden.",
    release_date: "1994-09-23",
    vote_average: 8.7,
    vote_count: 26000,
    original_language: "en",
    genre_ids: [18, 80],
    genres: [{ id: 18, name: "Drama" }, { id: 80, name: "Crime" }]
  },
  {
    id: 3,
    title: "Parasite",
    poster_path: "/7IiTTgloJzvGI1TAYymCfbfl3vT.jpg",
    backdrop_path: "/TU9NIjwzjoKPwQHoHshkFcQUCG.jpg",
    overview: "All unemployed, Ki-taek family takes peculiar interest in the wealthy and glamorous Parks for their livelihood until they get entangled in an unexpected incident.",
    release_date: "2019-05-30",
    vote_average: 8.5,
    vote_count: 18000,
    original_language: "ko",
    genre_ids: [35, 53, 18],
    genres: [{ id: 35, name: "Comedy" }, { id: 53, name: "Thriller" }, { id: 18, name: "Drama" }]
  },
  {
    id: 4,
    title: "Interstellar",
    poster_path: "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
    backdrop_path: "/xJHokMbljvjADYdit5fK5VQsXEG.jpg",
    overview: "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel and conquer the vast distances involved in an interstellar voyage.",
    release_date: "2014-11-05",
    vote_average: 8.4,
    vote_count: 34000,
    original_language: "en",
    genre_ids: [12, 18, 878],
    genres: [{ id: 12, name: "Adventure" }, { id: 18, name: "Drama" }, { id: 878, name: "Science Fiction" }]
  },
  {
    id: 5,
    title: "The Dark Knight",
    poster_path: "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
    backdrop_path: "/nMKdUUepR0i5zn0y1T4CsSB5chy.jpg",
    overview: "Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets.",
    release_date: "2008-07-16",
    vote_average: 8.5,
    vote_count: 32000,
    original_language: "en",
    genre_ids: [18, 28, 80, 53],
    genres: [{ id: 18, name: "Drama" }, { id: 28, name: "Action" }, { id: 80, name: "Crime" }, { id: 53, name: "Thriller" }]
  },
  {
    id: 6,
    title: "Pulp Fiction",
    poster_path: "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
    backdrop_path: "/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
    overview: "A burger-loving hit man, his philosophical partner, a drug-addled gangster moll and a washed-up boxer converge in this sprawling, comedic crime caper.",
    release_date: "1994-09-10",
    vote_average: 8.5,
    vote_count: 27000,
    original_language: "en",
    genre_ids: [53, 80],
    genres: [{ id: 53, name: "Thriller" }, { id: 80, name: "Crime" }]
  },
  {
    id: 7,
    title: "Spirited Away",
    poster_path: "/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
    backdrop_path: "/6oaL4DP75yABrd5EbC4H2zq5ghc.jpg",
    overview: "A young girl, Chihiro, becomes trapped in a strange new world of spirits. When her parents undergo a mysterious transformation, she must call upon the courage she never knew she had.",
    release_date: "2001-07-20",
    vote_average: 8.5,
    vote_count: 16000,
    original_language: "ja",
    genre_ids: [16, 14, 12],
    genres: [{ id: 16, name: "Animation" }, { id: 14, name: "Fantasy" }, { id: 12, name: "Adventure" }]
  },
  {
    id: 8,
    title: "Fight Club",
    poster_path: "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
    backdrop_path: "/hZkgoQYus5vegHoetLkCJzb17zJ.jpg",
    overview: "A ticking-Loss bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy. Their concept catches on, with underground fight clubs forming in every town.",
    release_date: "1999-10-15",
    vote_average: 8.4,
    vote_count: 28000,
    original_language: "en",
    genre_ids: [18, 53, 35],
    genres: [{ id: 18, name: "Drama" }, { id: 53, name: "Thriller" }, { id: 35, name: "Comedy" }]
  },
  {
    id: 9,
    title: "The Matrix",
    poster_path: "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg",
    backdrop_path: "/fNG7i7RqMErkcqhohV2a6cV1Ehy.jpg",
    overview: "Set in the 22nd century, The Matrix tells the story of a computer hacker who joins a group of underground insurgents fighting the vast and powerful computers who now rule the earth.",
    release_date: "1999-03-30",
    vote_average: 8.2,
    vote_count: 25000,
    original_language: "en",
    genre_ids: [28, 878],
    genres: [{ id: 28, name: "Action" }, { id: 878, name: "Science Fiction" }]
  },
  {
    id: 10,
    title: "Oppenheimer",
    poster_path: "/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg",
    backdrop_path: "/rLb2cwF3Pazuxaj0sRXQ037tGI1.jpg",
    overview: "The story of J. Robert Oppenheimer journey from his role in the Manhattan Project to his controversial fall from grace during the McCarthy era.",
    release_date: "2023-07-19",
    vote_average: 8.1,
    vote_count: 8500,
    original_language: "en",
    genre_ids: [18, 36],
    genres: [{ id: 18, name: "Drama" }, { id: 36, name: "History" }]
  },
  {
    id: 11,
    title: "Your Name",
    poster_path: "/q719jXXEzOoYaps6babgKnONONX.jpg",
    backdrop_path: "/dIWwZW7dJJtqC6CgWzYkNVKIUm8.jpg",
    overview: "High schoolers Mitsuha and Taki are complete strangers living separate lives. But one night, they suddenly switch places. This bizarre occurrence continues to happen randomly.",
    release_date: "2016-08-26",
    vote_average: 8.5,
    vote_count: 11000,
    original_language: "ja",
    genre_ids: [16, 10749, 18],
    genres: [{ id: 16, name: "Animation" }, { id: 10749, name: "Romance" }, { id: 18, name: "Drama" }]
  },
  {
    id: 12,
    title: "The Godfather",
    poster_path: "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
    backdrop_path: "/tmU7GeKVybMWFButWEGl2M4GeiP.jpg",
    overview: "Spanning the years 1945 to 1955, a chronicle of the fictional Italian-American Corleone crime family. When organized crime family patriarch Vito Corleone barely survives an attempt on his life.",
    release_date: "1972-03-14",
    vote_average: 8.7,
    vote_count: 20000,
    original_language: "en",
    genre_ids: [18, 80],
    genres: [{ id: 18, name: "Drama" }, { id: 80, name: "Crime" }]
  },
  {
    id: 13,
    title: "Dune",
    poster_path: "/d5NXSklXo0qyIYkgV94XAgMIckC.jpg",
    backdrop_path: "/jYEW5xZkZk2WTrdbMGAPFuBqbDc.jpg",
    overview: "Paul Atreides, a brilliant and gifted young man born into a great destiny beyond his understanding, must travel to the most dangerous planet in the universe to ensure the future of his family and his people.",
    release_date: "2021-09-15",
    vote_average: 7.8,
    vote_count: 12000,
    original_language: "en",
    genre_ids: [878, 12],
    genres: [{ id: 878, name: "Science Fiction" }, { id: 12, name: "Adventure" }]
  },
  {
    id: 14,
    title: "Everything Everywhere All at Once",
    poster_path: "/w3LxiVYdWWRvEVdn5RYq6jIqkb1.jpg",
    backdrop_path: "/fOy2Jurz9k6RnJnMUMRDAgBwru2.jpg",
    overview: "An aging Chinese immigrant is swept up in an insane adventure, where she alone can save what is important to her by connecting with the lives she could have led in other universes.",
    release_date: "2022-03-11",
    vote_average: 7.8,
    vote_count: 9500,
    original_language: "en",
    genre_ids: [28, 12, 878],
    genres: [{ id: 28, name: "Action" }, { id: 12, name: "Adventure" }, { id: 878, name: "Science Fiction" }]
  },
  {
    id: 15,
    title: "Whiplash",
    poster_path: "/6uSPcdGNA2A6vJmCagXkvnutegs.jpg",
    backdrop_path: "/fRGxZuo7jJUWQsVg9PREb98Aclp.jpg",
    overview: "Under the direction of a ruthless instructor, a talented young drummer begins to pursue perfection at any cost, even his humanity.",
    release_date: "2014-10-10",
    vote_average: 8.4,
    vote_count: 15000,
    original_language: "en",
    genre_ids: [18, 10402],
    genres: [{ id: 18, name: "Drama" }, { id: 10402, name: "Music" }]
  },
  {
    id: 16,
    title: "The Grand Budapest Hotel",
    poster_path: "/eWdyYQreja6JGCzqHWXpWHDrrPo.jpg",
    backdrop_path: "/nX5XotM9yprCKarRH4fzOq1VM1J.jpg",
    overview: "The Grand Budapest Hotel recounts the adventures of Gustave H, a legendary concierge at a famous European hotel between the wars, and Zero Moustafa, the lobby boy who becomes his most trusted friend.",
    release_date: "2014-02-26",
    vote_average: 8.1,
    vote_count: 13000,
    original_language: "en",
    genre_ids: [35, 18],
    genres: [{ id: 35, name: "Comedy" }, { id: 18, name: "Drama" }]
  },
  {
    id: 17,
    title: "Oldboy",
    poster_path: "/pWDtjs568ZfOTMbURQBYuT4Qxka.jpg",
    backdrop_path: "/2qlx7o5cRj23Snp5LRa8p6yWYPR.jpg",
    overview: "With no clue how he came to be imprisoned, drugged and tortured for 15 years, a desperate businessman seeks revenge on his captors.",
    release_date: "2003-11-21",
    vote_average: 8.4,
    vote_count: 11000,
    original_language: "ko",
    genre_ids: [53, 18, 9648],
    genres: [{ id: 53, name: "Thriller" }, { id: 18, name: "Drama" }, { id: 9648, name: "Mystery" }]
  },
  {
    id: 18,
    title: "La La Land",
    poster_path: "/uDO8zWDhfWwoFdKS4fzkUJt0Rf0.jpg",
    backdrop_path: "/nadTlnTE6DdgmYsN4iWc2a2wiaI.jpg",
    overview: "Mia, an aspiring actress, serves lattes to movie stars in between auditions and Sebastian, a jazz musician, scrapes by playing cocktail party gigs in dingy bars.",
    release_date: "2016-11-29",
    vote_average: 7.9,
    vote_count: 16000,
    original_language: "en",
    genre_ids: [35, 18, 10749, 10402],
    genres: [{ id: 35, name: "Comedy" }, { id: 18, name: "Drama" }, { id: 10749, name: "Romance" }, { id: 10402, name: "Music" }]
  },
  {
    id: 19,
    title: "Amélie",
    poster_path: "/nSxDa3ppafARKIFSQhpYNS6khLw.jpg",
    backdrop_path: "/aw4FOsWr2FY373nKSxbpNi3fz4F.jpg",
    overview: "At a tiny Parisian café, the adorable yet painfully shy Amélie accidentally discovers a remarkable gift for helping others. Soon Amélie is spending her days as a matchmaker and guardian angel.",
    release_date: "2001-04-25",
    vote_average: 7.9,
    vote_count: 13000,
    original_language: "fr",
    genre_ids: [35, 10749],
    genres: [{ id: 35, name: "Comedy" }, { id: 10749, name: "Romance" }]
  },
  {
    id: 20,
    title: "The Prestige",
    poster_path: "/tRNlZbgNCNOpLpbPEz5L8G8A0JN.jpg",
    backdrop_path: "/c6YJvxbE0dUXKjJYlUn5kMJGqJG.jpg",
    overview: "A mysterious story of two magicians whose intense rivalry leads them on a life-long battle for supremacy full of obsession, deceit and jealousy with dangerous consequences.",
    release_date: "2006-10-19",
    vote_average: 8.2,
    vote_count: 16000,
    original_language: "en",
    genre_ids: [18, 9648, 53],
    genres: [{ id: 18, name: "Drama" }, { id: 9648, name: "Mystery" }, { id: 53, name: "Thriller" }]
  },
]

export const MOVIE_CREDITS: Record<number, { cast: CastMember[], crew: CrewMember[] }> = {
  1: {
    cast: [
      { id: 6193, name: "Leonardo DiCaprio", profile_path: "/wo2hJpn04vbtmh0B9utCFdsQhxM.jpg", known_for_department: "Acting", character: "Cobb", order: 0 },
      { id: 24045, name: "Joseph Gordon-Levitt", profile_path: "/dhv9f3AaozOjpvjAwVzOWlmmT2V.jpg", known_for_department: "Acting", character: "Arthur", order: 1 },
      { id: 2524, name: "Tom Hardy", profile_path: "/d81K0RH8UX7tZj49tZaQhZ9ewH.jpg", known_for_department: "Acting", character: "Eames", order: 2 },
      { id: 27578, name: "Elliot Page", profile_path: "/bLAT0rTuBvwrGT4cNJZrqaz8l6s.jpg", known_for_department: "Acting", character: "Ariadne", order: 3 },
      { id: 3899, name: "Ken Watanabe", profile_path: "/psAXOYp9SBOXvg6AXzARDedNQ9P.jpg", known_for_department: "Acting", character: "Saito", order: 4 },
    ],
    crew: [
      { id: 525, name: "Christopher Nolan", profile_path: "/xuAIuYSmsUzKlUMBFGVZaWsY3DZ.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  2: {
    cast: [
      { id: 504, name: "Tim Robbins", profile_path: "/djLVFETFTvPyVUdrd7aLVykobof.jpg", known_for_department: "Acting", character: "Andy Dufresne", order: 0 },
      { id: 192, name: "Morgan Freeman", profile_path: "/jPsLqiYGSofU4s6BjrxnefMfabb.jpg", known_for_department: "Acting", character: "Ellis Boyd Redding", order: 1 },
    ],
    crew: [
      { id: 4027, name: "Frank Darabont", profile_path: "/nvGkINsoKk9Dcr8c1UxjkmQJkuI.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  3: {
    cast: [
      { id: 20738, name: "Song Kang-ho", profile_path: "/ceezbukNFi4MWKF7HiDmMr9TghB.jpg", known_for_department: "Acting", character: "Kim Ki-taek", order: 0 },
      { id: 84495, name: "Lee Sun-kyun", profile_path: "/x7x3lqp5tjrAyULLIWLAL7F0ozX.jpg", known_for_department: "Acting", character: "Park Dong-ik", order: 1 },
    ],
    crew: [
      { id: 21684, name: "Bong Joon-ho", profile_path: "/tKLJBqbdH6HFj2QxLA5o8Zk7IVs.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  4: {
    cast: [
      { id: 10297, name: "Matthew McConaughey", profile_path: "/sY2mwpafcwqyYS1sOySu1MENDz.jpg", known_for_department: "Acting", character: "Cooper", order: 0 },
      { id: 1813, name: "Anne Hathaway", profile_path: "/tLelKoPNiyJCSEtQTz1FGv4TLGc.jpg", known_for_department: "Acting", character: "Brand", order: 1 },
      { id: 83002, name: "Jessica Chastain", profile_path: "/lodMzLKSdrPcBry6TdoDsMN3Vge.jpg", known_for_department: "Acting", character: "Murph", order: 2 },
    ],
    crew: [
      { id: 525, name: "Christopher Nolan", profile_path: "/xuAIuYSmsUzKlUMBFGVZaWsY3DZ.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  5: {
    cast: [
      { id: 3894, name: "Christian Bale", profile_path: "/qCpZn2e3dimwbryLnqxZuI88PTi.jpg", known_for_department: "Acting", character: "Bruce Wayne / Batman", order: 0 },
      { id: 1810, name: "Heath Ledger", profile_path: "/5Y9HnYYa9jF4NunY9lSgJGjSe8E.jpg", known_for_department: "Acting", character: "Joker", order: 1 },
      { id: 5132, name: "Aaron Eckhart", profile_path: "/nPt8bDTJ9ygNAg7qp6QRZLU32ij.jpg", known_for_department: "Acting", character: "Harvey Dent", order: 2 },
    ],
    crew: [
      { id: 525, name: "Christopher Nolan", profile_path: "/xuAIuYSmsUzKlUMBFGVZaWsY3DZ.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  6: {
    cast: [
      { id: 8891, name: "John Travolta", profile_path: "/ns8uZHEHzV18ifqA9secv8c2Ard.jpg", known_for_department: "Acting", character: "Vincent Vega", order: 0 },
      { id: 2231, name: "Samuel L. Jackson", profile_path: "/nCJJ3NVksYNxIzEHcyC1XziwPVj.jpg", known_for_department: "Acting", character: "Jules Winnfield", order: 1 },
      { id: 139, name: "Uma Thurman", profile_path: "/wRoWbfPBfXeQXZbjJj75PDXKRu8.jpg", known_for_department: "Acting", character: "Mia Wallace", order: 2 },
    ],
    crew: [
      { id: 138, name: "Quentin Tarantino", profile_path: "/1gjcpAa99FAOWGnrUvHEXXsRs7o.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  7: {
    cast: [
      { id: 1253350, name: "Rumi Hiiragi", profile_path: "/zITaVtfyc4xSM3hNWOvJjaXm0je.jpg", known_for_department: "Acting", character: "Chihiro (voice)", order: 0 },
      { id: 1254, name: "Miyu Irino", profile_path: "/cXrdC4LxqtK4wDVnxLfbHHX33Q6.jpg", known_for_department: "Acting", character: "Haku (voice)", order: 1 },
    ],
    crew: [
      { id: 608, name: "Hayao Miyazaki", profile_path: "/mG3cfxtA5jqDc7fpKgyzZMKbtLD.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  8: {
    cast: [
      { id: 287, name: "Brad Pitt", profile_path: "/oTB9vGIBFH4tNrYDQ9Dq1xFnqXE.jpg", known_for_department: "Acting", character: "Tyler Durden", order: 0 },
      { id: 819, name: "Edward Norton", profile_path: "/8nytsqL59SFJTVYVrN72k6qkGgJ.jpg", known_for_department: "Acting", character: "The Narrator", order: 1 },
      { id: 1283, name: "Helena Bonham Carter", profile_path: "/DDeITcCpnBd0CkAIRPhggy9bt5.jpg", known_for_department: "Acting", character: "Marla Singer", order: 2 },
    ],
    crew: [
      { id: 7467, name: "David Fincher", profile_path: "/tpEczFHQFpSEHfxgprGymOxvsGV.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  9: {
    cast: [
      { id: 6384, name: "Keanu Reeves", profile_path: "/4D0PpNI0kmP58hgrwGC3wCjxhnm.jpg", known_for_department: "Acting", character: "Thomas A. Anderson / Neo", order: 0 },
      { id: 2975, name: "Laurence Fishburne", profile_path: "/8suOhUmPbfKqDQ17jQ1Gy0mI3P4.jpg", known_for_department: "Acting", character: "Morpheus", order: 1 },
      { id: 530, name: "Carrie-Anne Moss", profile_path: "/xD4jTA3KhBTE4Qywasr4t1JRnzn.jpg", known_for_department: "Acting", character: "Trinity", order: 2 },
    ],
    crew: [
      { id: 9340, name: "The Wachowskis", profile_path: null, known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  10: {
    cast: [
      { id: 2037, name: "Cillian Murphy", profile_path: "/dm6V24NjjvjMiCtbMkc8Y2GOkBx.jpg", known_for_department: "Acting", character: "J. Robert Oppenheimer", order: 0 },
      { id: 5293, name: "Emily Blunt", profile_path: "/5nCSG5TL1bP1geD8aaBfaLnLLCD.jpg", known_for_department: "Acting", character: "Kitty Oppenheimer", order: 1 },
      { id: 1892, name: "Matt Damon", profile_path: "/At3JgvaNeEN4Z4ESKlhhes85Xo3.jpg", known_for_department: "Acting", character: "Leslie Groves", order: 2 },
    ],
    crew: [
      { id: 525, name: "Christopher Nolan", profile_path: "/xuAIuYSmsUzKlUMBFGVZaWsY3DZ.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  11: {
    cast: [
      { id: 1117329, name: "Ryunosuke Kamiki", profile_path: "/4n6POH0zVJOEfgjDfALa7HyoB1E.jpg", known_for_department: "Acting", character: "Taki Tachibana (voice)", order: 0 },
      { id: 1268019, name: "Mone Kamishiraishi", profile_path: "/ksTqcJgwlb5WLbJLNIQb9g2TVJu.jpg", known_for_department: "Acting", character: "Mitsuha Miyamizu (voice)", order: 1 },
    ],
    crew: [
      { id: 94417, name: "Makoto Shinkai", profile_path: "/vAR6bz34QCJ8lTpUe5Ld1K7f2W.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  12: {
    cast: [
      { id: 3084, name: "Marlon Brando", profile_path: "/fuTEPMsBtV1zE98ujPONbKiYDc2.jpg", known_for_department: "Acting", character: "Don Vito Corleone", order: 0 },
      { id: 1158, name: "Al Pacino", profile_path: "/2dGBb1fOcNdZjtQToVPFxXjm4ke.jpg", known_for_department: "Acting", character: "Michael Corleone", order: 1 },
    ],
    crew: [
      { id: 1776, name: "Francis Ford Coppola", profile_path: "/3lTtuBWLhqrqNmOqTXmLd3BvkxU.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  13: {
    cast: [
      { id: 1190668, name: "Timothée Chalamet", profile_path: "/BE2sdjpgsa2rNTFa66f7upkaOP.jpg", known_for_department: "Acting", character: "Paul Atreides", order: 0 },
      { id: 933238, name: "Rebecca Ferguson", profile_path: "/lJloTOheuQSirSLXNA3JHsrMNfH.jpg", known_for_department: "Acting", character: "Lady Jessica", order: 1 },
      { id: 25072, name: "Oscar Isaac", profile_path: "/dW5U5yrIIPmMjRThR9KT2xH6nTz.jpg", known_for_department: "Acting", character: "Duke Leto Atreides", order: 2 },
    ],
    crew: [
      { id: 137427, name: "Denis Villeneuve", profile_path: "/zdDx9Xs93UIrJFWYApYR28J8M6b.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  14: {
    cast: [
      { id: 1625558, name: "Michelle Yeoh", profile_path: "/6gHJ3LHxDhgpyaUyD7f8JaP5S5t.jpg", known_for_department: "Acting", character: "Evelyn Wang", order: 0 },
      { id: 1625558, name: "Stephanie Hsu", profile_path: "/8gb3lfIHKQAGOQyeqnRwzJlAaXD.jpg", known_for_department: "Acting", character: "Joy Wang / Jobu Tupaki", order: 1 },
      { id: 1621, name: "Ke Huy Quan", profile_path: "/5LzHCdConCqbKwSCHjyIMYWzDcH.jpg", known_for_department: "Acting", character: "Waymond Wang", order: 2 },
    ],
    crew: [
      { id: 1280071, name: "Daniel Kwan", profile_path: "/aQqXqAKBR0qTvXIHvRQKz8xXQZt.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  15: {
    cast: [
      { id: 1373737, name: "Miles Teller", profile_path: "/cg1v5qqeuLr1VciDYZwc0YHObZ4.jpg", known_for_department: "Acting", character: "Andrew Neiman", order: 0 },
      { id: 49265, name: "J.K. Simmons", profile_path: "/ScmKoJ9eiSUOthAt1PDNAcjYVE.jpg", known_for_department: "Acting", character: "Terence Fletcher", order: 1 },
    ],
    crew: [
      { id: 136532, name: "Damien Chazelle", profile_path: "/jrAOvxb6PA7ALf54AQ8F1sJEvw2.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  16: {
    cast: [
      { id: 5530, name: "Ralph Fiennes", profile_path: "/1pG1JTLSKjmqjDvpY3SHY98J3PZ.jpg", known_for_department: "Acting", character: "M. Gustave", order: 0 },
      { id: 505710, name: "Tony Revolori", profile_path: "/8eTtJ7XVXY0BnEHX79uTILgkNJC.jpg", known_for_department: "Acting", character: "Zero Moustafa", order: 1 },
    ],
    crew: [
      { id: 5655, name: "Wes Anderson", profile_path: "/AoOlJTJLzuJj4NjJHaVrjLmM7wL.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  17: {
    cast: [
      { id: 10071, name: "Choi Min-sik", profile_path: "/lV9Gg4hQfJiP41UeCCmJCT3zYw.jpg", known_for_department: "Acting", character: "Oh Dae-su", order: 0 },
    ],
    crew: [
      { id: 10099, name: "Park Chan-wook", profile_path: "/kDPMmJVYyL8lC9Pzr2KhbyHBxCh.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  18: {
    cast: [
      { id: 30614, name: "Ryan Gosling", profile_path: "/lyUyVARQKhGxaxy0FbPJCQRpiaW.jpg", known_for_department: "Acting", character: "Sebastian", order: 0 },
      { id: 1903, name: "Emma Stone", profile_path: "/2hwXbPW2ffnXUe1Um0WXHG0cTwb.jpg", known_for_department: "Acting", character: "Mia", order: 1 },
    ],
    crew: [
      { id: 136532, name: "Damien Chazelle", profile_path: "/jrAOvxb6PA7ALf54AQ8F1sJEvw2.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  19: {
    cast: [
      { id: 15277, name: "Audrey Tautou", profile_path: "/czLnCZv3FYb8JMzuNJT1aI1jzi2.jpg", known_for_department: "Acting", character: "Amélie Poulain", order: 0 },
    ],
    crew: [
      { id: 2662, name: "Jean-Pierre Jeunet", profile_path: "/7Jqc5pROCb5TqRZOTWNJ1c1cEGI.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
  20: {
    cast: [
      { id: 17419, name: "Hugh Jackman", profile_path: "/oX6CpXmnXCHLarAqFWh0o1BGxSr.jpg", known_for_department: "Acting", character: "Robert Angier", order: 0 },
      { id: 3894, name: "Christian Bale", profile_path: "/qCpZn2e3dimwbryLnqxZuI88PTi.jpg", known_for_department: "Acting", character: "Alfred Borden", order: 1 },
      { id: 1920, name: "Scarlett Johansson", profile_path: "/6bBCPmc55gzP7TR9Rhl2EPlpFMZ.jpg", known_for_department: "Acting", character: "Olivia Wenscombe", order: 2 },
    ],
    crew: [
      { id: 525, name: "Christopher Nolan", profile_path: "/xuAIuYSmsUzKlUMBFGVZaWsY3DZ.jpg", known_for_department: "Directing", job: "Director", department: "Directing" },
    ]
  },
}

// Helper functions
export function searchMovies(query: string, language?: string): Movie[] {
  const q = query.toLowerCase()
  let results = MOVIES.filter(m => 
    m.title.toLowerCase().includes(q) || 
    m.overview.toLowerCase().includes(q)
  )
  if (language) {
    results = results.filter(m => m.original_language === language)
  }
  return results
}

export function getMoviesByGenre(genreId: number, language?: string): Movie[] {
  let results = MOVIES.filter(m => m.genre_ids?.includes(genreId))
  if (language) {
    results = results.filter(m => m.original_language === language)
  }
  return results
}

export function getSimilarMovies(movie: Movie, language?: string): Movie[] {
  const movieGenres = movie.genre_ids || movie.genres?.map(g => g.id) || []
  let results = MOVIES.filter(m => {
    if (m.id === movie.id) return false
    const mGenres = m.genre_ids || m.genres?.map(g => g.id) || []
    return movieGenres.some(g => mGenres.includes(g))
  })
  if (language) {
    results = results.filter(m => m.original_language === language)
  }
  return results
}

export function getMoviesByDirector(directorId: number, excludeMovieId: number, language?: string): Movie[] {
  const movieIds = Object.entries(MOVIE_CREDITS)
    .filter(([id, credits]) => {
      const director = credits.crew.find(c => c.job === "Director")
      return director?.id === directorId && Number(id) !== excludeMovieId
    })
    .map(([id]) => Number(id))
  
  let results = MOVIES.filter(m => movieIds.includes(m.id))
  if (language) {
    results = results.filter(m => m.original_language === language)
  }
  return results
}

export function getMoviesByCast(castId: number, excludeMovieId: number, language?: string): Movie[] {
  const movieIds = Object.entries(MOVIE_CREDITS)
    .filter(([id, credits]) => {
      return credits.cast.some(c => c.id === castId) && Number(id) !== excludeMovieId
    })
    .map(([id]) => Number(id))
  
  let results = MOVIES.filter(m => movieIds.includes(m.id))
  if (language) {
    results = results.filter(m => m.original_language === language)
  }
  return results
}

export function getCredits(movieId: number) {
  return MOVIE_CREDITS[movieId] || { cast: [], crew: [] }
}

export function getMoviesByGenreFromMovie(movie: Movie, language?: string): Movie[] {
  const genreId = movie.genres?.[0]?.id || movie.genre_ids?.[0]
  if (!genreId) return []
  let results = MOVIES.filter(m => {
    if (m.id === movie.id) return false
    const mGenres = m.genre_ids || m.genres?.map(g => g.id) || []
    return mGenres.includes(genreId)
  })
  if (language) {
    results = results.filter(m => m.original_language === language)
  }
  return results
}
