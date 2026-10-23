import React from "react";
import { Sparkles, Trash2, X } from "lucide-react";
import { Badge } from "./Common.jsx";
import Dialog from "./Dialog.jsx";

export default function IncidentDetails({
  selected,
  setSelected,
  updateStatus,
  disabled,
  analyze,
  busy,
  notice,
  analysis,
  remove,
  setQuery,
  setResults,
  setPage,
}) {
  return (
    <Dialog
      titleId="incident-title"
      className="detail-modal"
      onClose={() => setSelected(null)}
    >
      <div className="modal-heading">
        <span className="eyebrow">
          INC-{String(selected.id).padStart(3, "0")}
        </span>
        <button
          className="icon-button"
          aria-label="Close incident"
          onClick={() => setSelected(null)}
        >
          <X size={20} />
        </button>
      </div>
      <h2 id="incident-title">{selected.title}</h2>
      <div className="detail-meta">
        <Badge status={selected.status} />
        <span>HTTP {selected.status_code || "no response"}</span>
      </div>
      <p className="error-detail">{selected.error_message}</p>
      <p className="endpoint">{selected.endpoint || "No endpoint recorded"}</p>
      <label>
        Incident status
        <select
          value={selected.status}
          disabled={disabled}
          onChange={(event) => updateStatus(selected, event.target.value)}
        >
          <option>OPEN</option>
          <option>INVESTIGATING</option>
          <option>RESOLVED</option>
        </select>
      </label>
      <div className="detail-actions">
        <button
          className="button"
          disabled={disabled}
          onClick={() => analyze(selected)}
        >
          <Sparkles size={17} />
          {busy === "analyze" ? "Analyzing…" : "Analyze with Gemini"}
        </button>
        <button
          className="button secondary"
          onClick={() => {
            setQuery(selected.error_message);
            setResults(null);
            setSelected(null);
            setPage("Knowledge base");
          }}
        >
          Find document context
        </button>
      </div>
      {notice?.error && (
        <p role="alert" className="form-error">
          {notice.text}
        </p>
      )}
      {analysis && (
        <div className="analysis">
          <h3>
            <Sparkles size={17} /> AI investigation
          </h3>
          <p>{analysis.summary}</p>
          {[
            ["Possible causes", analysis.possible_causes],
            ["Troubleshooting steps", analysis.troubleshooting_steps],
            ["Missing information", analysis.missing_information],
          ].map(([title, items]) => (
            <div key={title}>
              <h4>{title}</h4>
              <ul>
                {items.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          ))}
          <small>
            AI suggestions require verification against your actual system.
          </small>
        </div>
      )}
      <button
        className="text-link danger"
        disabled={disabled}
        onClick={() => remove("incidents", selected)}
      >
        <Trash2 size={15} />
        Delete incident
      </button>
    </Dialog>
  );
}
