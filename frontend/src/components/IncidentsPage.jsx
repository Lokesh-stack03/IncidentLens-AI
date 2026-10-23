import React from "react";
import { Plus, Search } from "lucide-react";

export default function IncidentsPage({
  integrations,
  openIncident,
  filter,
  setFilter,
  statusFilter,
  setStatusFilter,
  incidentTable,
  visibleIncidents,
}) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <h2>Incident activity</h2>
          <p>Track the full journey from detection to resolution.</p>
        </div>
        <button
          className="button"
          disabled={!integrations.length}
          onClick={openIncident}
        >
          <Plus size={17} />
          Report incident
        </button>
      </div>
      <div className="toolbar">
        <label className="search-box">
          <Search size={17} />
          <input
            aria-label="Filter incidents"
            placeholder="Search incidents…"
            value={filter}
            onChange={(event) => setFilter(event.target.value)}
          />
        </label>
        <select
          aria-label="Filter by status"
          value={statusFilter}
          onChange={(event) => setStatusFilter(event.target.value)}
        >
          <option value="ALL">All statuses</option>
          <option value="OPEN">Open</option>
          <option value="INVESTIGATING">Investigating</option>
          <option value="RESOLVED">Resolved</option>
        </select>
      </div>
      {incidentTable(visibleIncidents)}
    </section>
  );
}
