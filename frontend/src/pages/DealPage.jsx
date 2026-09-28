import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  analyzeDeal,
  createInteraction,
  getDeal,
  getIntelligenceBrief,
  getTimeline,
} from "../api";

const TYPE_OPTIONS = [
  { value: "call", label: "Call" },
  { value: "email", label: "Email" },
  { value: "meeting", label: "Meeting" },
];

const SENTIMENT_OPTIONS = [
  { value: "neutral", label: "Neutral" },
  { value: "positive", label: "Positive" },
  { value: "negative", label: "Negative" },
];

const OUTCOME_OPTIONS = [
  { value: "", label: "Outcome optional" },
  { value: "worked", label: "Worked" },
  { value: "failed", label: "Failed" },
  { value: "neutral", label: "Neutral" },
];

function formatMoney(value) {
  const number = Number(value || 0);

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(number);
}

function formatDate(value) {
  if (!value) return "—";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function titleCase(value) {
  if (!value) return "";

  return String(value)
    .replace(/[_-]/g, " ")
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function riskClass(value) {
  const normalized = String(value || "").toLowerCase();

  if (normalized === "high") return "dp-badge dp-risk-high";
  if (normalized === "low") return "dp-badge dp-risk-low";

  return "dp-badge dp-risk-medium";
}

function scoreTone(score) {
  const value = Number(score || 0);

  if (value >= 75) return "dp-score-good";
  if (value >= 50) return "dp-score-mid";

  return "dp-score-low";
}

function extractRecommendations(analysis) {
  const recommendations = [];

  if (Array.isArray(analysis?.recommendations)) {
    recommendations.push(...analysis.recommendations);
  }

  if (Array.isArray(analysis?.agent_results)) {
    analysis.agent_results.forEach((agent) => {
      if (Array.isArray(agent?.recommendations)) {
        recommendations.push(...agent.recommendations);
      }
    });
  }

  if (Array.isArray(analysis?.actions)) {
    recommendations.push(...analysis.actions);
  }

  return recommendations;
}

function normalizeList(value) {
  return Array.isArray(value) ? value : [];
}

export default function DealPage() {
  const { id } = useParams();

  const [deal, setDeal] = useState(null);
  const [timeline, setTimeline] = useState([]);

  const [intelligence, setIntelligence] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  const [loading, setLoading] = useState(true);
  const [intelligenceLoading, setIntelligenceLoading] = useState(false);
  const [analysisLoading, setAnalysisLoading] = useState(false);

  const [error, setError] = useState(null);
  const [intelligenceError, setIntelligenceError] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  const [interactionForm, setInteractionForm] = useState({
    type: "call",
    summary: "",
    sentiment: "neutral",
    strategy: "",
    outcome: "",
  });

  const [interactionSubmitting, setInteractionSubmitting] = useState(false);
  const [interactionMessage, setInteractionMessage] = useState(null);

  const loadDeal = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const [dealData, timelineData] = await Promise.all([
        getDeal(id),
        getTimeline(id),
      ]);

      setDeal(dealData);
      setTimeline(Array.isArray(timelineData) ? timelineData : []);

      return dealData;
    } catch (err) {
      setError(err.message || "Unable to load deal.");
      throw err;
    } finally {
      setLoading(false);
    }
  }, [id]);

  const loadIntelligence = useCallback(async (dealData) => {
    if (!dealData) return;

    setIntelligenceLoading(true);
    setIntelligenceError(null);

    try {
      const result = await getIntelligenceBrief(dealData);
      setIntelligence(result);
    } catch (err) {
      setIntelligenceError(
        err.message || "Unable to load deal intelligence."
      );
    } finally {
      setIntelligenceLoading(false);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const dealData = await loadDeal();

        if (!cancelled && dealData) {
          await loadIntelligence(dealData);
        }
      } catch {
        // Error state is already handled by loadDeal.
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, [loadDeal, loadIntelligence]);

  const handleInteractionChange = (event) => {
    const { name, value } = event.target;

    setInteractionForm((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleCreateInteraction = async (event) => {
    event.preventDefault();

    if (!interactionForm.summary.trim()) {
      setInteractionMessage({
        type: "error",
        text: "Add a short interaction summary first.",
      });
      return;
    }

    setInteractionSubmitting(true);
    setInteractionMessage(null);

    try {
      await createInteraction({
        deal_id: Number(id),
        stakeholder_id: null,
        type: interactionForm.type,
        summary: interactionForm.summary.trim(),
        sentiment: interactionForm.sentiment,
        strategy: interactionForm.strategy.trim(),
        outcome: interactionForm.outcome || null,
      });

      const [freshTimeline, freshDeal] = await Promise.all([
        getTimeline(id),
        getDeal(id),
      ]);

      setTimeline(Array.isArray(freshTimeline) ? freshTimeline : []);
      setDeal(freshDeal);

      await loadIntelligence(freshDeal);

      setInteractionForm({
        type: "call",
        summary: "",
        sentiment: "neutral",
        strategy: "",
        outcome: "",
      });

      setInteractionMessage({
        type: "success",
        text: "Interaction added successfully.",
      });
    } catch (err) {
      setInteractionMessage({
        type: "error",
        text: err.message || "Unable to add interaction.",
      });
    } finally {
      setInteractionSubmitting(false);
    }
  };

  const handleAnalyzeDeal = async () => {
    if (!deal) return;

    setAnalysisLoading(true);
    setAnalysisError(null);

    try {
      const [brief, agentResult] = await Promise.all([
        getIntelligenceBrief(deal),
        analyzeDeal(deal, timeline),
      ]);

      setIntelligence(brief);
      setAnalysis(agentResult);
    } catch (err) {
      setAnalysisError(err.message || "Unable to analyze this deal.");
    } finally {
      setAnalysisLoading(false);
    }
  };

  const recommendations = useMemo(
    () => extractRecommendations(analysis),
    [analysis]
  );

  const competitorSignals = normalizeList(
    intelligence?.competitor_signals
  );

  const marketEvents = normalizeList(intelligence?.market_events);
  const keyRisks = normalizeList(intelligence?.key_risks);
  const keyOpportunities = normalizeList(intelligence?.key_opportunities);

  const externalPressure = Number(
    intelligence?.external_pressure_score ??
      intelligence?.pressure_score ??
      0
  );

  if (loading) {
    return (
      <>
        <style>{styles}</style>
        <main className="dp-page">
          <div className="dp-loading-card">
            <div className="dp-spinner" />
            <p>Loading deal workspace…</p>
          </div>
        </main>
      </>
    );
  }

  if (error || !deal) {
    return (
      <>
        <style>{styles}</style>
        <main className="dp-page">
          <Link className="dp-back" to="/">
            ← Back to Dashboard
          </Link>

          <div className="dp-error-card">
            <h1>Unable to load deal</h1>
            <p>{error || "The requested deal could not be found."}</p>
            <button className="dp-button dp-button-primary" onClick={loadDeal}>
              Retry
            </button>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <style>{styles}</style>

      <main className="dp-page">
        <div className="dp-shell">
          <Link className="dp-back" to="/">
            ← Back to Dashboard
          </Link>

          <section className="dp-header">
            <div>
              <div className="dp-eyebrow">
                {deal.customer?.name || "Customer"}{" "}
                {deal.customer?.industry
                  ? `· ${deal.customer.industry}`
                  : ""}
              </div>

              <h1>{deal.title}</h1>

              <div className="dp-value">{formatMoney(deal.value)}</div>
            </div>

            <div className="dp-header-actions">
              <span className="dp-stage">
                {titleCase(deal.stage)}
              </span>

              <span className={riskClass(deal.risk_level)}>
                {titleCase(deal.risk_level)}
              </span>

              <span className={`dp-score ${scoreTone(deal.deal_score)}`}>
                Score {deal.deal_score ?? "—"}
              </span>
            </div>
          </section>

          <section className="dp-stat-grid">
            <div className="dp-stat">
              <span>Customer</span>
              <strong>{deal.customer?.name || "—"}</strong>
            </div>

            <div className="dp-stat">
              <span>Industry</span>
              <strong>{deal.customer?.industry || "—"}</strong>
            </div>

            <div className="dp-stat">
              <span>Stage</span>
              <strong>{titleCase(deal.stage)}</strong>
            </div>

            <div className="dp-stat">
              <span>External pressure</span>
              <strong>
                {intelligence
                  ? `${externalPressure}/100`
                  : "Not analyzed"}
              </strong>
            </div>
          </section>

          <section className="dp-section">
            <div className="dp-section-header">
              <div>
                <span className="dp-section-kicker">Relationships</span>
                <h2>Stakeholders</h2>
              </div>

              <span className="dp-section-count">
                {deal.stakeholders?.length || 0}
              </span>
            </div>

            {deal.stakeholders?.length ? (
              <div className="dp-stakeholder-grid">
                {deal.stakeholders.map((stakeholder) => (
                  <div className="dp-person" key={stakeholder.id}>
                    <div className="dp-avatar">
                      {(stakeholder.name || "?")
                        .charAt(0)
                        .toUpperCase()}
                    </div>

                    <div>
                      <strong>{stakeholder.name}</strong>
                      <span>{stakeholder.role || "Stakeholder"}</span>
                      {stakeholder.concern && (
                        <small>{stakeholder.concern}</small>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="dp-empty">
                No stakeholders have been added to this deal yet.
              </div>
            )}
          </section>

          <section className="dp-section">
            <div className="dp-section-header">
              <div>
                <span className="dp-section-kicker">Customer context</span>
                <h2>Log an interaction</h2>
              </div>
            </div>

            <form className="dp-form" onSubmit={handleCreateInteraction}>
              <div className="dp-form-row">
                <label>
                  Type
                  <select
                    name="type"
                    value={interactionForm.type}
                    onChange={handleInteractionChange}
                  >
                    {TYPE_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Sentiment
                  <select
                    name="sentiment"
                    value={interactionForm.sentiment}
                    onChange={handleInteractionChange}
                  >
                    {SENTIMENT_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label>
                  Outcome
                  <select
                    name="outcome"
                    value={interactionForm.outcome}
                    onChange={handleInteractionChange}
                  >
                    {OUTCOME_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <label>
                Summary
                <textarea
                  name="summary"
                  value={interactionForm.summary}
                  onChange={handleInteractionChange}
                  placeholder="What happened in the customer interaction?"
                  rows={4}
                />
              </label>

              <label>
                Strategy / next step
                <input
                  name="strategy"
                  value={interactionForm.strategy}
                  onChange={handleInteractionChange}
                  placeholder="Optional follow-up or next action"
                />
              </label>

              <div className="dp-form-footer">
                {interactionMessage && (
                  <span
                    className={
                      interactionMessage.type === "error"
                        ? "dp-form-message dp-form-error"
                        : "dp-form-message dp-form-success"
                    }
                  >
                    {interactionMessage.text}
                  </span>
                )}

                <button
                  className="dp-button dp-button-primary"
                  type="submit"
                  disabled={interactionSubmitting}
                >
                  {interactionSubmitting
                    ? "Saving…"
                    : "Add interaction"}
                </button>
              </div>
            </form>
          </section>

          <section className="dp-section">
            <div className="dp-section-header">
              <div>
                <span className="dp-section-kicker">Deal history</span>
                <h2>Timeline</h2>
              </div>

              <span className="dp-section-count">
                {timeline.length}
              </span>
            </div>

            {timeline.length ? (
              <div className="dp-timeline">
                {timeline.map((item) => (
                  <article className="dp-timeline-item" key={item.id}>
                    <div className="dp-timeline-marker" />

                    <div className="dp-timeline-main">
                      <div className="dp-timeline-top">
                        <span className="dp-timeline-type">
                          {titleCase(item.type)}
                        </span>

                        <span className="dp-timeline-date">
                          {formatDate(item.occurred_at)}
                        </span>
                      </div>

                      <p>{item.summary}</p>

                      <div className="dp-timeline-meta">
                        <span
                          className={`dp-sentiment dp-sentiment-${String(
                            item.sentiment || "neutral"
                          ).toLowerCase()}`}
                        >
                          {titleCase(item.sentiment)}
                        </span>

                        {item.outcome && (
                          <span>{titleCase(item.outcome)}</span>
                        )}

                        {item.strategy && (
                          <em>Next step: {item.strategy}</em>
                        )}
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="dp-empty">
                No interactions yet. Add the first customer interaction
                above.
              </div>
            )}
          </section>

          <section className="dp-section dp-intelligence-section">
            <div className="dp-section-header">
              <div>
                <span className="dp-section-kicker">
                  Market awareness
                </span>
                <h2>Deal intelligence</h2>
              </div>

              <button
                className="dp-button dp-button-secondary"
                onClick={() => loadIntelligence(deal)}
                disabled={intelligenceLoading}
              >
                {intelligenceLoading ? "Refreshing…" : "Refresh"}
              </button>
            </div>

            {intelligenceError && (
              <div className="dp-inline-error">
                {intelligenceError}
              </div>
            )}

            {intelligenceLoading && !intelligence ? (
              <div className="dp-loading-inline">
                <div className="dp-spinner" />
                <span>Building intelligence brief…</span>
              </div>
            ) : intelligence ? (
              <>
                <div className="dp-intelligence-overview">
                  <div>
                    <span>External pressure</span>
                    <strong>{externalPressure}/100</strong>
                  </div>

                  <div>
                    <span>Competitor signals</span>
                    <strong>{competitorSignals.length}</strong>
                  </div>

                  <div>
                    <span>Market events</span>
                    <strong>{marketEvents.length}</strong>
                  </div>

                  <div>
                    <span>Key risks</span>
                    <strong>{keyRisks.length}</strong>
                  </div>

                  <div>
                    <span>Opportunities</span>
                    <strong>{keyOpportunities.length}</strong>
                  </div>
                </div>

                <div className="dp-intelligence-grid">
                  <div className="dp-panel">
                    <div className="dp-panel-title">
                      Competitive signals
                    </div>

                    {competitorSignals.length ? (
                      <div className="dp-list">
                        {competitorSignals.slice(0, 5).map((signal, index) => (
                          <div
                            className="dp-list-item"
                            key={`${signal.competitor || "signal"}-${index}`}
                          >
                            <div>
                              <strong>
                                {signal.competitor || "Competitor"}
                              </strong>

                              <span>
                                {signal.headline ||
                                  signal.category ||
                                  "Competitive signal"}
                              </span>
                            </div>

                            {signal.impact && (
                              <span className="dp-impact">
                                {titleCase(signal.impact)}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="dp-empty">
                        No competitor signals found.
                      </div>
                    )}
                  </div>

                  <div className="dp-panel">
                    <div className="dp-panel-title">
                      Market events
                    </div>

                    {marketEvents.length ? (
                      <div className="dp-list">
                        {marketEvents.slice(0, 5).map((event, index) => (
                          <div
                            className="dp-list-item"
                            key={`${event.event_id || event.title || "event"}-${index}`}
                          >
                            <div>
                              <strong>
                                {event.title || "Market event"}
                              </strong>

                              <span>
                                {event.summary ||
                                  event.category ||
                                  "Relevant market activity"}
                              </span>
                            </div>

                            {event.impact_score != null && (
                              <span className="dp-impact">
                                {event.impact_score}
                              </span>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="dp-empty">
                        No relevant market events found.
                      </div>
                    )}
                  </div>

                  <div className="dp-panel">
                    <div className="dp-panel-title">
                      Key risks
                    </div>

                    {keyRisks.length ? (
                      <ul className="dp-simple-list dp-risk-list">
                        {keyRisks.map((risk, index) => (
                          <li key={index}>
                            {typeof risk === "string"
                              ? risk
                              : risk.title ||
                                risk.description ||
                                risk.detail ||
                                JSON.stringify(risk)}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <div className="dp-empty">
                        No key risks identified.
                      </div>
                    )}
                  </div>

                  <div className="dp-panel">
                    <div className="dp-panel-title">
                      Opportunities
                    </div>

                    {keyOpportunities.length ? (
                      <ul className="dp-simple-list dp-opportunity-list">
                        {keyOpportunities.map((opportunity, index) => (
                          <li key={index}>
                            {typeof opportunity === "string"
                              ? opportunity
                              : opportunity.title ||
                                opportunity.description ||
                                opportunity.detail ||
                                JSON.stringify(opportunity)}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <div className="dp-empty">
                        No specific opportunities identified.
                      </div>
                    )}
                  </div>
                </div>
              </>
            ) : (
              <div className="dp-empty">
                Intelligence hasn't been generated yet.
              </div>
            )}
          </section>

          <section className="dp-section dp-recommendations-section">
            <div className="dp-section-header">
              <div>
                <span className="dp-section-kicker">
                  Decision support
                </span>
                <h2>Recommended next actions</h2>
              </div>

              <button
                className="dp-button dp-button-primary"
                onClick={handleAnalyzeDeal}
                disabled={analysisLoading}
              >
                {analysisLoading
                  ? "Analyzing…"
                  : "Analyze deal"}
              </button>
            </div>

            {analysisError && (
              <div className="dp-inline-error">
                {analysisError}
              </div>
            )}

            {analysisLoading ? (
              <div className="dp-loading-inline">
                <div className="dp-spinner" />
                <span>
                  Running Risk Analyst and Next Best Action…
                </span>
              </div>
            ) : recommendations.length ? (
              <div className="dp-recommendation-list">
                {recommendations.map((recommendation, index) => (
                  <article
                    className="dp-recommendation"
                    key={`${recommendation.action || "recommendation"}-${index}`}
                  >
                    <div className="dp-recommendation-number">
                      {index + 1}
                    </div>

                    <div className="dp-recommendation-body">
                      <div className="dp-recommendation-top">
                        <h3>
                          {recommendation.action ||
                            recommendation.title ||
                            "Recommended action"}
                        </h3>

                        {recommendation.priority && (
                          <span className="dp-priority">
                            {titleCase(recommendation.priority)}
                          </span>
                        )}
                      </div>

                      {recommendation.rationale && (
                        <p>{recommendation.rationale}</p>
                      )}

                      {recommendation.expected_impact && (
                        <div className="dp-expected">
                          <strong>Expected impact:</strong>{" "}
                          {recommendation.expected_impact}
                        </div>
                      )}

                      <div className="dp-recommendation-meta">
                        {recommendation.category && (
                          <span>
                            {titleCase(recommendation.category)}
                          </span>
                        )}

                        {recommendation.risk && (
                          <span>{titleCase(recommendation.risk)}</span>
                        )}
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="dp-analysis-empty">
                <div>
                  <h3>Ready for deal analysis</h3>
                  <p>
                    Run the agent stack to combine deal context,
                    interaction history, competitive intelligence, and
                    next-best-action reasoning.
                  </p>
                </div>

                <button
                  className="dp-button dp-button-primary"
                  onClick={handleAnalyzeDeal}
                  disabled={analysisLoading}
                >
                  Analyze deal
                </button>
              </div>
            )}
          </section>

          <footer className="dp-footer">
            <span>Precedent</span>
            <span>Deal workspace</span>
          </footer>
        </div>
      </main>
    </>
  );
}

const styles = `
  :root {
    --dp-bg: #f5f6f8;
    --dp-surface: #ffffff;
    --dp-border: #e4e7ec;
    --dp-border-strong: #d8dce3;
    --dp-text: #172033;
    --dp-muted: #697386;
    --dp-subtle: #8a93a3;
    --dp-accent: #4f46e5;
    --dp-accent-soft: #eef0ff;
    --dp-success: #137a4b;
    --dp-success-soft: #e9f7ef;
    --dp-warning: #a86100;
    --dp-warning-soft: #fff4de;
    --dp-danger: #b42318;
    --dp-danger-soft: #fff0ef;
    --dp-shadow: 0 8px 30px rgba(19, 32, 51, 0.06);
  }

  * {
    box-sizing: border-box;
  }

  .dp-page {
    min-height: 100vh;
    background: var(--dp-bg);
    color: var(--dp-text);
    padding: 28px 20px 56px;
  }

  .dp-shell {
    width: min(1120px, 100%);
    margin: 0 auto;
  }

  .dp-back {
    display: inline-flex;
    margin-bottom: 20px;
    color: var(--dp-accent);
    text-decoration: none;
    font-weight: 600;
    font-size: 14px;
  }

  .dp-back:hover {
    text-decoration: underline;
  }

  .dp-header {
    display: flex;
    justify-content: space-between;
    gap: 24px;
    align-items: flex-start;
    background: var(--dp-surface);
    border: 1px solid var(--dp-border);
    border-radius: 18px;
    padding: 30px;
    box-shadow: var(--dp-shadow);
  }

  .dp-eyebrow {
    color: var(--dp-muted);
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  .dp-header h1 {
    margin: 0;
    font-size: clamp(28px, 4vw, 42px);
    line-height: 1.08;
    letter-spacing: -0.035em;
  }

  .dp-value {
    margin-top: 12px;
    color: var(--dp-accent);
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.02em;
  }

  .dp-header-actions {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 8px;
  }

  .dp-stage,
  .dp-badge,
  .dp-score,
  .dp-priority,
  .dp-impact {
    display: inline-flex;
    align-items: center;
    min-height: 32px;
    padding: 6px 11px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    white-space: nowrap;
  }

  .dp-stage {
    background: var(--dp-accent-soft);
    color: var(--dp-accent);
  }

  .dp-risk-high {
    background: var(--dp-danger-soft);
    color: var(--dp-danger);
  }

  .dp-risk-medium {
    background: var(--dp-warning-soft);
    color: var(--dp-warning);
  }

  .dp-risk-low {
    background: var(--dp-success-soft);
    color: var(--dp-success);
  }

  .dp-score {
    background: #f0f2f6;
    color: var(--dp-text);
  }

  .dp-score-good {
    background: #edf8f1;
    color: var(--dp-success);
  }

  .dp-score-mid {
    background: var(--dp-warning-soft);
    color: var(--dp-warning);
  }

  .dp-score-low {
    background: var(--dp-danger-soft);
    color: var(--dp-danger);
  }

  .dp-stat-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
    margin: 14px 0;
  }

  .dp-stat {
    background: var(--dp-surface);
    border: 1px solid var(--dp-border);
    border-radius: 14px;
    padding: 17px 18px;
  }

  .dp-stat span {
    display: block;
    color: var(--dp-muted);
    font-size: 12px;
    margin-bottom: 7px;
  }

  .dp-stat strong {
    display: block;
    font-size: 15px;
  }

  .dp-section {
    margin-top: 14px;
    background: var(--dp-surface);
    border: 1px solid var(--dp-border);
    border-radius: 18px;
    padding: 26px;
    box-shadow: var(--dp-shadow);
  }

  .dp-section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 20px;
  }

  .dp-section-kicker {
    display: block;
    color: var(--dp-subtle);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 5px;
  }

  .dp-section-header h2 {
    margin: 0;
    font-size: 20px;
    letter-spacing: -0.02em;
  }

  .dp-section-count {
    min-width: 30px;
    height: 30px;
    display: grid;
    place-items: center;
    border-radius: 999px;
    background: #f0f2f6;
    color: var(--dp-muted);
    font-size: 12px;
    font-weight: 700;
  }

  .dp-button {
    border: 1px solid transparent;
    border-radius: 10px;
    min-height: 42px;
    padding: 0 16px;
    font: inherit;
    font-size: 13px;
    font-weight: 700;
    cursor: pointer;
    transition:
      transform 120ms ease,
      box-shadow 120ms ease,
      background 120ms ease;
  }

  .dp-button:hover:not(:disabled) {
    transform: translateY(-1px);
  }

  .dp-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .dp-button-primary {
    background: var(--dp-accent);
    color: white;
    box-shadow: 0 5px 14px rgba(79, 70, 229, 0.16);
  }

  .dp-button-secondary {
    background: white;
    color: var(--dp-text);
    border-color: var(--dp-border-strong);
  }

  .dp-stakeholder-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .dp-person {
    display: flex;
    gap: 12px;
    padding: 14px;
    border: 1px solid var(--dp-border);
    border-radius: 13px;
  }

  .dp-avatar {
    flex: 0 0 38px;
    height: 38px;
    display: grid;
    place-items: center;
    border-radius: 10px;
    background: var(--dp-accent-soft);
    color: var(--dp-accent);
    font-weight: 800;
  }

  .dp-person strong,
  .dp-person span,
  .dp-person small {
    display: block;
  }

  .dp-person strong {
    font-size: 14px;
    margin-bottom: 3px;
  }

  .dp-person span {
    color: var(--dp-muted);
    font-size: 12px;
  }

  .dp-person small {
    color: var(--dp-subtle);
    margin-top: 5px;
    line-height: 1.4;
  }

  .dp-form {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }

  .dp-form-row {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
  }

  .dp-form label {
    display: flex;
    flex-direction: column;
    gap: 7px;
    color: var(--dp-muted);
    font-size: 12px;
    font-weight: 600;
  }

  .dp-form input,
  .dp-form select,
  .dp-form textarea {
    width: 100%;
    border: 1px solid var(--dp-border-strong);
    border-radius: 10px;
    background: white;
    color: var(--dp-text);
    padding: 12px 13px;
    font: inherit;
    font-size: 14px;
    outline: none;
    transition:
      border-color 120ms ease,
      box-shadow 120ms ease;
  }

  .dp-form textarea {
    resize: vertical;
  }

  .dp-form input:focus,
  .dp-form select:focus,
  .dp-form textarea:focus {
    border-color: var(--dp-accent);
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
  }

  .dp-form-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }

  .dp-form-message {
    font-size: 13px;
  }

  .dp-form-success {
    color: var(--dp-success);
  }

  .dp-form-error,
  .dp-inline-error {
    color: var(--dp-danger);
  }

  .dp-inline-error {
    margin-bottom: 16px;
    padding: 12px 14px;
    border-radius: 10px;
    background: var(--dp-danger-soft);
    font-size: 13px;
  }

  .dp-timeline {
    position: relative;
    margin-left: 6px;
    padding-left: 25px;
    border-left: 1px solid var(--dp-border);
  }

  .dp-timeline-item {
    position: relative;
    padding-bottom: 18px;
  }

  .dp-timeline-marker {
    position: absolute;
    left: -31px;
    top: 4px;
    width: 11px;
    height: 11px;
    border: 3px solid var(--dp-surface);
    border-radius: 999px;
    background: var(--dp-accent);
    box-shadow: 0 0 0 1px var(--dp-border-strong);
  }

  .dp-timeline-main {
    border: 1px solid var(--dp-border);
    border-radius: 13px;
    padding: 16px;
  }

  .dp-timeline-top {
    display: flex;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 8px;
  }

  .dp-timeline-type {
    font-size: 11px;
    font-weight: 800;
    color: var(--dp-accent);
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }

  .dp-timeline-date {
    color: var(--dp-subtle);
    font-size: 12px;
  }

  .dp-timeline-main p {
    margin: 0;
    color: var(--dp-text);
    line-height: 1.55;
  }

  .dp-timeline-meta {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
    margin-top: 11px;
    color: var(--dp-muted);
    font-size: 12px;
  }

  .dp-sentiment {
    font-weight: 700;
  }

  .dp-sentiment-negative {
    color: var(--dp-danger);
  }

  .dp-sentiment-positive {
    color: var(--dp-success);
  }

  .dp-sentiment-neutral {
    color: var(--dp-muted);
  }

  .dp-empty {
    padding: 22px;
    border: 1px dashed var(--dp-border-strong);
    border-radius: 12px;
    color: var(--dp-muted);
    font-size: 13px;
    text-align: center;
  }

  .dp-intelligence-overview {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 14px;
  }

  .dp-intelligence-overview > div {
    border: 1px solid var(--dp-border);
    border-radius: 12px;
    padding: 14px;
  }

  .dp-intelligence-overview span,
  .dp-intelligence-overview strong {
    display: block;
  }

  .dp-intelligence-overview span {
    color: var(--dp-muted);
    font-size: 11px;
    margin-bottom: 6px;
  }

  .dp-intelligence-overview strong {
    font-size: 18px;
  }

  .dp-intelligence-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }

  .dp-panel {
    border: 1px solid var(--dp-border);
    border-radius: 14px;
    padding: 18px;
  }

  .dp-panel-title {
    font-size: 13px;
    font-weight: 800;
    margin-bottom: 12px;
  }

  .dp-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .dp-list-item {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    padding: 11px 0;
    border-top: 1px solid var(--dp-border);
  }

  .dp-list-item:first-child {
    border-top: 0;
    padding-top: 0;
  }

  .dp-list-item:last-child {
    padding-bottom: 0;
  }

  .dp-list-item strong,
  .dp-list-item span {
    display: block;
  }

  .dp-list-item strong {
    font-size: 13px;
    margin-bottom: 3px;
  }

  .dp-list-item div span {
    color: var(--dp-muted);
    font-size: 12px;
    line-height: 1.45;
  }

  .dp-impact {
    background: #f0f2f6;
    color: var(--dp-muted);
  }

  .dp-simple-list {
    margin: 0;
    padding-left: 18px;
    color: var(--dp-text);
  }

  .dp-simple-list li {
    margin-bottom: 9px;
    line-height: 1.45;
    font-size: 13px;
  }

  .dp-risk-list li::marker {
    color: var(--dp-danger);
  }

  .dp-opportunity-list li::marker {
    color: var(--dp-success);
  }

  .dp-analysis-empty {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    padding: 18px;
    border: 1px solid var(--dp-border);
    border-radius: 14px;
  }

  .dp-analysis-empty h3 {
    margin: 0 0 5px;
    font-size: 15px;
  }

  .dp-analysis-empty p {
    margin: 0;
    color: var(--dp-muted);
    font-size: 13px;
    line-height: 1.5;
  }

  .dp-recommendation-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .dp-recommendation {
    display: flex;
    gap: 14px;
    padding: 16px;
    border: 1px solid var(--dp-border);
    border-radius: 14px;
  }

  .dp-recommendation-number {
    flex: 0 0 30px;
    height: 30px;
    display: grid;
    place-items: center;
    border-radius: 9px;
    background: var(--dp-accent-soft);
    color: var(--dp-accent);
    font-size: 12px;
    font-weight: 800;
  }

  .dp-recommendation-body {
    flex: 1;
    min-width: 0;
  }

  .dp-recommendation-top {
    display: flex;
    justify-content: space-between;
    gap: 14px;
    align-items: flex-start;
  }

  .dp-recommendation-top h3 {
    margin: 0;
    font-size: 14px;
    line-height: 1.4;
  }

  .dp-priority {
    background: #f0f2f6;
    color: var(--dp-muted);
  }

  .dp-recommendation-body p {
    margin: 8px 0 0;
    color: var(--dp-muted);
    line-height: 1.5;
    font-size: 13px;
  }

  .dp-expected {
    margin-top: 10px;
    color: var(--dp-text);
    font-size: 12px;
    line-height: 1.45;
  }

  .dp-recommendation-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-top: 10px;
    color: var(--dp-subtle);
    font-size: 11px;
  }

  .dp-loading-card,
  .dp-error-card {
    width: min(700px, 100%);
    margin: 12vh auto;
    padding: 30px;
    border-radius: 18px;
    border: 1px solid var(--dp-border);
    background: var(--dp-surface);
    box-shadow: var(--dp-shadow);
    text-align: center;
  }

  .dp-loading-inline {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 16px 0;
    color: var(--dp-muted);
    font-size: 13px;
  }

  .dp-spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #dfe3eb;
    border-top-color: var(--dp-accent);
    border-radius: 999px;
    animation: dp-spin 700ms linear infinite;
  }

  @keyframes dp-spin {
    to {
      transform: rotate(360deg);
    }
  }

  .dp-error-card h1 {
    margin-top: 0;
  }

  .dp-error-card p {
    color: var(--dp-muted);
    margin-bottom: 18px;
  }

  .dp-footer {
    display: flex;
    justify-content: space-between;
    padding: 22px 4px 0;
    color: var(--dp-subtle);
    font-size: 12px;
  }

  @media (max-width: 900px) {
    .dp-header {
      flex-direction: column;
    }

    .dp-header-actions {
      justify-content: flex-start;
    }

    .dp-stat-grid,
    .dp-intelligence-overview {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 700px) {
    .dp-page {
      padding: 18px 12px 40px;
    }

    .dp-section,
    .dp-header {
      padding: 20px;
      border-radius: 14px;
    }

    .dp-form-row,
    .dp-stakeholder-grid,
    .dp-intelligence-grid,
    .dp-stat-grid,
    .dp-intelligence-overview {
      grid-template-columns: 1fr;
    }

    .dp-form-footer,
    .dp-analysis-empty,
    .dp-section-header {
      align-items: flex-start;
      flex-direction: column;
    }

    .dp-recommendation-top,
    .dp-timeline-top {
      flex-direction: column;
      align-items: flex-start;
    }

    .dp-footer {
      flex-direction: column;
      gap: 5px;
    }
  }
`;