---
name: tmdb
description: Access The Movie Database (TMDB) for movie metadata, cast, crew, and images.
---

# TMDB Skill

Integrates with The Movie Database API v3.

## Configuration
Requires `TMDB_API_KEY` or `TMDB_READ_TOKEN` in environment variables.

## Actions

### `search_movie`
Search for a movie by title.
- `query` (str): Movie title to search for.
- `year` (str, optional): Release year to filter results.

### `get_movie_details`
Get full metadata for a movie by ID.
- `tmdb_id` (int): The TMDB Movie ID.
Returns processed object suitable for database entry (credits, budget, ratings, etc.)

### `search_person`
Search for cast or crew members.
- `query` (str): Person's name.
