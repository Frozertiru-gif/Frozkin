import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../api";

export default function AdGatePage() {
  const [status, setStatus] = useState("init");
  const navigate = useNavigate();

  useEffect(() => {
    const start = async () => {
      try {
        await apiFetch("/ads/start", { method: "POST" });
        setStatus("ready");
      } catch (err) {
        setStatus("error");
      }
    };
    start();
  }, []);

  const complete = async () => {
    try {
      const response = await apiFetch("/ads/complete", { method: "POST" });
      localStorage.setItem("ad_nonce", response.nonce);
      const pending = localStorage.getItem("pending_variant");
      if (pending) {
        const parsed = JSON.parse(pending);
        navigate(`/episode/${parsed.scope_id}`);
      } else {
        navigate("/");
      }
    } catch (err) {
      setStatus("error");
    }
  };

  if (status === "error") return <div>Ошибка рекламы</div>;

  return (
    <div>
      <h1>Просмотр рекламы</h1>
      <p>Посмотрите рекламу и нажмите кнопку.</p>
      <button onClick={complete}>Я посмотрел</button>
    </div>
  );
}
