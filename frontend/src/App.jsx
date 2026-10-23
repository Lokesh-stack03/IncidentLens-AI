import { Empty, Badge, date } from "./components/Common.jsx";
import IncidentDetails from "./components/IncidentDetails.jsx";
import RecordForm from "./components/RecordForm.jsx";
import KnowledgePage from "./components/KnowledgePage.jsx";
import IncidentsPage from "./components/IncidentsPage.jsx";
import IntegrationsPage from "./components/IntegrationsPage.jsx";
import OverviewPage from "./components/OverviewPage.jsx";
import React, { useEffect, useState } from "react";
import {
  Activity,
  ArrowRight,
  BookOpen,
  CircleHelp,
  LayoutDashboard,
  Link2,
  LoaderCircle,
  RefreshCw,
  X,
} from "lucide-react";
import { request } from "./api.js";

const pages = [
  ["Overview", LayoutDashboard],
  ["Integrations", Link2],
  ["Incidents", Activity],
  ["Knowledge base", BookOpen],
];
const emptyIntegration = {
  name: "",
  base_url: "",
  http_method: "GET",
  is_active: true,
};
export default function App() {
  const [page, setPage] = useState("Overview");
  const [integrations, setIntegrations] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [busy, setBusy] = useState("");
  const [notice, setNotice] = useState(null);
  const [modal, setModal] = useState(null);
  const [form, setForm] = useState(emptyIntegration);
  const [filter, setFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [selected, setSelected] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);

  async function load() {
    setLoading(true);
    try {
      const [items, events, files] = await Promise.all([
        request("/integrations/"),
        request("/incidents/"),
        request("/documents/"),
      ]);
      setIntegrations(items);
      setIncidents(events);
      setDocuments(files);
      setConnected(true);
    } catch (error) {
      setConnected(false);
      setNotice({ error: true, text: error.message });
    } finally {
      setLoading(false);
    }
  }
  useEffect(() => {
    load();
  }, []);

  // All actions share the same loading and error feedback.
  async function act(label, action) {
    setBusy(label);
    setNotice(null);
    try {
      await action();
    } catch (error) {
      setNotice({ error: true, text: error.message });
    } finally {
      setBusy("");
    }
  }
  function navigate(next) {
    setPage(next);
    setFilter("");
    setSelected(null);
    setAnalysis(null);
  }
  function openIntegration(item) {
    setForm(item || { ...emptyIntegration });
    setModal("integration");
  }
  function openIncident() {
    setForm({
      integration_id: integrations[0]?.id || "",
      title: "",
      error_message: "",
      status: "OPEN",
      status_code: "",
      endpoint: "",
    });
    setModal("incident");
  }
  async function save(event) {
    event.preventDefault();
    await act("save", async () => {
      const isIntegration = modal === "integration";
      const payload = isIntegration
        ? form
        : {
            ...form,
            integration_id: Number(form.integration_id),
            status_code:
              form.status_code === "" ? null : Number(form.status_code),
            endpoint: form.endpoint || null,
          };
      await request(
        `/${isIntegration ? "integrations" : "incidents"}/${form.id || ""}`,
        {
          method: form.id ? "PUT" : "POST",
          body: JSON.stringify(payload),
        },
      );
      setModal(null);
      await load();
      setNotice({ text: "Saved successfully." });
    });
  }
  async function execute(item) {
    await act(`run-${item.id}`, async () => {
      const result = await request(`/integrations/${item.id}/execute`, {
        method: "POST",
      });
      await load();
      setNotice({
        error: !result.success,
        text: result.success
          ? `${item.name} responded successfully.`
          : `${item.name} failed. An incident was created — open Incidents to investigate.`,
      });
    });
  }
  async function remove(kind, item) {
    if (
      !window.confirm(
        `Delete ${item.name || item.title || item.source}? This cannot be undone.`,
      )
    )
      return;
    await act("delete", async () => {
      const path =
        kind === "documents"
          ? `/documents/?source=${encodeURIComponent(item.source)}`
          : `/${kind}/${item.id}`;
      await request(path, { method: "DELETE" });
      setSelected(null);
      setResults(null);
      await load();
      setNotice({ text: "Deleted successfully." });
    });
  }
  async function updateStatus(item, status) {
    await act("status", async () => {
      const updated = await request(`/incidents/${item.id}`, {
        method: "PUT",
        body: JSON.stringify({ ...item, status }),
      });
      setSelected(updated);
      await load();
    });
  }
  async function analyze(item) {
    setAnalysis(null);
    await act("analyze", async () => {
      setAnalysis(
        await request(`/incidents/${item.id}/analyze`, { method: "POST" }),
      );
    });
  }
  async function upload(event) {
    const file = event.target.files[0];
    event.target.value = "";
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      setNotice({ error: true, text: "PDF must be 10 MB or smaller." });
      return;
    }
    await act("upload", async () => {
      const body = new FormData();
      body.append("file", file);
      const result = await request("/documents/upload", {
        method: "POST",
        body,
      });
      await load();
      setNotice({
        text: `${result.source}: ${result.page_count} pages processed into ${result.chunk_count} searchable chunks.`,
      });
    });
  }
  async function search(event) {
    event.preventDefault();
    await act("search", async () => {
      setResults(
        await request("/documents/search", {
          method: "POST",
          body: JSON.stringify({ query, top_k: 3 }),
        }),
      );
    });
  }

  const open = incidents.filter((item) => item.status !== "RESOLVED");
  const active = integrations.filter((item) => item.is_active);
  const visibleIncidents = [...incidents]
    .reverse()
    .filter(
      (item) =>
        (statusFilter === "ALL" || item.status === statusFilter) &&
        `${item.title} ${item.error_message}`
          .toLowerCase()
          .includes(filter.toLowerCase()),
    );
  const visibleIntegrations = integrations.filter((item) =>
    `${item.name} ${item.base_url}`
      .toLowerCase()
      .includes(filter.toLowerCase()),
  );
  const disabled = Boolean(busy);
  const field = (key, value) => setForm({ ...form, [key]: value });

  function incidentTable(items) {
    return items.length ? (
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Incident</th>
              <th>Integration</th>
              <th>Status</th>
              <th>Detected</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>
                  <button
                    className="text-button"
                    onClick={() => {
                      setSelected(item);
                      setAnalysis(null);
                    }}
                  >
                    {item.title}
                  </button>
                  <small>
                    INC-{String(item.id).padStart(3, "0")} ·{" "}
                    {item.status_code || "No response"}
                  </small>
                </td>
                <td>
                  {integrations.find((i) => i.id === item.integration_id)
                    ?.name || `#${item.integration_id}`}
                </td>
                <td>
                  <Badge status={item.status} />
                </td>
                <td className="muted nowrap">{date(item.created_at)}</td>
                <td>
                  <button
                    className="icon-button"
                    aria-label={`View incident ${item.id}`}
                    onClick={() => {
                      setSelected(item);
                      setAnalysis(null);
                    }}
                  >
                    <ArrowRight size={17} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    ) : (
      <Empty title="No incidents here">
        New API failures will appear here. You can also report an incident
        manually.
      </Empty>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a
          className="brand"
          href="#"
          onClick={(event) => {
            event.preventDefault();
            navigate("Overview");
          }}
        >
          <span className="brand-icon">
            <Activity size={25} />
          </span>
          <span>
            IncidentLens<span className="brand-ai">AI</span>
          </span>
        </a>
        <div className="workspace">
          <span className="workspace-avatar">IL</span>
          <div>
            Student workspace<small>Local environment</small>
          </div>
          <span className="workspace-dot" />
        </div>
        <div className="nav-label">WORKSPACE</div>
        <nav aria-label="Main navigation">
          {pages.map(([name, Icon]) => (
            <button
              key={name}
              className={page === name ? "nav-item current" : "nav-item"}
              onClick={() => navigate(name)}
            >
              <Icon size={19} />
              {name}
              {name === "Incidents" && open.length > 0 && (
                <span className="nav-count">{open.length}</span>
              )}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div className="help-card">
            <CircleHelp size={21} />
            <strong>Built to investigate.</strong>
            <p>Connect an API, capture a failure, and find your next step.</p>
            <a
              href="http://127.0.0.1:8000/docs"
              target="_blank"
              rel="noreferrer"
            >
              Explore API docs <ArrowRight size={14} />
            </a>
          </div>
          <div className="sidebar-footer">
            <span className={`connection-dot ${connected ? "online" : ""}`} />
            {connected ? "Backend connected" : "Backend unavailable"}
            <span>v1.0</span>
          </div>
        </div>
      </aside>
      <div className="main-shell">
        <header className="topbar">
          <div>
            Workspace <span>/</span> <strong>{page}</strong>
          </div>
          <div className="topbar-right">
            <span className="environment">
              <span className="connection-dot online" /> Development
            </span>
            <span className="avatar">S</span>
          </div>
        </header>
        <main>
          <div className="page-heading">
            <div>
              <div className="eyebrow">YOUR OPERATIONS, IN FOCUS</div>
              <h1>
                {page === "Overview"
                  ? "A clearer view of every incident."
                  : page}
              </h1>
              <p>
                {
                  {
                    Overview:
                      "Monitor your integrations. Investigate with context. Get back to building.",
                    Integrations:
                      "Connect your APIs and check how they respond.",
                    Incidents:
                      "Turn failures into clear, actionable next steps.",
                    "Knowledge base":
                      "Your troubleshooting documents, one search away.",
                  }[page]
                }
              </p>
            </div>
            <button
              className="button secondary"
              disabled={loading || disabled}
              onClick={load}
            >
              <RefreshCw size={16} className={loading ? "spin" : ""} />
              Refresh
            </button>
          </div>
          {notice && (
            <div
              role={notice.error ? "alert" : "status"}
              className={`notice ${notice.error ? "error" : ""}`}
            >
              <span>{notice.text}</span>
              <button
                className="icon-button"
                aria-label="Dismiss notification"
                onClick={() => setNotice(null)}
              >
                <X size={17} />
              </button>
            </div>
          )}
          {loading && (
            <div className="loading" role="status">
              <LoaderCircle size={18} className="spin" /> Loading workspace…
            </div>
          )}

          {page === "Overview" && (
            <OverviewPage
              incidents={incidents}
              active={active}
              open={open}
              documents={documents}
              integrations={integrations}
              incidentTable={incidentTable}
              navigate={navigate}
            />
          )}

          {page === "Integrations" && (
            <IntegrationsPage
              integrations={integrations}
              visibleIntegrations={visibleIntegrations}
              filter={filter}
              setFilter={setFilter}
              openIntegration={openIntegration}
              disabled={disabled}
              busy={busy}
              execute={execute}
              remove={remove}
            />
          )}

          {page === "Incidents" && (
            <IncidentsPage
              integrations={integrations}
              openIncident={openIncident}
              filter={filter}
              setFilter={setFilter}
              statusFilter={statusFilter}
              setStatusFilter={setStatusFilter}
              incidentTable={incidentTable}
              visibleIncidents={visibleIncidents}
            />
          )}

          {page === "Knowledge base" && (
            <KnowledgePage
              query={query}
              setQuery={setQuery}
              results={results}
              search={search}
              documents={documents}
              upload={upload}
              disabled={disabled}
              busy={busy}
              remove={remove}
            />
          )}
          <footer className="page-footer">
            IncidentLens AI <span>Made for clearer troubleshooting.</span>
          </footer>
        </main>
      </div>

      {modal && (
        <RecordForm
          modal={modal}
          form={form}
          field={field}
          save={save}
          disabled={disabled}
          busy={busy}
          notice={notice}
          setModal={setModal}
          integrations={integrations}
        />
      )}

      {selected && (
        <IncidentDetails
          selected={selected}
          setSelected={setSelected}
          updateStatus={updateStatus}
          disabled={disabled}
          analyze={analyze}
          busy={busy}
          notice={notice}
          analysis={analysis}
          remove={remove}
          setQuery={setQuery}
          setResults={setResults}
          setPage={setPage}
        />
      )}
    </div>
  );
}
