import React from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import App from "./App.jsx";
import { request } from "./api.js";

vi.mock("./api.js", () => ({ request: vi.fn() }));
const integration = {
  id: 1,
  name: "Payments API",
  base_url: "https://example.com",
  http_method: "GET",
  is_active: true,
};
const incident = {
  id: 1,
  integration_id: 1,
  title: "Payment timeout",
  error_message: "Request timed out",
  status: "OPEN",
  created_at: "2026-10-21T10:00:00",
};
beforeEach(() => {
  request.mockReset();
  request.mockImplementation(async (path) => {
    if (path === "/integrations/") return [integration];
    if (path === "/incidents/") return [incident];
    if (path === "/documents/")
      return [{ source: "guide.pdf", chunk_count: 3 }];
    return {};
  });
});

describe("workspace", () => {
  it("shows live counts and navigates to integrations", async () => {
    render(<App />);
    expect(await screen.findByText("Payment timeout")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /^Integrations/ }));
    expect(screen.getByText("Payments API")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Filter integrations"), {
      target: { value: "missing" },
    });
    expect(screen.queryByText("Payments API")).not.toBeInTheDocument();
  });
  it("creates an integration through the form", async () => {
    render(<App />);
    await screen.findByText("Payment timeout");
    fireEvent.click(screen.getByRole("button", { name: /^Integrations/ }));
    fireEvent.click(screen.getByRole("button", { name: /Add integration/ }));
    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Orders" },
    });
    fireEvent.change(screen.getByLabelText("API URL"), {
      target: { value: "https://example.com/orders" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save" }));
    await waitFor(() =>
      expect(request).toHaveBeenCalledWith(
        "/integrations/",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            name: "Orders",
            base_url: "https://example.com/orders",
            http_method: "GET",
            is_active: true,
          }),
        }),
      ),
    );
    expect(await screen.findByText("Saved successfully.")).toBeInTheDocument();
  });
  it("executes a check and reports a created incident", async () => {
    request.mockImplementation(async (path) =>
      path === "/integrations/"
        ? [integration]
        : path === "/documents/"
          ? []
          : path === "/incidents/"
            ? []
            : { success: false },
    );
    render(<App />);
    await screen.findByText("Backend connected");
    fireEvent.click(screen.getByRole("button", { name: /^Integrations/ }));
    fireEvent.click(screen.getByRole("button", { name: /Run check/ }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "An incident was created",
    );
  });
  it("shows document search results with source and page", async () => {
    request.mockImplementation(async (path) => {
      if (path === "/documents/search")
        return [
          {
            id: "1",
            text: "Check the timeout setting.",
            metadata: { source: "guide.pdf", page_number: 2 },
            distance: 0.2,
          },
        ];
      return path === "/documents/"
        ? [{ source: "guide.pdf", chunk_count: 3 }]
        : [];
    });
    render(<App />);
    await screen.findByText("Backend connected");
    fireEvent.click(screen.getByRole("button", { name: /^Knowledge base/ }));
    fireEvent.change(screen.getByLabelText("Search document content"), {
      target: { value: "timeout" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Search" }));
    expect(
      await screen.findByText("Check the timeout setting."),
    ).toBeInTheDocument();
    expect(screen.getByText("Page 2")).toBeInTheDocument();
  });
  it("reports backend errors", async () => {
    request.mockRejectedValue(new Error("Cannot reach the API."));
    render(<App />);
    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Cannot reach the API.",
    );
  });
  it("closes dialogs with Escape and restores focus", async () => {
    render(<App />);
    await screen.findByText("Backend connected");
    fireEvent.click(screen.getByRole("button", { name: /^Integrations/ }));
    const add = screen.getByRole("button", { name: "Add integration" });
    add.focus();
    fireEvent.click(add);
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    fireEvent.keyDown(document, { key: "Escape" });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(add).toHaveFocus();
  });
  it("opens an incident and requests analysis", async () => {
    render(<App />);
    fireEvent.click(await screen.findByText("Payment timeout"));
    request.mockImplementation(async (path) =>
      path.includes("/analyze")
        ? {
            summary: "Check server logs",
            possible_causes: [],
            troubleshooting_steps: [],
            missing_information: [],
          }
        : [],
    );
    fireEvent.click(
      screen.getByRole("button", { name: "Analyze with Gemini" }),
    );
    await waitFor(() =>
      expect(request).toHaveBeenCalledWith("/incidents/1/analyze", {
        method: "POST",
      }),
    );
  });
});
