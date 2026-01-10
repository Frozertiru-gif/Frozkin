import { useEffect, useState } from "react";
import { apiFetch } from "../api";

interface Favorite {
  id: number;
  title_id: number;
}

export default function FavoritesPage() {
  const [items, setItems] = useState<Favorite[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await apiFetch("/favorites");
        setItems(response);
      } catch (err) {
        setError("Ошибка загрузки избранного");
      }
    };
    load();
  }, []);

  if (error) return <div>{error}</div>;

  return (
    <div>
      <h1>Избранное</h1>
      {items.length === 0 ? <div>Пусто</div> : items.map((item) => <div key={item.id}>ID {item.title_id}</div>)}
    </div>
  );
}
