import { useState } from 'react';
import './App.css';

const SUGGESTIONS = [
  'Show all active employees',
  'Who is on leave?',
  'List employees in Engineering',
  'Who earns more than 100000 USD?',
  'Show employees managed by Michael Chen',
];

function formatCell(value) {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'number') return value.toLocaleString();
  return String(value);
}

function formatColumnName(col) {
  return col.replace(/_/g, ' ');
}

export default function App() {
  const [question, setQuestion] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function handleSubmit(e) {
    e.preventDefault();
    const q = question.trim();
    if (!q) return;

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.detail || `Request failed (${res.status})`);
      }

      setResult(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleSuggestion(text) {
    setQuestion(text);
  }

  return (
    <div className="app">
      <header className="header">
        <h1>Employee Info Search</h1>
        <p>Ask questions about employees in plain English</p>
      </header>

      {/* Search */}
      <section className="search-card">
        <form className="search-form" onSubmit={handleSubmit}>
          <input
            className="search-input"
            type="text"
            placeholder="e.g. Show all employees in Engineering department"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
          />
          <button className="search-btn" type="submit" disabled={loading || !question.trim()}>
            {loading ? 'Searching…' : 'Search'}
          </button>
        </form>

        <div className="suggestions">
          {SUGGESTIONS.map((s) => (
            <button key={s} className="suggestion-chip" type="button" onClick={() => handleSuggestion(s)}>
              {s}
            </button>
          ))}
        </div>
      </section>

      {/* Error */}
      {error && <div className="error-banner">{error}</div>}

      {/* Loading */}
      {loading && (
        <div className="loading-spinner">
          <div className="spinner" />
        </div>
      )}

      {/* SQL Preview */}
      {result && (
        <div className="sql-card">
          <div className="label">Generated SQL</div>
          <code>{result.generated_sql}</code>
        </div>
      )}

      {/* Results */}
      {result && result.rows.length > 0 && (
        <div className="results-card">
          <div className="results-header">
            <h2>Results</h2>
            <span className="row-count">{result.row_count} row{result.row_count !== 1 ? 's' : ''}</span>
          </div>
          <div className="table-wrapper">
            <table className="results-table">
              <thead>
                <tr>
                  {result.columns.map((col) => (
                    <th key={col}>{formatColumnName(col)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {result.rows.map((row, i) => (
                  <tr key={i}>
                    {result.columns.map((col) => (
                      <td key={col}>{formatCell(row[col])}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Empty */}
      {result && result.rows.length === 0 && (
        <div className="empty-state">
          <div className="icon">🔍</div>
          <p>No results found for your query.</p>
        </div>
      )}

      {/* Initial state */}
      {!result && !loading && !error && (
        <div className="empty-state">
          <div className="icon">💬</div>
          <p>Type a question above to search employee records</p>
        </div>
      )}
    </div>
  );
}
