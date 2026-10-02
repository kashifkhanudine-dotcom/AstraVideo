import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "ASTRA VIDEO AI",
    short_name: "AstraVideo",
    description: "Create anything. Direct everything.",
    start_url: "/",
    display: "standalone",
    background_color: "#080a0f",
    theme_color: "#080a0f",
    icons: [
      { src: "/astra-mark.svg", sizes: "any", type: "image/svg+xml", purpose: "any" }
    ],
  };
}
