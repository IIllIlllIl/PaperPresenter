"""Initial deterministic planner for PaperPresenter Lite."""

from __future__ import annotations

from typing import List

from src.lite.models import DeckSpec, PaperAnalysis, PaperMetadata, SlideSpec, VisualAsset


class LitePlanner:
    """Create a reviewable initial deck plan."""

    def plan(
        self,
        metadata: PaperMetadata,
        paper_text: str,
        visuals: List[VisualAsset],
    ) -> DeckSpec:
        analysis = self._fallback_analysis(paper_text)
        visual_ids = [visual.asset_id for visual in visuals]

        slides = [
            SlideSpec(
                title=metadata.title,
                bullets=self._title_bullets(metadata),
                layout="title",
                speaker_intent="Orient the audience to the paper and venue.",
            ),
            SlideSpec(
                title="Why This Paper Matters",
                bullets=analysis.problem,
                layout="text_only",
                speaker_intent="State the motivation and gap.",
            ),
            SlideSpec(
                title="Core Idea",
                bullets=analysis.method[:3],
                layout="split" if visual_ids else "text_only",
                visual_asset_ids=visual_ids[:1],
                speaker_intent="Explain the main mechanism before details.",
            ),
            SlideSpec(
                title="Method Overview",
                bullets=analysis.method,
                layout="visual_full" if len(visual_ids) > 1 else "text_only",
                visual_asset_ids=visual_ids[1:2],
                speaker_intent="Inspect the method or system diagram.",
            ),
            SlideSpec(
                title="Experimental Setup",
                bullets=[
                    "Datasets, baselines, and metrics to verify",
                    "Look for evaluation scope and assumptions",
                    "Mark missing setup details during review",
                ],
                layout="text_only",
                speaker_intent="Prepare the audience to interpret results.",
            ),
            SlideSpec(
                title="Main Results",
                bullets=analysis.results,
                layout="split" if len(visual_ids) > 2 else "text_only",
                visual_asset_ids=visual_ids[2:3],
                speaker_intent="Surface the strongest quantitative evidence.",
            ),
            SlideSpec(
                title="Deeper Result Analysis",
                bullets=[
                    "Ablations or sensitivity tests",
                    "Qualitative cases and failure examples",
                    "Result patterns worth discussing",
                ],
                layout="split" if len(visual_ids) > 3 else "text_only",
                visual_asset_ids=visual_ids[3:4],
                speaker_intent="Move from headline result to mechanism.",
            ),
            SlideSpec(
                title="Strengths",
                bullets=analysis.strengths,
                layout="text_only",
                speaker_intent="Identify what the paper does well.",
            ),
            SlideSpec(
                title="Limitations",
                bullets=analysis.limitations,
                layout="text_only",
                speaker_intent="Support critical group discussion.",
            ),
            SlideSpec(
                title="Discussion Questions",
                bullets=analysis.discussion_questions,
                layout="text_only",
                speaker_intent="End with questions the group can debate.",
            ),
        ]

        return DeckSpec(metadata=metadata, analysis=analysis, slides=slides, visuals=visuals)

    def _title_bullets(self, metadata: PaperMetadata) -> List[str]:
        bullets = []
        if metadata.authors:
            bullets.append(", ".join(metadata.authors[:4]))
        if metadata.year:
            bullets.append(str(metadata.year))
        bullets.append(f"{metadata.page_count} pages")
        return bullets

    def _fallback_analysis(self, paper_text: str) -> PaperAnalysis:
        excerpt = " ".join(paper_text.split())[:500]
        summary = excerpt or "Text extraction returned no readable content."
        return PaperAnalysis(
            summary=summary,
            problem=[
                "What gap does the paper claim?",
                "Why existing approaches are insufficient",
                "Who benefits if the claim is true",
            ],
            method=[
                "Main technical idea to verify",
                "Key components and assumptions",
                "How the approach differs from prior work",
            ],
            results=[
                "Primary metric improvements",
                "Baselines and statistical strength",
                "Where the method wins or fails",
            ],
            strengths=[
                "Clear empirical or conceptual contribution",
                "Reusable method or benchmark insight",
                "Evidence that supports the central claim",
            ],
            limitations=[
                "Dataset or domain coverage",
                "Ablations and missing comparisons",
                "Threats to validity for deployment",
            ],
            discussion_questions=[
                "Is the central claim fully supported?",
                "What experiment would change our confidence?",
                "How could this inform our own work?",
            ],
        )

