// Basic client-side PDF extractor using pdf.js
// Provides minimal, backend-free testing by letting users load a local PDF and extract metrics

(function(){
  const SCHEMA = [
    { standard_name: 'net_interest_income', search_terms: ['Net interest income', 'Interest income, net', 'Net interest revenue', 'Net interest earnings'], value_kind: 'amount' },
    { standard_name: 'operating_income', search_terms: ['Operating income', 'Total operating income', 'Operating profit', 'Operating profit before provisions'], value_kind: 'amount' },
    { standard_name: 'loan_impairment_expense', search_terms: ['Loan impairment expense', 'Provision for credit losses', 'Credit impairment charge', 'Loan loss provision'], value_kind: 'amount' },
    { standard_name: 'net_profit_after_tax', search_terms: ['Net profit after tax', 'Profit for the year attributable to equity holders', 'Net income', 'Profit for the year'], value_kind: 'amount' },
    { standard_name: 'total_assets', search_terms: ['Total assets', 'Assets, total'], value_kind: 'amount' },
    { standard_name: 'total_liabilities', search_terms: ['Total liabilities', 'Liabilities, total'], value_kind: 'amount' },
    { standard_name: 'net_cash_from_operating', search_terms: ['Net cash from operating activities', 'Net cash provided by operating activities'], value_kind: 'amount' },
  ];

  function normalizeLabel(text){
    return (text || '').toLowerCase().normalize('NFKD').replace(/[^a-z0-9%\-\s]/g,' ').replace(/\s+/g,' ').trim();
  }

  function detectUnitsNearby(text){
    const t = (text||'').toLowerCase();
    if (/(thousands|000s)/.test(t)) return 'thousands';
    if (/(million|\$m|aud m|in millions)/.test(t)) return 'millions';
    if (/(billion|\$bn|aud bn|in billions)/.test(t)) return 'billions';
    if (/%/.test(t)) return '%';
    return null;
  }

  function detectCurrencyNearby(text){
    const t = (text||'').toLowerCase();
    if (/aud|a\$/.test(t)) return 'AUD';
    if (/cad|c\$/.test(t)) return 'CAD';
    if (/usd|us\$|\$/.test(t)) return 'USD';
    if (/eur|€/.test(t)) return 'EUR';
    if (/gbp|£/.test(t)) return 'GBP';
    if (/jpy|¥/.test(t)) return 'JPY';
    if (/cny|rmb/.test(t)) return 'CNY';
    if (/sgd/.test(t)) return 'SGD';
    return null;
  }

  function normalizeByUnits(value, units){
    if (value == null || isNaN(value)) return value;
    if (!units) return value;
    if (units === 'thousands') return value * 1_000;
    if (units === 'millions') return value * 1_000_000;
    if (units === 'billions') return value * 1_000_000_000;
    return value;
  }

  function cleanNumberString(s){
    if (!s) return null;
    let t = s.trim().replace(/,/g,'').replace(/\u2212/g,'-');
    if (/^\(.*\)$/.test(t)) t = '-' + t.slice(1,-1);
    t = t.replace(/[$%]/g,'');
    const v = parseFloat(t);
    return isNaN(v) ? null : v;
  }

  function scoreConfidence({ matchedTerm, exactTermMatch, units, currency, numbersOnLine, pageNeighborhoodText }){
    let score = 0;
    if (exactTermMatch) score += 0.45; else if (matchedTerm) score += 0.3;
    if (units) score += 0.2;
    if (currency) score += 0.1;
    if (numbersOnLine === 1) score += 0.15; else if (numbersOnLine === 2) score += 0.05;
    const t = (pageNeighborhoodText || '').toLowerCase();
    if (/income statement|statement of profit|balance sheet|statement of financial position|cash flow/.test(t)) score += 0.1;
    if (score > 1) score = 1;
    return Math.max(0, score);
  }

  async function extractFromPdf(file){
    const pdfjsLib = window.pdfjsLib;
    if (!pdfjsLib) throw new Error('pdf.js not loaded');

    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({data: arrayBuffer}).promise;

    const results = [];
    const found = new Set();

    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++){
      const page = await pdf.getPage(pageNum);
      const content = await page.getTextContent();
      const strings = content.items.map(it => (it.str||''));
      const pageText = strings.join('\n');

      for (const metric of SCHEMA){
        if (found.has(metric.standard_name)) continue;
        for (const term of metric.search_terms){
          const re = new RegExp(`\\b${term.replace(/[-/\\^$*+?.()|[\]{}]/g,'\\$&')}\\b`, 'i');
          const match = pageText.match(re);
          if (!match) continue;

          // very simple: take the line where match occurs
          const lines = pageText.split(/\n+/);
          let line = null;
          for (const ln of lines){ if (re.test(ln)) { line = ln; break; } }
          if (!line) continue;

          // extract first number on that line
          const numbers = line.match(/\(?[\$\d,]+\)?\.?\d*%?/g) || [];
          const valStr = numbers.find(n => /\d/.test(n));
          if (!valStr) continue;

          const valueFloat = cleanNumberString(valStr);
          if (valueFloat == null) continue;

          // search a small neighborhood (previous line + current line + next) for units/currency hints
          const idx = lines.indexOf(line);
          const prev = lines[idx-1]||'';
          const next = lines[idx+1]||'';
          const nearby = [prev, line, next].join(' ');
          const units = detectUnitsNearby(nearby);
          const currency = detectCurrencyNearby(nearby);
          const normalized = normalizeByUnits(valueFloat, units);
          const confidence = scoreConfidence({
            matchedTerm: term,
            exactTermMatch: new RegExp(`^\s*${term.replace(/[-/\\^$*+?.()|[\]{}]/g,'\\$&')}\s*$`, 'i').test(line),
            units,
            currency,
            numbersOnLine: numbers.length,
            pageNeighborhoodText: nearby
          });
          const flags = [];
          if (!units) flags.push('units_missing');
          if (!currency) flags.push('currency_missing');
          if (numbers.length > 1) flags.push('multiple_numbers_on_line');

          results.push({
            metric_name: metric.standard_name,
            value: normalized,
            raw_value: valStr,
            value_units: units,
            value_currency: currency,
            value_kind: metric.value_kind || 'amount',
            source_page: pageNum,
            source_term_used: term,
            context_prev_line: prev,
            context_line: line,
            context_next_line: next,
            confidence,
            flags,
          });
          found.add(metric.standard_name);
          break;
        }
      }
    }

    return results;
  }

  // Expose minimal API to window for script.js to use
  window.ClientSideExtractor = { extractFromPdf };
})();


