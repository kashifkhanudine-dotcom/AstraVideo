import { getProviderStatus, type GenerationRequest } from "@/lib/ai/provider";

export const runtime = "nodejs";

const allowedModes = new Set([
  "text-to-video",
  "image-to-video",
  "video-to-video",
  "text-to-image",
  "storyboard",
  "ai-director",
]);

export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as Partial<GenerationRequest> | null;

  if (!body || typeof body.prompt !== "string" || body.prompt.trim().length < 3) {
    return Response.json(
      { ok: false, code: "INVALID_PROMPT", message: "Enter a valid prompt." },
      { status: 400 },
    );
  }

  if (!body.mode || !allowedModes.has(body.mode)) {
    return Response.json(
      { ok: false, code: "UNSUPPORTED_MODE", message: "Unsupported generation mode." },
      { status: 400 },
    );
  }

  const provider = getProviderStatus();

  if (!provider.connected) {
    return Response.json(
      {
        ok: false,
        code: "AI_PROVIDER_NOT_CONNECTED",
        message: "AI PROVIDER NOT CONNECTED",
        action: "Configure AI Provider",
        provider,
      },
      { status: 503 },
    );
  }

  // Intentionally do not fabricate output. A real adapter will create a provider job here.
  return Response.json(
    {
      ok: false,
      code: "PROVIDER_ADAPTER_NOT_ENABLED",
      message: "Provider adapter is not enabled yet.",
    },
    { status: 501 },
  );
}
