export type GenerationMode =
  | "text-to-video"
  | "image-to-video"
  | "video-to-video"
  | "text-to-image"
  | "storyboard"
  | "ai-director";

export type GenerationRequest = {
  mode: GenerationMode;
  prompt: string;
  duration?: number;
  aspectRatio?: string;
  resolution?: string;
};

export type ProviderStatus = {
  connected: boolean;
  provider: string | null;
  reason?: string;
};

export function getProviderStatus(): ProviderStatus {
  const provider = process.env.ASTRA_AI_PROVIDER?.trim() || null;
  const gatewayKey = process.env.AI_GATEWAY_API_KEY?.trim();

  if (!provider) {
    return { connected: false, provider: null, reason: "No AI provider selected." };
  }

  if (provider === "vercel-ai-gateway" && !gatewayKey) {
    return { connected: false, provider, reason: "AI_GATEWAY_API_KEY is missing." };
  }

  return {
    connected: false,
    provider,
    reason: "Provider adapter exists as an architectural slot but generation is not enabled yet."
  };
}
