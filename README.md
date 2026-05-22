# Filmory

> Multilingual Multi-Modal AI Movie Recommendation System

An intelligent recommendation platform supporting story, cast, director, and genre-based discovery across multiple languages using sparse similarity computation and memory-optimized architecture.

## Summary and Background of the Invention
Movie recommendation systems have been widely studied, but existing solutions suffer from three fundamental limitations. First, they predominantly operate on single-language English datasets, making them ill-suited for globally diverse audiences who consume content in Hindi, Tamil, Telugu, Korean, and other languages. Second, they rely on either collaborative filtering — which requires large volumes of user interaction data and therefore fails for new or low-traffic deployments — or pre-computed dense cosine similarity matrices that consume huge memory. Third, existing systems offer only a single recommendation modality, typically plot-based similarity, without any support for cast-driven, director-driven, or genre-driven discovery, forcing users into a one-size-fits-all experience regardless of their intent.
To address these gaps, the proposed invention introduces a “Memory-Optimized Multilingual Multi-Modal Recommendation Architecture,” implemented and validated through Filmory. The central novelty of the system is its “Sparse On-Demand Similarity Engine,” which replaces the memory-intensive pre-computed N×N dense matrix with a SciPy sparse CSR TF-IDF matrix of approximately 5–10 MB. At query time, only the seed movie’s row vector is extracted and cosine similarity is computed on demand against the full sparse matrix, reducing total system RAM from approximately 700 MB to approximately 200 MB — a 71% reduction — while keeping per-query latency to around 50 milliseconds.
The system further distinguishes itself through two additional novel mechanisms. The first is a “Four-Step Multilingual Title Resolver” that bridges the gap between transliterated user input and native-script database entries — for example, correctly resolving the English input ‘dangal’ to the stored Hindi-script entry ‘दंगल’ — by sequencing exact case-insensitive matching, partial substring matching, TMDB(The Movie DataBase) ID intersection, and TMDB original_title field matching. The second is a “Billing-Weighted Cast Scoring” mechanism that assigns hierarchical weights to actors based on their official TMDB billing position, so that films sharing both lead actors rank significantly higher than those sharing only supporting cast. Both mechanisms operate against a PostgreSQL-backed credits cache pre-populated
at startup, enabling O(1) lookup for cast and director data without any live API calls at query time.
By integrating the sparse similarity engine, the multilingual title resolver, the billing-weighted cast scorer, and a TMDB-metadata-based fallback for movies absent from the local database, Filmory delivers a unified four-modality recommendation system — Story/Plot, Cast, Director, and Genre — that operates across five languages (English, Hindi, Tamil, Telugu, and Korean) within infrastructure constraints, without requiring any user interaction history.

## Objective(s)

- Global Language Support: We built a system that recommends movies in five different languages (English, Hindi, Tamil, Telugu, and Korean), ensuring that the movies suggested are culturally and linguistically authentic.
- Four Ways to Discover: Users can find new movies based on four specific preferences: the story (plot similarity), the main actors (giving more weight to lead stars), the director, or the genre.
- Smart Search for Regional Titles: The system easily finds movies even if you type the name in English (like 'Dangal') when the record is saved in its original script (like 'दंगल'). It uses a multi-step "translator" to make sure it finds the right movie every time.
- Lightweight and Efficient: We redesigned how the system "thinks" to make it much lighter. By changing how it calculates movie similarities, we reduced its memory needs by over 70%, allowing the app to run smoothly on free, basic cloud servers without crashing.
- Always-On Recommendations: Even if you search for an obscure movie that isn't in our main database, the system doesn't give up. It uses a backup "expert" to find similar movies based on themes and descriptions, so the user never hits a dead end.

## Working principle

