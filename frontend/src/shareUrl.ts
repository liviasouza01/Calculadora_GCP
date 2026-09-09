export const PUBLIC_APP_URL =
  (import.meta.env.VITE_PUBLIC_APP_URL ?? "https://calculadora-gcp.web.app").replace(/\/$/, "");

export function currentShareId(): string | null {
  const fromQuery = new URLSearchParams(window.location.search).get("share");
  if (fromQuery) {
    return fromQuery;
  }
  const match = window.location.pathname.match(/^\/s\/([^/]+)\/?$/);
  return match?.[1] ?? null;
}

export function magicLink(shareId: string): string {
  return `${PUBLIC_APP_URL}/s/${shareId}`;
}
