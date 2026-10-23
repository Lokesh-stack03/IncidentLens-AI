import React from "react";
import { X } from "lucide-react";
import Dialog from "./Dialog.jsx";

export default function RecordForm({
  modal,
  form,
  field,
  save,
  disabled,
  busy,
  notice,
  setModal,
  integrations,
}) {
  return (
    <Dialog titleId="form-title" onClose={() => setModal(null)}>
      <div className="modal-heading">
        <h2 id="form-title">
          {modal === "integration"
            ? `${form.id ? "Edit" : "Add"} integration`
            : "Report incident"}
        </h2>
        <button
          className="icon-button"
          aria-label="Close form"
          onClick={() => setModal(null)}
        >
          <X size={20} />
        </button>
      </div>
      <form onSubmit={save}>
        {modal === "integration" ? (
          <>
            <label>
              Name
              <input
                required
                maxLength={100}
                value={form.name}
                onChange={(event) => field("name", event.target.value)}
                placeholder="e.g. Payments API"
              />
            </label>
            <label>
              API URL
              <input
                type="url"
                required
                maxLength={500}
                value={form.base_url}
                onChange={(event) => field("base_url", event.target.value)}
                placeholder="https://api.example.com/health"
              />
            </label>
            <label>
              HTTP method
              <select
                value={form.http_method}
                onChange={(event) => field("http_method", event.target.value)}
              >
                {["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD"].map(
                  (method) => (
                    <option key={method}>{method}</option>
                  ),
                )}
              </select>
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={(event) => field("is_active", event.target.checked)}
              />
              Active integration
            </label>
            <p className="muted">
              Run check sends a real HTTP request. Use an endpoint you have
              permission to test.
            </p>
          </>
        ) : (
          <>
            <label>
              Integration
              <select
                required
                value={form.integration_id}
                onChange={(event) =>
                  field("integration_id", event.target.value)
                }
              >
                {integrations.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.name}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Title
              <input
                required
                maxLength={255}
                value={form.title}
                onChange={(event) => field("title", event.target.value)}
              />
            </label>
            <label>
              Error message
              <textarea
                required
                rows={3}
                value={form.error_message}
                onChange={(event) => field("error_message", event.target.value)}
              />
            </label>
            <label>
              HTTP status (optional)
              <input
                type="number"
                min="100"
                max="599"
                value={form.status_code}
                onChange={(event) => field("status_code", event.target.value)}
              />
            </label>
            <label>
              Endpoint (optional)
              <input
                value={form.endpoint}
                onChange={(event) => field("endpoint", event.target.value)}
              />
            </label>
          </>
        )}
        {notice?.error && (
          <p role="alert" className="form-error">
            {notice.text}
          </p>
        )}
        <div className="modal-actions">
          <button
            type="button"
            className="button secondary"
            onClick={() => setModal(null)}
          >
            Cancel
          </button>
          <button className="button" disabled={disabled}>
            {busy === "save" ? "Saving…" : "Save"}
          </button>
        </div>
      </form>
    </Dialog>
  );
}