The Filmory architecture functions as a comprehensive full-stack recommendation pipeline organized into six logical stages. The process begins with Data Collection and Storage, where movies are retrieved from the TMDB API across five languages and nineteen genres. To ensure cultural authenticity, the system utilizes language-specific parameters and stores the data—including high-quality visual backdrops—in a Supabase PostgreSQL database using efficient bulk insertion techniques that prevent duplicate entries. Following storage, the Credits Pre-Caching stage populates a specialized table with actor and director information, which is then loaded into the backend's memory upon startup to allow for near-instant data retrieval during active user searches.
The core recommendation logic is driven by Feature Engineering, which creates a weighted text description for every movie by emphasizing the plot and genre. This text is then processed through a Sparse TF-IDF Similarity engine; rather than using a massive, memory-heavy database of every possible movie pairing, the system uses a highly compressed "sparse" format. This allows it to calculate similarities
on the fly, reducing memory usage by over 70% and making the system light enough to run on basic cloud servers.
To provide a personalized experience, the system utilizes Multi-Modal Recommendation Scoring, which offers three distinct ways to find movies: a "Cast mode" that gives higher priority to lead actors based on their billing order, a "Director mode" that identifies shared creative styles, and a "Genre mode" for fans of specific categories. Finally, the Title Resolution and Fallback stage ensures reliability; a smart 4-step search tool translates English-typed titles to find their original-language matches, and if a movie isn't in the local database, a backup "expert" system uses external metadata to ensure the user always receives relevant recommendations.

<p align="center">
  <img width="441" height="564" alt="image" src="https://github.com/user-attachments/assets/788978dd-d278-4269-94cc-513490050b32" />
</p>

<p align="center">
  <i>This diagram illustrates the end-to-end pipeline of Filmory, including data collection, feature engineering, memory-efficient similarity computation, and multi-modal recommendation strategies.</i>
</p>

## System Overview (High Level)
The Filmory system is organized into six logical layers that work together to provide a seamless, high-performance recommendation experience while remaining extremely resource-efficient:

- **Data Layer (Supabase PostgreSQL):** The system uses a professional-grade database to store three main categories of information: movie details, contributor credits, and user feedback. To handle multiple users efficiently, it uses a Threaded Connection Pool, which acts like a "waiting line manager" to share database connections effectively, and Context-Managed Transactions to ensure that data is either saved perfectly or safely cancelled if an error occurs.

- **Recommendation Engine (Python):** This is the "brain" of the system, consisting of specialized scripts for different types of matching: Sparse TF-IDF for analyzing story plots, a Credits Cache for quickly looking up actors and directors, and a Unified Router that decides which recommendation method to use based on the user's current search.

- **API Layer (FastAPI):** This layer acts as the "waiter," receiving requests from the user and delivering data from the backend. It uses CORS (Cross-Origin Resource Sharing) to ensure the website can securely communicate with the server and loads the "memory-heavy" data once at startup to keep the system fast during use.

- **Frontend (Next.js + Tailwind):** This is the visual interface the user interacts with. It features a 300ms Debounced Search, which waits a fraction of a second after you stop typing to prevent the system from getting overwhelmed, and Scroll-Triggered Animations that use a "visibility sensor" (IntersectionObserver) to make movie cards slide in smoothly only when they appear on your screen.

- **Infrastructure:** The system is split across specialized cloud platforms: Render for the heavy calculations, Vercel for the website interface, and Supabase for permanent storage. By using a Sparse Matrix approach, we reduced the system's "active memory" needs by 71%, allowing it to host up to 28,000 movies on a basic, free-tier server that would normally crash.

- **Update Mechanism:** To keep the movie list current without wasting time or resources, the system uses an Incremental Update process. Instead of downloading everything from scratch, it only looks for new movies and missing credits, ensuring the database stays fresh with minimal effort.

## Core Similarity Computation (Algorithms & Formulas)
### Story/Plot Mode — Sparse TF-IDF Cosine Similarity:
combined_features(m) = (overview × 3) + (genre_ids_text × 2) + language_code
sim(seed, candidate) = cosine(tfidf_matrix[seed_idx], tfidf_matrix[candidate_idx])

