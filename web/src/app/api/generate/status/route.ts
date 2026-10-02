import { gateway } from "@ai-sdk/gateway";

export const runtime = "nodejs";
export const maxDuration = 30;

const MODEL_ID = "klingai/kling-v3.0-t2v";

type StatusBody = { operation?: unknown };

export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as StatusBody | null;
  if (!body?.operation) {
    return Response.json({ ok: false, message: "Missing generation operation." }, { status: 400 });
  }

  try {
    const model = gateway.videoModel(MODEL_ID);
    const status = await model.doStatus({ operation: body.operation as never });
    const videos = (status.videos ?? [])
      .filter((video) => video.type === "url")
      .map((video) => ({ url: video.url, mediaType: video.mediaType }));

    return Response.json({
      ok: true,
      status: status.status,
      videos,
      error: status.status === "failed" ? "Kling generation failed." : undefined,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unable to check generation status.";
    return Response.json({ ok: false, code: "STATUS_FAILED", message }, { status: 502 });
  }
}
