import { FormEvent, useMemo, useState } from "react";
import { Database, Loader2, MessageSquarePlus, Send, ShieldCheck } from "lucide-react";
import { sendChatMessage, type ChatResponse } from "./lib/api";
import { ResultsView } from "./components/ResultsView";
import { ToolTimeline } from "./components/ToolTimeline";
import "./styles/app.css";

type Message = {
  role: "user" | "assistant";
  content: string;
  response?: ChatResponse;
};

type Language = "fr" | "en";
type LanguageMode = "auto" | Language;

const copy = {
  fr: {
    autoMode: "Auto",
    subtitle: "Assistant MCP pour data.gouv.ci",
    newConversation: "Nouvelle conversation",
    promptTitle: "Exemples de requêtes",
    trustTitle: "Traçabilité",
    trustBody:
      "Les réponses proviennent d'outils MCP côté backend qui interrogent data.gouv.ci. Les données principales ne sont pas simulées.",
    selectedDataset: "Dataset sélectionné",
    eyebrow: "Plateforme eGov connectée",
    headline: "Interrogez les données publiques en langage naturel",
    status: "Exécution API réelle",
    assistantLabel: "Assistant",
    userLabel: "Vous",
    loading: "Exécution des outils...",
    error: "Je n'ai pas pu exécuter la requête. Vérifie que le backend est lancé.",
    backendUnreachable:
      "Impossible de joindre l'API backend. Lance le serveur FastAPI puis réessaie.",
    placeholder: "Pose une question sur les données publiques...",
    latestExecution: "Dernière exécution",
    intent: "Intention",
    language: "Langue",
    tools: "Outils",
    noTrace: "Les traces d'exécution apparaîtront après la première requête.",
    welcome:
      "Bonjour. Je peux rechercher, analyser et résumer les jeux de données publics de data.gouv.ci avec des appels API vérifiables.",
    prompts: [
      "Trouve les datasets liés à l'éducation",
      "Compare les investissements entre 2020 et 2023",
      "Résume le dataset sélectionné",
      "Montre les colonnes disponibles",
    ],
  },
  en: {
    autoMode: "Auto",
    subtitle: "MCP assistant for data.gouv.ci",
    newConversation: "New conversation",
    promptTitle: "Example requests",
    trustTitle: "Traceability",
    trustBody:
      "Responses come from backend MCP tools that query data.gouv.ci. Primary data is not simulated.",
    selectedDataset: "Selected dataset",
    eyebrow: "Connected eGov platform",
    headline: "Query public data in natural language",
    status: "Real API execution",
    assistantLabel: "Assistant",
    userLabel: "You",
    loading: "Executing tools...",
    error: "I could not execute the request. Check that the backend is running.",
    backendUnreachable: "The backend API is unreachable. Start the FastAPI server and try again.",
    placeholder: "Ask a question about public data...",
    latestExecution: "Latest execution",
    intent: "Intent",
    language: "Language",
    tools: "Tools",
    noTrace: "Execution traces will appear after the first request.",
    welcome:
      "Hello. I can search, analyze and summarize data.gouv.ci public datasets using verifiable API calls.",
    prompts: [
      "Search datasets about education",
      "Compare investments between 2020 and 2023",
      "Summarize the selected dataset",
      "Show available columns",
    ],
  },
} as const;

