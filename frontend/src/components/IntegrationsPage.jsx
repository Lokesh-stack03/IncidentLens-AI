import React from "react";
import {
  Link2,
  LoaderCircle,
  Play,
  Plus,
  Search,
  Trash2,
  Pencil,
} from "lucide-react";
import { Empty, Badge } from "./Common.jsx";

export default function IntegrationsPage({
  integrations,
  visibleIntegrations,
  filter,
  setFilter,
  openIntegration,
  disabled,
  busy,
  execute,
  remove,
}) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h2>
            API integrations{" "}
            <span className="count">{integrations.length}</span>
          </h2>
          <p>Run checks on APIs you own or have permission to test.</p>
        </div>
        <button className="button" onClick={() => openIntegration()}>
          <Plus size={17} />
          Add integration
        </button>
      </div>
      <div className="toolbar">
        <label className="search-box">
          <Search size={17} />
          <input
            aria-label="Filter integrations"
            placeholder="Search integrations…"
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
          />
        </label>
      </div>
      {visibleIntegrations.length ? (
        <div className="integration-grid">
          {visibleIntegrations.map((item) => (
            <article className="integration-card" key={item.id}>
              <div className="integration-top">
                <span className="integration-icon">
                  <Link2 size={22} />
                </span>
                <Badge status={item.is_active ? "ACTIVE" : "INACTIVE"} />
              </div>
              <h3>{item.name}</h3>
              <p className="endpoint">
                <span>{item.http_method}</span>
                {item.base_url}
              </p>
              <div className="integration-actions">
                <button
                  className="button secondary"
                  disabled={disabled || !item.is_active}
                  onClick={() => execute(item)}
                >
                  {busy === `run-${item.id}` ? (
                    <LoaderCircle size={15} className="spin" />
                  ) : (
                    <Play size={15} />
                  )}
                  Run check
                </button>
                <div>
                  <button
                    className="icon-button"
                    aria-label={`Edit ${item.name}`}
                    onClick={() => openIntegration(item)}
                  >
                    <Pencil size={16} />
                  </button>
                  <button
                    className="icon-button danger"
                    disabled={disabled}
                    aria-label={`Delete ${item.name}`}
                    onClick={() => remove("integrations", item)}
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <Empty title="Connect your first API">
          Add an integration with a name, URL, and HTTP method to start checking
          requests.
        </Empty>
      )}
    </section>
  );
}
