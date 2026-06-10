import { CheckCircle2, Clock3, Database, Wrench } from "lucide-react";
import type { ToolTrace } from "../lib/api";

type Props = {
  traces: ToolTrace[];
  language: "fr" | "en";
};

export function ToolTimeline({ traces, language }: Props) {
  if (!traces.length) {
    return null;
  }

  const title = language === "fr" ? "Exécution des outils" : "Tool execution";

  return (
    <div className="tool-panel">
      <div className="panel-title">
        <Wrench size={16} />
        {title}
      </div>
      <div className="timeline">
        {traces.map((trace, index) => (
          <div className="timeline-item" key={`${trace.tool}-${index}`}>
            <CheckCircle2 size={16} className="success-icon" />
            <div>
              <div className="timeline-main">{trace.tool}</div>
              <div className="timeline-meta">
                <Database size={13} />
                {trace.source}
                {trace.endpoint ? ` · ${trace.endpoint}` : ""}
              </div>
            </div>
            <span className="duration">
              <Clock3 size={13} />
              {trace.duration_ms} ms
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
