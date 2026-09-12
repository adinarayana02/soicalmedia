from __future__ import annotations

import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from agents.analysis_agent import AnalysisAgent
from agents.data_agent import DataAgent
from agents.decision_agent import DecisionAgent
from agents.multimodal_agent import MultimodalAgent
from agents.preprocessing_agent import PreprocessingAgent


@dataclass(frozen=True)
class PipelineInput:
    text: str
    upload_bytes: Optional[bytes]
    filename: Optional[str]
    content_type: Optional[str]


data_agent = DataAgent()
pre_agent = PreprocessingAgent()
mm_agent = MultimodalAgent()
analysis_agent = AnalysisAgent()
decision_agent = DecisionAgent()


async def run_pipeline(
    *,
    text: str,
    upload_bytes: Optional[bytes],
    filename: Optional[str],
    content_type: Optional[str],
) -> Dict:
    """
    Input → Preprocess → Multimodal Conversion → XLM-R Analysis → Decision → Output
    """
    inp = PipelineInput(text=text, upload_bytes=upload_bytes, filename=filename, content_type=content_type)

    with tempfile.TemporaryDirectory(prefix="sentinel-mm-") as td:
        tmp_dir = Path(td)

        raw = await data_agent.collect(inp, tmp_dir=tmp_dir)
        cleaned_text = pre_agent.clean(raw["text"])

        unified_text = await mm_agent.to_text(
            text=cleaned_text,
            file_path=raw.get("file_path"),
            content_type=raw.get("content_type"),
        )

        predictions = analysis_agent.analyze(unified_text)
        output = decision_agent.decide(
            unified_text=unified_text,
            sentiment=predictions["sentiment"],
            emotions=predictions["emotions"],
            evidence=predictions["evidence"],
        )

        return output

