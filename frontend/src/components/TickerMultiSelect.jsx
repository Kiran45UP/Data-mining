import { useState } from 'react';
import { Plus, X } from 'lucide-react';

const DEFAULT_TICKERS = ['AAPL', 'MSFT', 'GOOG', 'TSLA', 'AMZN', 'META', 'NVDA', 'NFLX', 'IBM', 'INTC'];

const TickerMultiSelect = ({
  label = 'Tickers',
  items,
  setItems,
  placeholder = 'Add ticker',
  helperText,
  options = DEFAULT_TICKERS,
  required = false,
}) => {
  const [inputValue, setInputValue] = useState('');

  const normalized = (value) => value.trim().toUpperCase();

  const addTicker = (value) => {
    const ticker = normalized(value || inputValue);
    if (!ticker) return;
    if (items.includes(ticker)) {
      setInputValue('');
      return;
    }
    setItems([...items, ticker]);
    setInputValue('');
  };

  const removeTicker = (index) => {
    setItems(items.filter((_, idx) => idx !== index));
  };

  const availableOptions = options.filter((opt) => !items.includes(opt));

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-400">{label}{required ? ' *' : ''}</label>
      <div className="grid gap-3 sm:grid-cols-[1fr_auto]">
        <div className="flex gap-2">
          <select
            value=""
            onChange={(e) => {
              if (e.target.value) {
                addTicker(e.target.value);
              }
            }}
            className="input-field w-full bg-dark-bg"
            aria-required={required}
          >
            <option value="">Select ticker from list</option>
            {availableOptions.map((option) => (
              <option key={option} value={option}>{option}</option>
            ))}
          </select>
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                e.preventDefault();
                addTicker();
              }
            }}
            placeholder={placeholder}
            className="input-field w-full"
            aria-required={required}
          />
        </div>

        <button
          type="button"
          onClick={() => addTicker()}
          className="btn-primary whitespace-nowrap flex items-center justify-center gap-2"
        >
          <Plus className="w-4 h-4" /> Add
        </button>
      </div>

      <div className="flex flex-wrap gap-2">
        {items.length === 0 && (
          <span className="text-sm text-gray-500">No tickers selected yet.</span>
        )}
        {items.map((ticker, index) => (
          <span key={ticker + index} className="inline-flex items-center gap-2 rounded-full border border-gray-700 bg-dark-surface px-3 py-1 text-sm text-gray-100">
            <span>{ticker}</span>
            <button
              type="button"
              onClick={() => removeTicker(index)}
              className="rounded-full p-1 text-gray-400 hover:text-white"
              aria-label={`Remove ${ticker}`}
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </span>
        ))}
      </div>

      {helperText && <p className="text-xs text-gray-500">{helperText}</p>}
    </div>
  );
};

export default TickerMultiSelect;
