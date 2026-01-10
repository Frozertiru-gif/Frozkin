import { useEffect, useState } from "react";
import { apiFetch } from "../api";
import { Link } from "react-router-dom";

interface Title {
  id: number;
  type: string;
  title: string;
  description: string;
  poster_url?: string;
  year: number;
}

export default function CatalogPage() {
  const [movies, setMovies] = useState<Title[]>([]);
  const [series, setSeries] = useState<Title[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const moviesData = await apiFetch("/catalog/top?type=movie&limit=12");
        const seriesData = await apiFetch("/catalog/top?type=series&limit=12");
        setMovies(moviesData);
        setSeries(seriesData);
      } catch (err) {
        setError("Ошибка загрузки каталога");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const onSearch = async () => {
    setLoading(true);
    try {
      const result = await apiFetch(`/catalog/search?q=${encodeURIComponent(query)}&type=movie`);
      setMovies(result);
    } catch (err) {
      setError("Ошибка поиска");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Загрузка...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div>
      <h1>Каталог</h1>
      <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Поиск" />
      <button onClick={onSearch}>Найти</button>
      <h2>Фильмы</h2>
      <div>
        {movies.length === 0 ? (
          <div>Нет данных</div>
        ) : (
          movies.map((item) => (
            <div key={item.id}>
              <Link to={`/title/${item.id}`}>{item.title}</Link> ({item.year})
            </div>
          ))
        )}
      </div>
      <h2>Сериалы</h2>
      <div>
        {series.length === 0 ? (
          <div>Нет данных</div>
        ) : (
          series.map((item) => (
            <div key={item.id}>
              <Link to={`/title/${item.id}`}>{item.title}</Link> ({item.year})
            </div>
          ))
        )}
      </div>
    </div>
  );
}
