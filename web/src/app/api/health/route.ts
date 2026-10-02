import { getProviderStatus } from "@/lib/ai/provider";

export const runtime = "nodejs";

export async function GET() {
  return Response.json({
    ok: true,
    service: "astravideo-web",
    provider: getProviderStatus(),
    timestamp: new Date().toISOString(),
  });
}
