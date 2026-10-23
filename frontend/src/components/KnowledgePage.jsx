import React from "react";
import {
  ArrowRight,
  FileText,
  LoaderCircle,
  Plus,
  Search,
  Sparkles,
  Trash2,
  UploadCloud,
} from "lucide-react";
import { Empty } from "./Common.jsx";

export default function KnowledgePage({
  query,
  setQuery,
  results,
  search,
  documents,
  upload,
  disabled,
  busy,
  remove,
}) {
  return (
    <div className="knowledge-grid">
      <div>
        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Search your knowledge</h2>
              <p>Ask a question to find relevant document passages.</p>
            </div>
            <Sparkles size={21} className="purple-text" />
          </div>
          <form className="knowledge-search" onSubmit={search}>
            <label className="search-box">
              <Search size={18} />
              <input
                aria-label="Search document content"
                placeholder="Why is my API request timing out?"
                required
                maxLength={2000}
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </label>
            <button
              className="button"
              disabled={disabled || !query.trim() || !documents.length}
            >
              {busy === "search" ? (
                <LoaderCircle size={17} className="spin" />
              ) : (
                <ArrowRight size={17} />
              )}
              Search
            </button>
          </form>
          {results === null ? (
            <Empty title="Find the right context">
              Upload a PDF, then search in plain English. Results include their
              original source and page.
            </Empty>
          ) : results.length ? (
            <div className="results">
              {results.map((item, index) => (
                <article key={item.id} className="result">
                  <div>
                    <span className="result-number">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <strong>{item.metadata.source}</strong>
                    <span className="muted">
                      {item.metadata.page_number
                        ? `Page ${item.metadata.page_number}`
                        : `Chunk ${item.metadata.chunk_index + 1}`}
                    </span>
                  </div>
                  <p>{item.text}</p>
                  <small>
                    Vector distance: {item.distance.toFixed(3)} · Lower is
                    closer; relevance is not guaranteed.
                  </small>
                </article>
              ))}
            </div>
          ) : (
            <Empty title="No passages found">
              Add a document with relevant text and try another question.
            </Empty>
          )}
        </section>
      </div>
      <div>
        <section className="upload-card">
          <span className="upload-icon">
            <UploadCloud size={27} />
          </span>
          <h2>Build your knowledge base</h2>
          <p>Add API guides, runbooks, or troubleshooting notes.</p>
          <label
            className={`button upload-button ${disabled ? "disabled" : ""}`}
          >
            <Plus size={17} />
            {busy === "upload" ? "Processing PDF…" : "Upload a PDF"}
            <input
              type="file"
              accept=".pdf,application/pdf"
              aria-label="Upload PDF"
              disabled={disabled}
              onChange={upload}
            />
          </label>
          <small>PDF only · Up to 10 MB · Text-based files</small>
          <small>First use downloads the embedding model.</small>
        </section>
        <section className="panel document-list">
          <div className="panel-heading">
            <h2>
              Documents <span className="count">{documents.length}</span>
            </h2>
          </div>
          {documents.length ? (
            documents.map((item) => (
              <div className="document" key={item.source}>
                <FileText size={21} />
                <div>
                  <strong>{item.source}</strong>
                  <small>{item.chunk_count} chunks indexed</small>
                </div>
                <button
                  className="icon-button danger"
                  disabled={disabled}
                  aria-label={`Delete ${item.source}`}
                  onClick={() => remove("documents", item)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))
          ) : (
            <p className="muted document-empty">
              Your uploaded PDFs will appear here.
            </p>
          )}
        </section>
      </div>
    </div>
  );
}
