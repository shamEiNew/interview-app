import { useState, type FormEvent } from 'react';
import katex from 'katex';
import { useMemo } from 'react';

const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined) || 'http://localhost:8000';

type ApiResult = {
  result?: string | string[];
  error?: string;
};
type MathBlockProps = {
  latex: string;
};


function MathBlock({ latex }: MathBlockProps) {
  const html = useMemo(() => {
    const expr = `x = ${latex}`;
    try {
      return katex.renderToString(expr, {
        throwOnError: false, // do not crash, show error in output instead
      });
    } catch (error) {
      console.error('KaTeX render error:', error);
      return '';
    }
  }, [latex]);

  if (!html) {
    return (
      <div className="text-xs text-red-600">
        Error rendering math expression
      </div>
    );
  }

  return <span dangerouslySetInnerHTML={{ __html: html }} />;
}


function App() {
  const [equation, setEquation] = useState<string>('');
  const [result, setResult] = useState<string[]>([]); // store LaTeX strings
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmedEquation = equation.trim();
    if (!trimmedEquation) {
      setError('Please enter an equation.');
      setResult([]);
      return;
    }

    setLoading(true);
    setError('');
    setResult([]);

    try {
      const response = await fetch(
        `${API_BASE_URL}/solve?equation=${encodeURIComponent(trimmedEquation)}`,
      );
      const data: ApiResult = await response.json();

      if (!response.ok) {
        throw new Error(data?.error || 'Request failed');
      }

      let latexList: string[] = [];

      // If backend sends an array of strings
      if (Array.isArray(data.result)) {
        latexList = data.result;
      }
      
      // If backend sends a single string but in our case it sends list of strings.
      else if (typeof data.result === 'string' && data.result.trim()) {
        const raw = data.result.trim();
        try {
          const parsed = JSON.parse(raw);
          if (Array.isArray(parsed)) {
            latexList = parsed.map(String);
          } else {
            latexList = [raw];
          }
        } catch {
          // Fallback: treat entire string as one expression
          latexList = [raw];
        }
      }

      setResult(latexList);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Request failed';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-10 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <header className="space-y-1 mb-4">
        <h1 className="text-2xl font-semibold text-slate-900 m-0">Solve equation</h1>
      </header>

      <form onSubmit={handleSubmit} className="space-y-2">
        <label className="block text-sm font-medium text-slate-900" htmlFor="equation">
          Equation
        </label>
        <div className="flex flex-col gap-3 sm:flex-row">
          <input
            id="equation"
            type="text"
            name="equation"
            placeholder="x^2 + 2x - 10"
            value={equation}
            onChange={(event) => setEquation(event.target.value)}
            aria-label="Equation"
            className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-base shadow-sm focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          />
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center justify-center rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
          >
            {loading ? 'Solving…' : 'Solve'}
          </button>
        </div>
      </form>

      <div className="mt-4 min-h-[48px] rounded-lg border border-slate-200 bg-slate-50 px-3 py-3">
        {result.length > 0 && (
          <div className="space-y-2">
            {result.map((latex, index) => {
              const safeLatex = String(latex).trim();

              return (
                <div key={index} className="text-lg font-semibold text-emerald-700">
                  <MathBlock latex={safeLatex} />
            </div>
                );
          })}
      </div>
      )}


        {error && <p className="m-0 text-sm font-semibold text-red-700">{error}</p>}

        {!result.length && !error && (
          <p className="m-0 text-sm text-slate-600">No response yet.</p>
        )}
      </div>
    </div>
  );
}

export default App;
