import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../api";

interface Variant {
  id: number;
  audio_code: string;
  quality_code: string;
  status: string;
}

export default function EpisodePage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [variants, setVariants] = useState<Variant[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await apiFetch(`/episodes/${id}`);
        setVariants(response.variants);
      } catch (err) {
        setError("Ошибка загрузки эпизода");
      }
    };
    load();
  }, [id]);

  const onWatch = async (variant: Variant) => {
    if (variant.status !== "uploaded") {
      setError("Видео ещё загружается");
      return;
    }
    try {
      const response = await apiFetch("/watch/request", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          scope_type: "episode",
          scope_id: Number(id),
          audio: variant.audio_code,
          quality: variant.quality_code,
          ad_nonce: localStorage.getItem("ad_nonce"),
        }),
      });
      if (response.action === "deliver") {
        await apiFetch(`/watch/deliver?delivery_token=${response.delivery_token}`, { method: "POST" });
        setError("Видео отправлено в чат");
      } else {
        localStorage.setItem("pending_variant", JSON.stringify({ scope_id: id, variant }));
        navigate("/ad-gate");
      }
    } catch (err) {
      setError("Не удалось запросить просмотр");
    }
  };

  if (error) return <div>{error}</div>;

  return (
    <div>
      <h1>Эпизод {id}</h1>
      {variants.map((variant) => (
        <div key={variant.id}>
          {variant.audio_code} {variant.quality_code} ({variant.status})
          <button onClick={() => onWatch(variant)} disabled={variant.status !== "uploaded"}>
            Смотреть
          </button>
        </div>
      ))}
    </div>
  );
}
