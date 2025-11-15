from typing import List, Dict
from datetime import datetime


class BaseAdapter:
    """Base class for data source adapters.

    Subclasses override `fetch` to return a list of records:
        [{'source': str, 'timestamp': str, 'text': str, 'tickers': List[str]}]
    """

    source_name: str = "base"

    def fetch(self, keywords: List[str], tickers: List[str], limit: int = 50) -> List[Dict]:  # pragma: no cover
        return []

    @staticmethod
    def _now_iso() -> str:
        return datetime.utcnow().isoformat() + 'Z'

    @staticmethod
    def _filter_tickers(text: str, tickers: List[str]) -> List[str]:
        found = []
        upper_text = text.upper()
        for t in tickers:
            u = t.upper()
            if f' ${u} ' in upper_text or f' {u} ' in upper_text or upper_text.startswith(u + ' ') or upper_text.endswith(' ' + u):
                found.append(t)
            elif u in upper_text and len(u) >= 3 and upper_text.count(u) < 10:
                found.append(t)
        return list(dict.fromkeys(found))  # preserve order
