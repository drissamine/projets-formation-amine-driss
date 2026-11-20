import { useState, useEffect } from 'react';
import './App.css';
import MovieForm from './components/MovieForm';
import MovieList from './components/MovieList';
import SearchBar from './components/SearchBar';

function App() {
  // Initialiser l'état avec les films sauvegardés
  const initializeMovies = () => {
    const savedMovies = localStorage.getItem('movies');
    if (savedMovies) {
      return JSON.parse(savedMovies);
    } else {
      // Films d'exemple
      return [
        {
          id: 1,
          title: 'Inception',
          year: 2010,
          director: 'Christopher Nolan',
          description: 'Un braqueur qui se specialise dans l\'extraction de secrets a partir de reves.',
          rating: 5,
          reviews: ['Chef-d\'oeuvre du cinema moderne']
        },
        {
          id: 2,
          title: 'Interstellar',
          year: 2014,
          director: 'Christopher Nolan',
          description: 'Une equipe d\'astronautes voyage a travers un trou de ver.',
          rating: 4,
          reviews: []
        }
      ];
    }
  };

  const [movies, setMovies] = useState(initializeMovies);
  const [searchTerm, setSearchTerm] = useState('');

  // Sauvegarder les films dans localStorage a chaque changement
  useEffect(() => {
    localStorage.setItem('movies', JSON.stringify(movies));
  }, [movies]);

  const handleAddMovie = (movieData) => {
    const newMovie = {
      id: Date.now(),
      ...movieData,
      rating: 0,
      reviews: []
    };
    setMovies([newMovie, ...movies]);
    alert('Film ajoute avec succes!');
  };

  const handleAddReview = (movieId, review) => {
    setMovies(
      movies.map((movie) =>
        movie.id === movieId
          ? { ...movie, reviews: [...movie.reviews, review] }
          : movie
      )
    );
  };

  const handleRateMovie = (movieId, rating) => {
    setMovies(
      movies.map((movie) =>
        movie.id === movieId ? { ...movie, rating } : movie
      )
    );
  };

  const handleDeleteMovie = (movieId) => {
    if (window.confirm('Etes-vous sur de vouloir supprimer ce film?')) {
      setMovies(movies.filter((movie) => movie.id !== movieId));
    }
  };

  // Filtrer les films selon la recherche
  const filteredMovies = movies.filter((movie) =>
    movie.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    movie.director.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="app">
      <h1>CineReview - Critique Cinematographique</h1>
      
      <div className="container">
        <MovieForm onAddMovie={handleAddMovie} />
      </div>

      <SearchBar 
        searchTerm={searchTerm} 
        onSearchChange={setSearchTerm} 
      />

      <div style={{ color: 'white', marginBottom: '10px' }}>
        {filteredMovies.length} film{filteredMovies.length !== 1 ? 's' : ''} trouve{filteredMovies.length !== 1 ? 's' : ''}
      </div>

      <MovieList 
        movies={filteredMovies} 
        onAddReview={handleAddReview} 
        onRateMovie={handleRateMovie} 
        onDeleteMovie={handleDeleteMovie} 
      />
    </div>
  );
}

export default App;
