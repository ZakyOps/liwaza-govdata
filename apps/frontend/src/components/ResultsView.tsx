type Props = {
  data: Record<string, unknown>;
  language: "fr" | "en";
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function renderValue(value: unknown): string {
  if (value === null || value === undefined) return "-";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
  return JSON.stringify(value);
}

function truncate(value: unknown, maxLength = 150): string {
  const text = renderValue(value).replace(/\s+/g, " ").trim();
  return text.length > maxLength ? `${text.slice(0, maxLength)}...` : text;
}

function formatDate(value: unknown): string {
  if (typeof value !== "string") return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "2-digit" });
}

export function ResultsView({ data, language }: Props) {
  const results = Array.isArray(data.results) ? data.results : [];
  const schema = Array.isArray(data.schema) ? data.schema : [];
  const points = Array.isArray(data.points) ? data.points : [];
  const values = Array.isArray(data.values) ? data.values : [];
  const dataset = isRecord(data.dataset) ? data.dataset : null;
  const labels = {
    comparison: language === "fr" ? "Comparaison d'indicateur" : "Indicator comparison",
    values: language === "fr" ? "Valeurs" : "Period values",
    absoluteChange: language === "fr" ? "Variation absolue" : "Absolute change",
    percentChange: language === "fr" ? "Variation en pourcentage" : "Percent change",
    datasetSummary: language === "fr" ? "Synthèse du dataset" : "Dataset summary",
    origin: language === "fr" ? "Source" : "Origin",
    rows: language === "fr" ? "Lignes" : "Rows",
    updated: language === "fr" ? "Mis à jour" : "Updated",
    license: language === "fr" ? "Licence" : "License",
    sampleRows:
      language === "fr"
        ? "lignes d'exemple réelles récupérées depuis data.gouv.ci."
        : "real sample rows fetched from data.gouv.ci.",
    publicDatasets: language === "fr" ? "Datasets publics" : "Public datasets",
    schema: language === "fr" ? "Schéma du dataset" : "Dataset schema",
    chartData: language === "fr" ? "Données pour graphique" : "Chart data",
    rawPayload: language === "fr" ? "Données structurées" : "Raw structured payload",
    noResults: language === "fr" ? "Aucun résultat trouvé" : "No results found",
    noResultsBody:
      language === "fr"
        ? "La recherche n'a retourné aucun dataset. Essayez une requête plus générale ou un autre thème."
        : "The search did not return any dataset. Try a broader query or another topic.",
  };

  if (data.count === 0 && Array.isArray(data.results) && data.results.length === 0) {
    return (
      <div className="result-panel empty-state">
        <div className="panel-title">{labels.noResults}</div>
        <p>{labels.noResultsBody}</p>
      </div>
    );
  }

  if (values.length > 0) {
    const numericPercent = typeof data.percent_change === "number" ? data.percent_change.toFixed(2) : "-";
    return (
      <div className="result-panel">
        <div className="panel-title">{labels.comparison}</div>
        <div className="summary-grid">
          <div className="summary-card">
            <span>{labels.values}</span>
            <strong>{values.length}</strong>
          </div>
          <div className="summary-card">
            <span>{labels.absoluteChange}</span>
            <strong>{renderValue(data.absolute_change)}</strong>
          </div>
          <div className="summary-card">
            <span>{labels.percentChange}</span>
            <strong>{numericPercent}%</strong>
          </div>
        </div>
        <div className="compact-list">
          {values.filter(isRecord).map((item, index) => (
            <div className="compact-row" key={index}>
              <span>{renderValue(item.year)}</span>
              <strong>{renderValue(item.value)}</strong>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (dataset) {
    return (
      <div className="result-panel">
        <div className="panel-title">{labels.datasetSummary}</div>
        <div className="dataset-summary">
          <h3>{renderValue(dataset.title)}</h3>
          <p>{truncate(dataset.description, 320)}</p>
          <div className="meta-grid">
            <div>
              <span>{labels.origin}</span>
              <strong>{truncate(dataset.origin, 80)}</strong>
            </div>
            <div>
              <span>{labels.rows}</span>
              <strong>{renderValue(dataset.count)}</strong>
            </div>
            <div>
              <span>{labels.updated}</span>
              <strong>{formatDate(dataset.updatedAt)}</strong>
            </div>
            <div>
              <span>{labels.license}</span>
              <strong>{truncate(dataset.license, 80)}</strong>
            </div>
          </div>
        </div>
        {Array.isArray(data.sample_rows) ? (
          <div className="sample-note">{data.sample_rows.length} {labels.sampleRows}</div>
        ) : null}
      </div>
    );
  }

  if (results.length > 0) {
    const rows = results.filter(isRecord).slice(0, 8);
    return (
      <div className="result-panel">
        <div className="panel-title">{labels.publicDatasets}</div>
        <div className="dataset-list">
          {rows.map((row, index) => (
            <article className="dataset-item" key={`${renderValue(row.slug)}-${index}`}>
              <div className="dataset-rank">{index + 1}</div>
              <div>
                <h3>{renderValue(row.title)}</h3>
                <p>{truncate(row.description, 230)}</p>
                <div className="dataset-meta">
                  <span>{truncate(row.origin, 70)}</span>
                  <span>{formatDate(row.updatedAt)}</span>
                  <span>{renderValue(row.count)} {language === "fr" ? "lignes" : "rows"}</span>
                </div>
              </div>
            </article>
          ))}
        </div>
      </div>
    );
  }

  if (schema.length > 0) {
    const rows = schema.filter(isRecord).slice(0, 12);
    return (
      <div className="result-panel">
        <div className="panel-title">{labels.schema}</div>
        <div className="schema-grid">
          {rows.map((field, index) => (
            <div className="schema-card" key={index}>
              <strong>{renderValue(field.key)}</strong>
              <span>{renderValue(field.type)}</span>
              <p>{renderValue(field.title)}</p>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (points.length > 0) {
    return (
      <div className="result-panel">
        <div className="panel-title">{labels.chartData}</div>
        <div className="chart-preview">
          {points.slice(0, 18).map((point, index) => {
            const record = isRecord(point) ? point : {};
            const height = Math.max(12, Math.min(120, Number(record.y) || 24));
            return (
              <div className="bar-item" key={index}>
                <div className="bar" style={{ height }} />
                <span>{renderValue(record.x)}</span>
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  if (Object.keys(data).length > 0) {
    return (
      <div className="result-panel">
        <div className="panel-title">{labels.rawPayload}</div>
        <pre>{JSON.stringify(data, null, 2)}</pre>
      </div>
    );
  }

  return null;
}
