import { useEffect, useState } from "react";
import { Routes, Route, Link } from "react-router-dom";
import CatalogPage from "./pages/CatalogPage";
import TitlePage from "./pages/TitlePage";
import EpisodePage from "./pages/EpisodePage";
import FavoritesPage from "./pages/FavoritesPage";
import AdGatePage from "./pages/AdGatePage";
import { authWithTelegram, clearToken, setToken } from "./api";

declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        initData: string;
        ready: () => void;
      };
    };
  }
}

export default function App() {
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [missingTelegram, setMissingTelegram] = useState(false);

  useEffect(() => {
    const init = async () => {
      try {
        const initData = window.Telegram?.WebApp?.initData || "";
        if (!initData) {
          clearToken();
          setMissingTelegram(true);
          return;
        }
        window.Telegram?.WebApp?.ready();
        const response = await authWithTelegram(initData);
        setToken(response.access_token);
        setReady(true);
      } catch (err) {
        clearToken();
        setError("Не удалось авторизоваться");
      }
    };
    init();
  }, []);

  if (error) {
    return <div className="error">{error}</div>;
  }
  if (missingTelegram) {
    return <div className="error">Open in Telegram</div>;
  }
  if (!ready) {
    return <div className="loading">Загрузка...</div>;
  }

  return (
    <div>
      <nav>
        <Link to="/">Каталог</Link> | <Link to="/favorites">Избранное</Link>
      </nav>
      <Routes>
        <Route path="/" element={<CatalogPage />} />
        <Route path="/title/:id" element={<TitlePage />} />
        <Route path="/episode/:id" element={<EpisodePage />} />
        <Route path="/favorites" element={<FavoritesPage />} />
        <Route path="/ad-gate" element={<AdGatePage />} />
      </Routes>
    </div>
  );
}
