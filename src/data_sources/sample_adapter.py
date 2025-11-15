from typing import List, Dict
from .base import BaseAdapter


SAMPLE_BLOCK = """Title: Market sentiment discussion
Content: Investors show mixed reactions; some anticipate growth while others fear correction.
Comment: Outlook seems Positive for tech sector.
Comment: Financials might be Neutral given rate trajectory.
Comment: Some bearish views on overvalued momentum stocks.
"""


class SampleAdapter(BaseAdapter):
    source_name = "sample"

    def fetch(self, keywords: List[str], tickers: List[str], limit: int = 10) -> List[Dict]:
        records = []
        segments = [s.strip() for s in SAMPLE_BLOCK.split('\n') if s.strip()]
        for seg in segments[:limit]:
            rec_tickers = self._filter_tickers(seg, tickers)
            records.append({
                'source': self.source_name,
                'timestamp': self._now_iso(),
                'text': seg,
                'tickers': rec_tickers
            })
        return records
