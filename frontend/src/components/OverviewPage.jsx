import React from "react";
import {
  Activity,
  ArrowRight,
  BookOpen,
  CheckCircle2,
  Link2,
  ShieldCheck,
  Sparkles,
} from "lucide-react";

export default function OverviewPage({
  incidents,
  active,
  open,
  documents,
  integrations,
  incidentTable,
  navigate,
}) {
  return (
    <>
      <div className="stats-grid">
        {[
          [
            "Total integrations",
            integrations.length,
            `${active.length} active connections`,
            Link2,
            "blue",
          ],
          [
            "Open incidents",
            open.length,
            "Awaiting investigation or resolution",
            Activity,
            "orange",
          ],
          [
            "Resolved incidents",
            incidents.length - open.length,
            "Investigated and closed",
            CheckCircle2,
            "green",
          ],
          [
            "Knowledge documents",
            documents.length,
            `${documents.reduce((sum, item) => sum + item.chunk_count, 0)} searchable chunks`,
            BookOpen,
            "purple",
          ],
        ].map(([label, count, caption, Icon, color]) => (
          <div className="stat-card" key={label}>
            <div className="stat-top">
              {label}
              <span className={`stat-icon ${color}`}>
                <Icon size={18} />
              </span>
            </div>
            <strong>{count}</strong>
            <small>{caption}</small>
          </div>
        ))}
      </div>
      <div className="overview-grid">
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>
                Recent incidents{" "}
                <span className="count">{incidents.length}</span>
              </h2>
              <p>The latest activity across your integrations</p>
            </div>
            <button className="text-link" onClick={() => navigate("Incidents")}>
              View all <ArrowRight size={15} />
            </button>
          </div>
          {incidentTable([...incidents].reverse().slice(0, 5))}
        </section>
        <section className="insight-card">
          <span className="insight-icon">
            <Sparkles size={22} />
          </span>
          <span className="eyebrow">LESS GUESSWORK</span>
          <h2>
            Give every incident
            <br />a little more context.
          </h2>
          <p>
            Upload your runbooks and API guides. Find relevant passages when
            something goes wrong.
          </p>
          <button className="button" onClick={() => navigate("Knowledge base")}>
            Explore knowledge base <ArrowRight size={16} />
          </button>
          <div className="insight-foot">
            <ShieldCheck size={15} /> Documents stored locally
          </div>
        </section>
      </div>
      <section className="panel getting-started">
        <div>
          <span className="eyebrow">A SIMPLE WORKFLOW</span>
          <h2>From API failure to a plan of action</h2>
        </div>
        <div className="workflow">
          {[
            ["01", "Connect", "Add an API integration"],
            ["02", "Execute", "Capture failed requests"],
            ["03", "Investigate", "Analyze and find context"],
          ].map(([number, title, text]) => (
            <div key={number}>
              <span>{number}</span>
              <div>
                <strong>{title}</strong>
                <p>{text}</p>
              </div>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
