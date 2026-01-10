import { useEffect, useState } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { apiFetch } from "../api";

interface Season {
  id: number;
  season_number: number;
  title?: string;
}

interface Episode {
  id: number;
  episode_number: number;
  title: string;
}

interface TitleDetail {
  id: number;
  type: string;
  title: string;
  description: string;
  year: number;
  seasons: Season[];
  episodes: Episode[];
}

export default function TitlePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState<TitleDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [variants, setVariants] = useState<{ id: number; audio_code: string; quality_code: string; status: string }[]>(
    []
  );

  useEffect(() => {
    const load = async () => {
      try {
        const response = await apiFetch(`/titles/${id}`);
        setData(response);
        if (response.type === "movie") {
          const movieVariants = await apiFetch(`/variants?scope=movie&scope_id=${id}`);
          setVariants(movieVariants);
        }
      } catch (err) {
        setError("Ошибка загрузки");
      }
    };
    load();
  }, [id]);

  if (error) return <div>{error}</div>;
  if (!data) return <div>Загрузка...</div>;

  return (
    <div>
      <h1>{data.title}</h1>
      <p>{data.description}</p>
      {data.type === "movie" && (
        <div>
          <h2>Варианты</h2>
          {variants.map((variant) => (
            <div key={variant.id}>
              {variant.audio_code} {variant.quality_code} ({variant.status})
              <button
                onClick={async () => {
                  try {
                    const response = await apiFetch("/watch/request", {
                      method: "POST",
                      headers: { "Content-Type": "application/json" },
                      body: JSON.stringify({
                        scope_type: "movie",
                        scope_id: Number(id),
                        audio: variant.audio_code,
                        quality: variant.quality_code,
                        ad_nonce: localStorage.getItem("ad_nonce"),
                      }),
                    });
                    if (response.action === "deliver") {
                      await apiFetch(`/watch/deliver?variant_id=${variant.id}`, { method: "POST" });
                      setError("Видео отправлено в чат");
                    } else {
                      localStorage.setItem("pending_variant", JSON.stringify({ scope_id: id, variant }));
                      navigate("/ad-gate");
                    }
                  } catch (err) {
                    setError("Не удалось запросить просмотр");
                  }
                }}
                disabled={variant.status !== "uploaded"}
              >
                Смотреть
              </button>
            </div>
          ))}
        </div>
      )}
      {data.type === "series" && (
        <div>
          <h2>Сезоны</h2>
          {data.seasons.map((season) => (
            <div key={season.id}>Сезон {season.season_number}</div>
          ))}
          <h2>Эпизоды</h2>
          {data.episodes.map((episode) => (
            <div key={episode.id}>
              <Link to={`/episode/${episode.id}`}>E{episode.episode_number} {episode.title}</Link>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
