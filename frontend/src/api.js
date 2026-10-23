// Vite forwards /api requests to FastAPI during local development.
export async function request(path, options = {}) {
  const headers =
    options.body instanceof FormData
      ? {}
      : { "Content-Type": "application/json" };
  let response;
  try {
    response = await fetch(`/api/v1${path}`, { ...options, headers });
  } catch {
    throw new Error("Cannot reach the API. Start the backend on port 8000.");
  }
  const data = await response.json();
  if (!response.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((item) => `${item.loc.at(-1)}: ${item.msg}`).join("; ")
      : data.detail;
    throw new Error(detail || "The request could not be completed.");
  }
  return data;
}
