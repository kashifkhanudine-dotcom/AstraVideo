"use client";

import { useMemo, useState } from "react";

type Mode = "text-to-video" | "image-to-video" | "video-to-video" | "text-to-image" | "storyboard" | "ai-director";

const modes: { id: Mode; label: string }[] = [
  { id: "text-to-video", label: "Text to Video" },
  { id: "image-to-video", label: "Image to Video" },
  { id: "video-to-video", label: "Video to Video" },
  { id: "text-to-image", label: "Text to Image" },
  { id: "storyboard", label: "Storyboard" },
  { id: "ai-director", label: "AI Director" },
];

const models = [
  { name: "Kling 3.0 Pro", detail: "LIVE · AI Gateway", quality: "★★★★★", speed: "★★★", cost: "Provider billed" },
  { name: "Kling 3.0 Standard", detail: "Coming next", quality: "★★★★", speed: "★★★★", cost: "Provider billed" },
  { name: "Auto Router", detail: "Coming soon", quality: "Adaptive", speed: "Adaptive", cost: "Adaptive" },
];

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export default function CreationStudio() {
  const [mode, setMode] = useState<Mode>("text-to-video");
  const [prompt, setPrompt] = useState("Create a cinematic scene of a futuristic city during a storm.");
  const [model, setModel] = useState("Kling 3.0 Pro");
  const [status, setStatus] = useState("Ready · Kling 3.0 Pro");
  const [busy, setBusy] = useState(false);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);

  const estimatedCredits = useMemo(() => (mode === "text-to-image" ? 4 : mode === "ai-director" ? 18 : 12), [mode]);

  async function generate() {
    if (mode !== "text-to-video") {
      setStatus("Provider required · Text to Video is connected first");
      return;
    }

    setBusy(true);
    setVideoUrl(null);
    setStatus("Starting Kling 3.0 Pro generation…");

    try {
      const response = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mode, prompt, duration: 5, aspectRatio: "16:9", resolution: "1080p", model }),
      });
      const data = await response.json();
      if (!response.ok || !data.ok) throw new Error(data.hint ? `${data.message} — ${data.hint}` : data.message || "Generation could not start.");

      setStatus("Queued on Kling · preparing generation…");

      for (let attempt = 0; attempt < 120; attempt += 1) {
        await sleep(5000);
        const statusResponse = await fetch("/api/generate/status", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ operation: data.operation }),
        });
        const statusData = await statusResponse.json();
        if (!statusResponse.ok || !statusData.ok) throw new Error(statusData.message || "Could not check Kling status.");

        if (statusData.status === "completed") {
          const url = statusData.videos?.[0]?.url;
          if (!url) throw new Error("Kling completed but no video URL was returned.");
          setVideoUrl(url);
          setStatus("Completed · video ready");
          return;
        }
        if (statusData.status === "failed" || statusData.status === "cancelled") {
          throw new Error(statusData.error || `Generation ${statusData.status}.`);
        }

        setStatus(`Kling generation · ${statusData.status || "processing"}…`);
      }

      throw new Error("Generation is still processing. Try again from the generation history later.");
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "Generation request failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="studio-shell">
      <aside className="sidebar">
        <div className="brand"><span className="brand-mark">A</span><div><strong>ASTRA VIDEO</strong><small>AI CREATIVE STUDIO</small></div></div>
        <nav className="side-nav" aria-label="Primary">
          {["Home", "Create", "AI Video", "AI Image", "AI Director", "Storyboard", "Characters", "Elements", "AI Effects", "AI Editor", "Audio Studio", "Explore", "Projects", "My Creations", "Assets", "Templates"].map((item) => <button className={item === "Create" ? "nav-item active" : "nav-item"} key={item}>{item}</button>)}
        </nav>
        <div className="side-footer"><button className="nav-item">Settings</button><button className="nav-item">Help Center</button></div>
      </aside>

      <section className="workspace">
        <header className="topbar">
          <div className="search">⌕ <span>Search projects, creations, characters…</span></div>
          <div className="top-actions"><span className="credits">◈ Provider billing</span><button className="icon-btn" aria-label="Notifications">◌</button><div className="avatar">KM</div></div>
        </header>

        <div className="content">
          <div className="hero-copy"><span className="eyebrow">ASTRA CREATION ENGINE</span><h1>Create anything.<br/><span>Direct everything.</span></h1><p>Professional AI video generation powered by Kling through Vercel AI Gateway.</p></div>

          <section className="composer-card">
            <div className="mode-tabs" role="tablist">
              {modes.map((item) => <button key={item.id} onClick={() => setMode(item.id)} className={mode === item.id ? "mode active" : "mode"}>{item.label}</button>)}
            </div>
            <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} aria-label="Describe your creation" />
            <div className="composer-tools">
              <div className="tool-row"><button>＋ Upload</button><button>◇ Add reference</button><button>♙ Character</button><button>✦ Enhance Prompt</button></div>
              <button className="generate" disabled={busy || prompt.trim().length < 3} onClick={generate}>{busy ? "GENERATING…" : "GENERATE"}</button>
            </div>
            <div className="status-line"><span className="status-dot" />{status}<span className="estimate">Mode: {mode === "text-to-video" ? "LIVE" : "Provider required"} · {estimatedCredits} Astra credits est.</span></div>
          </section>

          {videoUrl && (
            <section style={{ marginTop: 18, border: "1px solid #2a2e3b", borderRadius: 16, overflow: "hidden", background: "#0d0f14" }}>
              <video src={videoUrl} controls autoPlay playsInline style={{ display: "block", width: "100%", maxHeight: 650, background: "black" }} />
              <div style={{ display: "flex", justifyContent: "space-between", gap: 12, padding: 14, alignItems: "center" }}>
                <span style={{ color: "#8f97aa", fontSize: 12 }}>Generated with Kling AI 3.0 Pro</span>
                <a href={videoUrl} target="_blank" rel="noreferrer" style={{ color: "#b79aff", fontSize: 12 }}>Open video ↗</a>
              </div>
            </section>
          )}

          <div className="section-heading"><div><span className="eyebrow">MODEL ROUTER</span><h2>Choose your generation engine</h2></div><button className="text-btn">More providers soon →</button></div>
          <div className="model-grid">
            {models.map((item) => <button key={item.name} onClick={() => setModel(item.name)} className={model === item.name ? "model-card selected" : "model-card"}><div className="model-top"><span className="model-icon">✦</span><span className="pill">{item.detail}</span></div><h3>{item.name}</h3><div className="metrics"><span>Quality <b>{item.quality}</b></span><span>Speed <b>{item.speed}</b></span><span>Cost <b>{item.cost}</b></span></div></button>)}
          </div>

          <section className="quick-grid">
            <article><span>01</span><h3>AI Director</h3><p>Turn one idea into a structured concept, scenes, shots and production plan.</p><button>Provider required →</button></article>
            <article><span>02</span><h3>Storyboard Studio</h3><p>Build, reorder and refine scenes while preserving characters and style.</p><button>Coming next →</button></article>
            <article><span>03</span><h3>Character System</h3><p>Create reusable character profiles ready for consistent generations.</p><button>Coming next →</button></article>
          </section>
        </div>
      </section>

      <nav className="mobile-nav" aria-label="Mobile navigation"><button>⌂<span>Home</span></button><button className="active">✦<span>Create</span></button><button>▣<span>Projects</span></button><button>◎<span>Profile</span></button></nav>
    </main>
  );
}
