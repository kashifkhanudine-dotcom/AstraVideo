import { gateway } from "@ai-sdk/gateway";
import { experimental_startVideo } from "ai";
import type { GenerationRequest } from "@/lib/ai/provider";

export const runtime = "nodejs";
export const maxDuration = 60;

const MODEL_ID = "klingai/kling-v3.0-t2v";
const allowedRatios = new Set(["16:9", "9:16", "1:1"]);

export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as Partial<GenerationRequest> | null;

  if (!body || typeof body.prompt !== "string" || body.prompt.trim().length < 3) {
    return Response.json({ ok: false, code: "INVALID_PROMPT", message: "Enter a valid prompt." }, { status: 400 });
  }

  if (body.mode !== "text-to-video") {
    return Response.json(
      { ok: false, code: "PROVIDER_REQUIRED", message: "This mode is not connected yet. Text to Video is available first." },
      { status: 501 },
    );
  }

  const duration = Math.min(15, Math.max(3, Number(body.duration) || 5));
  const aspectRatio = allowedRatios.has(body.aspectRatio || "") ? body.aspectRatio! : "16:9";

  try {
    const result = await experimental_startVideo({
      model: gateway.videoModel(MODEL_ID),
      prompt: body.prompt.trim().slice(0, 2500),
      duration,
      aspectRatio,
      generateAudio: true,
      providerOptions: {
        klingai: {
          mode: "pro",
        },
      },
    });

    return Response.json({
      ok: true,
      status: "queued",
      model: MODEL_ID,
      operation: result.operation,
      warnings: result.warnings ?? [],
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to start Kling generation.";
    return Response.json(
      {
        ok: false,
        code: "GENERATION_START_FAILED",
        message,
        hint: "Enable Vercel AI Gateway for this project or add AI_GATEWAY_API_KEY in Vercel Environment Variables.",
      },
      { status: 502 },
    );
  }
}
