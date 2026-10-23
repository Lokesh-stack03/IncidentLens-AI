import React from "react";
import { Search } from "lucide-react";

export const date = (value) =>
  new Date(value + (value.endsWith("Z") ? "" : "Z")).toLocaleString();

export function Empty({ title, children }) {
  return (
    <div className="empty">
      <div className="empty-icon">
        <Search size={24} />
      </div>
      <h3>{title}</h3>
      <p>{children}</p>
    </div>
  );
}

export function Badge({ status }) {
  return (
    <span className={`badge ${status.toLowerCase()}`}>
      {status.replaceAll("_", " ")}
    </span>
  );
}
