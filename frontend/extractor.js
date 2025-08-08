// Basic client-side PDF extractor using pdf.js
// Provides minimal, backend-free testing by letting users load a local PDF and extract metrics

(function(){
  const SCHEMA = [
    { standard_name: 'net_interest_income', search_terms: ['Net interest income', 'Interest income, net'], value_kind: 'amount' },
    { standard_name: 'operating_income', search_terms: ['Operating income', 'Total operating income'], value_kind: 'amount' },
    { standard_name: 'loan_impairment_expense', search_terms: ['Loan impairment expense', 'Provision for credit losses'], value_kind: 'amount' },
    { standard_name: 'net_profit_after_tax', search_terms: ['Net profit after tax', 'Profit for the year attributable to equity holders'], value_kind: 'amount' },
    { standard_name: 'total_assets', search_terms: ['Total assets'], value_kind: 'amount' },
    { standard_name: 'total_liabilities', search_terms: ['Total liabilities'], value_kind: 'amount' },
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

          // search a small neighborhood (previous line + current line) for units/currency hints
          const idx = lines.indexOf(line);
          const nearby = [lines[idx-1]||'', line, lines[idx+1]||''].join(' ');
          const units = detectUnitsNearby(nearby);
          const currency = detectCurrencyNearby(nearby);
          const normalized = normalizeByUnits(valueFloat, units);

          results.push({
            metric_name: metric.standard_name,
            value: normalized,
            raw_value: valStr,
            value_units: units,
            value_currency: currency,
            value_kind: metric.value_kind || 'amount',
            source_page: pageNum,
            source_term_used: term,
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


