import { afterEach, describe, expect, it, vi } from "vitest";
import { request } from "./api.js";

afterEach(() => vi.unstubAllGlobals());
describe("API helper", () => {
  it("sends JSON and returns successful results", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({ id: 1 }) });
    vi.stubGlobal("fetch", fetch);
    expect(
      await request("/integrations/", { method: "POST", body: "{}" }),
    ).toEqual({ id: 1 });
    expect(fetch).toHaveBeenCalledWith(
      "/api/v1/integrations/",
      expect.objectContaining({
        headers: { "Content-Type": "application/json" },
      }),
    );
  });
  it("lets the browser supply multipart headers", async () => {
    const fetch = vi
      .fn()
      .mockResolvedValue({ ok: true, json: async () => ({}) });
    vi.stubGlobal("fetch", fetch);
    await request("/documents/upload", {
      method: "POST",
      body: new FormData(),
    });
    expect(fetch.mock.calls[0][1].headers).toEqual({});
  });
  it("explains validation failures", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        json: async () => ({
          detail: [{ loc: ["body", "name"], msg: "Required" }],
        }),
      }),
    );
    await expect(request("/integrations/")).rejects.toThrow("name: Required");
  });
  it("explains connection failures", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockRejectedValue(new TypeError("Failed to fetch")),
    );
    await expect(request("/integrations/")).rejects.toThrow(
      "Start the backend",
    );
  });
});
