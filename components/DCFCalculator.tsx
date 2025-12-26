import React, { useMemo, useState } from 'react';

type DCFInputs = {
  current_fcf: number;
  growth_rate: number;
  forecast_years: number;
  terminal_growth: number;
  discount_rate: number;
  net_debt: number;
  shares_outstanding: number;
  manual_fcfs?: number[] | null;
};

type DCFRow = {
  year: number;
  fcf: number;
  discount_factor: number;
  present_value: number;
};

type DCFResult = {
  inputs: DCFInputs;
  rows: DCFRow[];
  pv_explicit: number;
  terminal_value: number;
  discounted_terminal_value: number;
  enterprise_value: number;
  equity_value: number;
  per_share_value: number;
};

function formatNumber(x: number, decimals = 2) {
  if (!Number.isFinite(x)) return '—';
  return x.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function parseManualFcfs(text: string): number[] | null {
  const raw = text.trim();
  if (!raw) return null;
  const parts = raw
    .split(/[\n,]+/g)
    .map((s) => s.trim())
    .filter(Boolean);
  if (parts.length === 0) return null;
  const nums = parts.map((p) => Number(p));
  if (nums.some((n) => !Number.isFinite(n))) return null;
  return nums;
}

const DCFCalculator: React.FC = () => {
  const [inputs, setInputs] = useState<DCFInputs>({
    current_fcf: 100,
    growth_rate: 0.15,
    forecast_years: 5,
    terminal_growth: 0.03,
    discount_rate: 0.1,
    net_debt: 0,
    shares_outstanding: 100,
    manual_fcfs: null,
  });

  const [manualFcfsText, setManualFcfsText] = useState<string>('');
  const [result, setResult] = useState<DCFResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const chartItems = useMemo(() => {
    if (!result) return [];
    const explicit = result.rows.map((r) => ({
      label: `Y${r.year}`,
      pv: r.present_value,
    }));
    const terminal = { label: 'TV', pv: result.discounted_terminal_value };
    return [...explicit, terminal];
  }, [result]);

  const maxPv = useMemo(() => {
    if (chartItems.length === 0) return 1;
    const m = Math.max(...chartItems.map((x) => Math.abs(x.pv)));
    return m > 0 ? m : 1;
  }, [chartItems]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);
    setResult(null);

    const parsedManual = parseManualFcfs(manualFcfsText);
    if (manualFcfsText.trim() && !parsedManual) {
      setIsLoading(false);
      setError('Manual FCFs could not be parsed. Use comma/newline-separated numbers.');
      return;
    }

    const payload: DCFInputs = {
      ...inputs,
      manual_fcfs: parsedManual,
    };

    try {
      const res = await fetch('/api/dcf', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const maybe = await res.json().catch(() => null);
        const detail = maybe?.detail ? String(maybe.detail) : `Request failed (${res.status})`;
        throw new Error(detail);
      }

      const data = (await res.json()) as DCFResult;
      setResult(data);
    } catch (err: any) {
      setError(err?.message || 'Failed to calculate DCF.');
    } finally {
      setIsLoading(false);
    }
  };

  const terminalRow = useMemo(() => {
    if (!result) return null;
    return {
      label: 'Terminal Value',
      terminal_value: result.terminal_value,
      present_value: result.discounted_terminal_value,
    };
  }, [result]);

  const growthVsDiscountWarning =
    inputs.discount_rate <= inputs.terminal_growth
      ? 'Discount rate must be greater than terminal growth for Gordon Growth terminal value.'
      : null;

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-200">Practical DCF Calculator</h1>
        <p className="text-sm text-gray-400 mt-2">
          Enter simple assumptions, get a clean DCF: explicit PV + Gordon Growth terminal value.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800 border border-gray-700 rounded-xl p-5">
          <h2 className="text-lg font-semibold text-white mb-4">Inputs</h2>

          <form onSubmit={onSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label className="block">
                <span className="text-sm text-gray-300">Current FCF</span>
                <input
                  type="number"
                  step="any"
                  value={inputs.current_fcf}
                  onChange={(e) => setInputs((p) => ({ ...p, current_fcf: Number(e.target.value) }))}
                  className="mt-1 w-full rounded-md bg-gray-900 border border-gray-700 px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </label>

              <label className="block">
                <span className="text-sm text-gray-300">Growth rate (explicit, decimal)</span>
                <input
                  type="number"
                  step="any"
                  value={inputs.growth_rate}
                  onChange={(e) => setInputs((p) => ({ ...p, growth_rate: Number(e.target.value) }))}
                  className="mt-1 w-full rounded-md bg-gray-900 border border-gray-700 px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </label>

              <label className="block">
                <span className="text-sm text-gray-300">Forecast years</span>
                <input
                  type="number"
                  min={1}
                  max={50}
                  step={1}
                  value={inputs.forecast_years}
                  onChange={(e) => setInputs((p) => ({ ...p, forecast_years: Number(e.target.value) }))}
                  className="mt-1 w-full rounded-md bg-gray-900 border border-gray-700 px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </label>

              <label className="block">
                <span className="text-sm text-gray-300">Terminal growth (decimal)</span>
                <input
                  type="number"
                  step="any"
                  value={inputs.terminal_growth}
                  onChange={(e) => setInputs((p) => ({ ...p, terminal_growth: Number(e.target.value) }))}
                  className="mt-1 w-full rounded-md bg-gray-900 border border-gray-700 px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </label>

              <label className="block">
                <span className="text-sm text-gray-300">Discount rate / WACC (decimal)</span>
                <input
                  type="number"
                  step="any"
                  value={inputs.discount_rate}
                  onChange={(e) => setInputs((p) => ({ ...p, discount_rate: Number(e.target.value) }))}
                  className="mt-1 w-full rounded-md bg-gray-900 border border-gray-700 px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </label>

              <label className="block">
                <span className="text-sm text-gray-300">Net debt</span>
                <input
                  type="number"
                  step="any"
                  value={inputs.net_debt}
                  onChange={(e) => setInputs((p) => ({ ...p, net_debt: Number(e.target.value) }))}
                  className="mt-1 w-full rounded-md bg-gray-900 border border-gray-700 px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </label>

              <label className="block md:col-span-2">
                <span className="text-sm text-gray-300">Shares outstanding</span>
                <input
                  type="number"
                  min={0}
                  step="any"
                  value={inputs.shares_outstanding}
                  onChange={(e) => setInputs((p) => ({ ...p, shares_outstanding: Number(e.target.value) }))}
                  className="mt-1 w-full rounded-md bg-gray-900 border border-gray-700 px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </label>
            </div>

            <div>
              <label className="block">
                <span className="text-sm text-gray-300">
                  Manual explicit FCFs (optional, comma/newline-separated)
                </span>
                <textarea
                  value={manualFcfsText}
                  onChange={(e) => setManualFcfsText(e.target.value)}
                  placeholder="Example: 120, 140, 160, 180, 200"
                  rows={3}
                  className="mt-1 w-full rounded-md bg-gray-900 border border-gray-700 px-3 py-2 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  If provided, the number of values must equal “Forecast years”.
                </p>
              </label>
            </div>

            {growthVsDiscountWarning && (
              <div className="text-sm text-yellow-300 bg-yellow-900/20 border border-yellow-800 rounded-md p-3">
                {growthVsDiscountWarning}
              </div>
            )}

            {error && (
              <div role="alert" className="text-sm text-red-300 bg-red-900/20 border border-red-800 rounded-md p-3">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2 px-4 rounded-lg bg-cyan-600 text-white hover:bg-cyan-700 disabled:bg-gray-600 disabled:opacity-50"
            >
              {isLoading ? 'Calculating…' : 'Calculate DCF'}
            </button>
          </form>
        </div>

        <div className="bg-gray-800 border border-gray-700 rounded-xl p-5">
          <h2 className="text-lg font-semibold text-white mb-4">Results</h2>

          {!result ? (
            <div className="text-gray-400 text-sm">
              Run a calculation to see enterprise value, equity value, per-share value, and the PV breakdown.
            </div>
          ) : (
            <div className="space-y-5">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                  <div className="text-xs text-gray-400">Enterprise Value</div>
                  <div className="text-xl font-bold text-white mt-1">{formatNumber(result.enterprise_value)}</div>
                </div>
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                  <div className="text-xs text-gray-400">Equity Value</div>
                  <div className="text-xl font-bold text-white mt-1">{formatNumber(result.equity_value)}</div>
                </div>
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                  <div className="text-xs text-gray-400">Per-share Value</div>
                  <div className="text-xl font-bold text-white mt-1">{formatNumber(result.per_share_value)}</div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-gray-200 mb-2">PV bar chart (explicit PVs + terminal PV)</h3>
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-4">
                  <div className="flex items-end gap-2 h-40">
                    {chartItems.map((item) => {
                      const h = Math.max(2, Math.round((Math.abs(item.pv) / maxPv) * 100));
                      const isTerminal = item.label === 'TV';
                      return (
                        <div key={item.label} className="flex-1 flex flex-col items-center gap-2">
                          <div
                            className={`w-full rounded-sm ${isTerminal ? 'bg-purple-500' : 'bg-cyan-500'}`}
                            style={{ height: `${h}%` }}
                            title={`${item.label}: ${formatNumber(item.pv)}`}
                          />
                          <div className="text-xs text-gray-400">{item.label}</div>
                        </div>
                      );
                    })}
                  </div>
                  <div className="mt-3 text-xs text-gray-500">
                    Bars are scaled by absolute present value (largest bar = 100% height).
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-sm font-semibold text-gray-200 mb-2">Cash flows & present values</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full text-sm">
                    <thead>
                      <tr className="text-left text-gray-300">
                        <th className="py-2 pr-4">Year</th>
                        <th className="py-2 pr-4">FCF</th>
                        <th className="py-2 pr-4">Discount factor</th>
                        <th className="py-2 pr-4">PV</th>
                      </tr>
                    </thead>
                    <tbody className="text-gray-200">
                      {result.rows.map((r) => (
                        <tr key={r.year} className="border-t border-gray-700">
                          <td className="py-2 pr-4">{r.year}</td>
                          <td className="py-2 pr-4">{formatNumber(r.fcf)}</td>
                          <td className="py-2 pr-4">{formatNumber(r.discount_factor, 4)}</td>
                          <td className="py-2 pr-4">{formatNumber(r.present_value)}</td>
                        </tr>
                      ))}
                      {terminalRow && (
                        <tr className="border-t border-gray-700">
                          <td className="py-2 pr-4 font-semibold text-white">TV</td>
                          <td className="py-2 pr-4">{formatNumber(terminalRow.terminal_value)}</td>
                          <td className="py-2 pr-4 text-gray-400">—</td>
                          <td className="py-2 pr-4 font-semibold text-white">
                            {formatNumber(terminalRow.present_value)}
                          </td>
                        </tr>
                      )}
                      <tr className="border-t border-gray-700">
                        <td className="py-2 pr-4 font-semibold text-white" colSpan={3}>
                          PV (explicit) + PV (terminal)
                        </td>
                        <td className="py-2 pr-4 font-semibold text-white">{formatNumber(result.enterprise_value)}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DCFCalculator;

