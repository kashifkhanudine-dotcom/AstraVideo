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

export function getProviderStatus() {
  return {
    provider: "vercel-ai-gateway",
    model: "klingai/kling-v3.0-t2v",
    authentication: process.env.AI_GATEWAY_API_KEY ? "api-key" : "vercel-oidc",
    configured: Boolean(process.env.AI_GATEWAY_API_KEY || process.env.VERCEL),
  };
}