- Explanation: We give the Overview (plot) three times the importance and the Genre twice the importance. This ensures the system focuses mostly on what the movie is about.

- The Math: We calculate the similarity score between a "Seed" movie (what you just watched) and a "Candidate" movie using the formula as above.

- Instead of storing a massive table of every movie paired with every other movie (which would take 512MB+), we use a Sparse CSR Matrix. This only stores the "active" words, reducing the memory to a tiny 5–10 MB while still finding the perfect match.

<p align="center">
  <img width="428" height="526" alt="image" src="https://github.com/user-attachments/assets/8a764e1c-a7dc-4a29-9d95-c6fa43725071" />

</p>

<p align="center">
  <i>This diagram shows how weighted textual features are transformed into a sparse TF-IDF matrix to compute memory-efficient cosine similarity between movies.</i>
</p>

### Cast Mode — Billing-Weighted Scoring:
score(candidate) = Σ weight(actor) for actor in (seed_cast_weights ∩ candidate_cast)
weight(actor) = 10 if billing_position ≤ 1, else 4 if position == 2, else 1
Results sorted by score only (rating excluded to prevent high-rated irrelevant films dominating)
Unlike standard systems that just check if the same actors are in both movies, Filmory cares how important those actors are.
**Explanation:** If two movies share the same "Lead Actor," they get a high score of 10. If they only share a background extra, they get 1. We exclude the movie's rating here so that obscure but highly relevant movies aren't hidden by "Blockbusters."

<p align="center">
  <img width="480" height="535" alt="image" src="https://github.com/user-attachments/assets/ead27cbf-ca5b-4baf-b9c6-97710b8d4681" />


</p>

<p align="center">
  <i>This diagram demonstrates billing-weighted actor matching, where lead actors contribute higher scores to improve recommendation relevance.</i>
</p>

### Director Mode:
score(candidate) = |seed_directors ∩ candidate_directors| × 10
**Explanation:** The system looks for an exact match in the director's name. If a match is found, it is given a massive 10-point boost, immediately pushing other films by that same director to the top of the list.

<p align="center">
 <img width="471" height="529" alt="image" src="https://github.com/user-attachments/assets/45a046a9-90ba-4df9-9b24-62992fbff076" />

<p align="center">
  <i>This flowchart highlights exact director matching with a strong weighting to prioritize films by the same creator.</i>
</p>

### Genre Mode:
score(candidate) = |seed_genre_ids ∩ candidate_genre_ids|, sorted by (score DESC, rating DESC)
**Explanation:** The system counts how many genre tags (like "Action" or "Sci-Fi") the two movies share. To break ties (if ten movies all share 2 genres), the system then sorts them by their Rating, ensuring the highest-quality movies in that genre are shown first.
<p align="center">
  <img width="388" height="515" alt="image" src="https://github.com/user-attachments/assets/cdd846cd-edd0-4157-9559-7f7886ece152" />


</p>

<p align="center">
  <i>This diagram illustrates genre overlap scoring with rating-based tie-breaking to recommend high-quality similar movies.</i>
</p>

## Title Resolution Algorithm (4-Step _find_seed_movie)
* Exact case-insensitive title match against movies_df['title'].str.lower()
* Partial substring match using str.contains(regex=False)
* TMDB search API → intersect returned TMDB movie IDs with DB movie IDs
* TMDB search API → match TMDB result original_title field against DB title column

If all 4 steps fail, _fallback_recommend() is invoked: fetches genre_ids, overview, original_language from TMDB, computes genre overlap (weight 2×) + TF-IDF cosine similarity (weight 1×) against local DB, returns same-language results first then other languages.

<p align="center">
  <img width="850" height="495" alt="image" src="https://github.com/user-attachments/assets/c95c9813-e14c-4cdf-8231-631c4b51a84e" />

</p>

<p align="center">
  <i>This flowchart represents the 4-step movie identification process with a fallback mechanism to ensure reliable recommendations even when the input title is not found.</i>
</p>

## Screenshots