export default function App() {
  const [languageMode, setLanguageMode] = useState<LanguageMode>("auto");
  const [uiLanguage, setUiLanguage] = useState<Language>("fr");
  const language = uiLanguage;
  const t = copy[language];
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: copy.fr.welcome,
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedDataset, setSelectedDataset] = useState<string | null>(null);
  const [selectedDatasetTitle, setSelectedDatasetTitle] = useState<string | null>(null);

  const latestResponse = useMemo(
    () => [...messages].reverse().find((message) => message.response)?.response,
    [messages],
  );

  async function submitMessage(message: string, context: Record<string, unknown> = {}) {
    const clean = message.trim();
    if (!clean || isLoading) return;
    setInput("");
    setError(null);
    setMessages((current) => [...current, { role: "user", content: clean }]);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(clean, languageMode === "auto" ? undefined : languageMode, {
        dataset: selectedDataset,
        ...context,
      });
      if (languageMode === "auto") {
        setUiLanguage(response.language);
      }
      const nextSelectedDataset =
        typeof response.data.selected_dataset === "string"
          ? response.data.selected_dataset
          : selectedDataset;
      setSelectedDataset(nextSelectedDataset);
      const firstResult = Array.isArray(response.data.results) ? response.data.results[0] : null;
      if (firstResult && typeof firstResult === "object" && "title" in firstResult) {
        setSelectedDatasetTitle(String(firstResult.title));
      }
      setMessages((current) => [
        ...(languageMode === "auto"
          ? current.map((message, index) =>
              index === 0 && message.role === "assistant" && !message.response
                ? { ...message, content: copy[response.language].welcome }
                : message,
            )
          : current),
        {
          role: "assistant",
          content: response.answer,
          response,
        },
      ]);
    } catch (err) {
      const messageText = err instanceof Error ? err.message : "Unexpected error";
      const readableError = messageText === "BACKEND_UNREACHABLE" ? t.backendUnreachable : messageText;
      setError(readableError);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: messageText === "BACKEND_UNREACHABLE" ? t.backendUnreachable : t.error,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    void submitMessage(input);
  }

  function startNewConversation() {
    setSelectedDataset(null);
    setSelectedDatasetTitle(null);
    setError(null);
    setMessages([{ role: "assistant", content: t.welcome }]);
  }

  function changeLanguageMode(nextLanguageMode: LanguageMode) {
    setLanguageMode(nextLanguageMode);
    const nextUiLanguage = nextLanguageMode === "auto" ? uiLanguage : nextLanguageMode;
    setUiLanguage(nextUiLanguage);
    setSelectedDataset(null);
    setSelectedDatasetTitle(null);
    setError(null);
    setMessages([{ role: "assistant", content: copy[nextUiLanguage].welcome }]);
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <Database size={22} />
          </div>
          <div>
            <h1>Liwaza GovData</h1>
            <p>{t.subtitle}</p>
          </div>
        </div>

        <div className="language-switch" aria-label="Language selector">
          <button className={languageMode === "auto" ? "active" : ""} onClick={() => changeLanguageMode("auto")}>
            {t.autoMode}
          </button>
          <button className={languageMode === "fr" ? "active" : ""} onClick={() => changeLanguageMode("fr")}>
            FR
          </button>
          <button className={languageMode === "en" ? "active" : ""} onClick={() => changeLanguageMode("en")}>
            EN
          </button>
        </div>

        <button className="new-chat" onClick={startNewConversation}>
          <MessageSquarePlus size={16} />
          {t.newConversation}
        </button>

        <section className="prompt-section">
          <h2>{t.promptTitle}</h2>
          {t.prompts.map((prompt) => (
            <button className="prompt-button" key={prompt} onClick={() => void submitMessage(prompt)}>
              {prompt}
            </button>
          ))}
        </section>

        <section className="trust-card">
          <div className="panel-title">
            <ShieldCheck size={16} />
            {t.trustTitle}
          </div>
          <p>{t.trustBody}</p>
          {selectedDataset ? (
            <div className="selected-dataset">
              <span>{t.selectedDataset}</span>
              <strong>{selectedDatasetTitle ?? selectedDataset}</strong>
            </div>
          ) : null}
        </section>
      </aside>

      <section className="chat-area">
        <div className="chat-header">
          <div>
            <span className="eyebrow">{t.eyebrow}</span>
            <h2>{t.headline}</h2>
          </div>
          <span className="status-pill">{t.status}</span>
        </div>

        <div className="messages">
          {messages.map((message, index) => (
            <article className={`message ${message.role}`} key={index}>
              <div className="message-role">{message.role === "user" ? t.userLabel : t.assistantLabel}</div>
              <p>{message.content}</p>
              {message.response ? (
                <div className="message-details">
                  <ToolTimeline traces={message.response.traces} language={language} />
                  <ResultsView data={message.response.data} language={language} />
                  <div className="followups">
                    {message.response.followups.map((followup) => (
                      <button
                        key={followup}
                        onClick={() => void submitMessage(followup, { dataset: selectedDataset })}
                      >
                        {followup}
                      </button>
                    ))}
                  </div>
                </div>
              ) : null}
            </article>
          ))}
          {isLoading ? (
            <article className="message assistant">
              <div className="message-role">{t.assistantLabel}</div>
              <p className="loading-line">
                <Loader2 size={16} className="spin" />
                {t.loading}
              </p>
            </article>
          ) : null}
        </div>

        {error ? <div className="error-box">{error}</div> : null}

        <form className="composer" onSubmit={handleSubmit}>
          <input
            aria-label="Message"
            placeholder={t.placeholder}
            value={input}
            onChange={(event) => setInput(event.target.value)}
          />
          <button type="submit" disabled={isLoading || !input.trim()} aria-label="Send message">
            <Send size={18} />
          </button>
        </form>
      </section>

      <aside className="inspector">
        <div className="panel-title">{t.latestExecution}</div>
        {latestResponse ? (
          <>
            <div className="metric">
              <span>{t.intent}</span>
              <strong>{latestResponse.intent}</strong>
            </div>
            <div className="metric">
              <span>{t.language}</span>
              <strong>{latestResponse.language}</strong>
            </div>
            <div className="metric">
              <span>{t.tools}</span>
              <strong>{latestResponse.traces.length}</strong>
            </div>
            <ToolTimeline traces={latestResponse.traces} language={language} />
          </>
        ) : (
          <p className="muted">{t.noTrace}</p>
        )}
      </aside>
    </main>
  );
}