<img width="1365" height="680" alt="image" src="https://github.com/user-attachments/assets/38c61e3b-103b-42b2-bc57-758b3a5443e1" />
<p align="center">
  <i>This screenshot displays the user interface of Filmory, including the search functionality, multi-modal selection options, and dynamic movie rendering designed for smooth user interaction.</i>
</p>

<img width="1361" height="680" alt="image" src="https://github.com/user-attachments/assets/91480345-20b4-4863-a931-f32707a7afaa" />
<img width="1365" height="679" alt="image" src="https://github.com/user-attachments/assets/0905442c-c6d7-44cd-bcf5-9cff9d33f52d" />

<p align="center">
  <i>These screenshots shows the real-time search functionality with debounced input, displaying relevant movie suggestions as the user types.</i>
</p>

<img width="1365" height="679" alt="image" src="https://github.com/user-attachments/assets/6a65596a-441e-4ba7-b958-8a0f226baf88" />
<p align="center">
  <i>This screenshot presents detailed movie information, including backdrop images fetched from TMDB and metadata stored in PostgreSQL.</i>
</p>

<img width="1365" height="683" alt="image" src="https://github.com/user-attachments/assets/8a9c7032-9de0-490a-881d-503178470730" />
<img width="1365" height="609" alt="image" src="https://github.com/user-attachments/assets/9e668fb9-df72-4190-9056-b7b8f5ae9a1b" />
<p align="center">
  <i>This screenshot highlights the selected Story/Plot recommendation mode and the language filter option, with circled regions indicating user-controlled parameters that influence the recommendation output.</i>
</p>

<img width="1364" height="682" alt="image" src="https://github.com/user-attachments/assets/6de1bb10-a608-43a2-a66e-bc420533ea4d" />

<p align="center">
  <i>This screenshot demonstrates the language selection feature, where users can filter recommendations based on preferred languages, enabling multilingual and culturally relevant movie suggestions.</i>
</p>

<img width="1365" height="683" alt="image" src="https://github.com/user-attachments/assets/7e645aad-ddc6-4eab-bf64-9e33e5da945b" />
<img width="1365" height="610" alt="image" src="https://github.com/user-attachments/assets/7b825cc5-f072-4ff8-8f38-7b377c9a8d0d" />
<p align="center">
  <i>This screenshot illustrates recommendations generated under the Story/Plot mode with the Hindi language filter applied, where circled regions highlight the active mode and selected language influencing the displayed results.</i>
</p>

<img width="1365" height="682" alt="image" src="https://github.com/user-attachments/assets/51f42732-30ef-4b0e-bf29-3163b6868a66" />
<img width="1365" height="609" alt="image" src="https://github.com/user-attachments/assets/a8e2e4d3-f1b8-4f05-a692-388212439a5a" />
<p align="center">
  <i>This screenshot demonstrates the Cast mode, where movies are recommended based on shared actors, with the highlighted region indicating the active selection and results prioritized using billing-weighted scoring.</i>
</p>

<img width="1365" height="681" alt="image" src="https://github.com/user-attachments/assets/67427d4a-bf85-4575-b2f4-a984e1b8393f" />
<img width="1365" height="608" alt="image" src="https://github.com/user-attachments/assets/ec866f8b-a7e7-494b-91f3-607198d6203e" />
<p align="center">
  <i>This screenshot illustrates director-driven recommendations, where films by the same director are prioritized using exact match scoring, as indicated by the highlighted Director mode.</i>
</p>

<img width="1365" height="682" alt="image" src="https://github.com/user-attachments/assets/f7a47001-4a0d-4598-86c9-a2ad2b750947" />
<img width="1365" height="610" alt="image" src="https://github.com/user-attachments/assets/277b954b-2a83-47bd-ab20-ac7dbfa1f981" />
<p align="center">
  <i>This screenshot illustrates genre-based recommendations, where movies sharing similar categories are prioritized, with higher-rated films ranked first in cases of equal genre overlap.</i>
</p>






