import json
import re
from dataclasses import dataclass, asdict
from typing import Any, Dict

from .logger import log
from .utils import get_llm


@dataclass
class QualityReport:
    personalization_score: int
    grounding_score: int
    tone_score: int
    length_score: int
    overall_score: int
    flagged_reasons: list[str]
    judge_notes: str
    needs_human_review: bool


def _normalize_score(score: int) -> int:
    return max(0, min(10, score))


def _rule_personalization(text: str, context: Dict[str, Any]) -> int:
    text_lower = text.lower()
    matches = 0
    for field in ("lead_name", "industry", "key_decision_maker", "position"):
        value = context.get(field)
        if value and value.lower() in text_lower:
            matches += 1
    if matches >= 3:
        return 10
    if matches == 2:
        return 8
    if matches == 1:
        return 6
    return 3


def _rule_grounding(text: str) -> int:
    weak_phrases = [
        "i think",
        "i believe",
        "maybe",
        "probably",
        "as far as i know",
        "likely",
        "might",
    ]
    count = sum(1 for phrase in weak_phrases if phrase in text.lower())
    if count == 0:
        return 9
    if count == 1:
        return 7
    return 4


def _rule_tone(text: str) -> int:
    negative_indicators = ["urgent", "closing", "buy now", "limited time"]
    positive_indicators = ["thank you", "appreciate", "look forward", "best regards", "respectfully"]
    score = 6
    if any(indicator in text.lower() for indicator in negative_indicators):
        score -= 2
    if any(indicator in text.lower() for indicator in positive_indicators):
        score += 2
    return _normalize_score(score)


def _rule_length(text: str) -> int:
    word_count = len(re.findall(r"\w+", text))
    if 100 <= word_count <= 220:
        return 10
    if 80 <= word_count < 100 or 221 <= word_count <= 260:
        return 8
    if 60 <= word_count < 80 or 261 <= word_count <= 300:
        return 6
    return 4


def _parse_judge_response(response: str) -> Dict[str, int]:
    scores: dict[str, int] = {}
    for metric in ["personalization", "grounding", "tone", "length"]:
        pattern = re.compile(rf"{metric}\s*[:=\-]\s*(\d{{1,2}})", re.IGNORECASE)
        match = pattern.search(response)
        if match:
            scores[f"{metric}_score"] = _normalize_score(int(match.group(1)))
    return scores


def _llm_judge(text: str, context: Dict[str, Any]) -> tuple[dict[str, int], str]:
    llm = get_llm()
    prompt = (
        "You are a quality reviewer for buyer outreach email copy. "
        "Review the email below and score it from 0 to 10 on each of these dimensions: "
        "personalization specificity, factual grounding, tone appropriateness, and length. "
        "Only use the information from the context and avoid making new claims. "
        "Return the result as a simple text block with each metric followed by its numeric score and a short note.\n\n"
        f"Context:\nlead_name: {context.get('lead_name', '')}\n"
        f"industry: {context.get('industry', '')}\n"
        f"key_decision_maker: {context.get('key_decision_maker', '')}\n"
        f"position: {context.get('position', '')}\n\n"
        f"Email:\n{text}\n"
    )
    try:
        response = llm(prompt)
        if hasattr(response, "content"):
            response_text = str(response.content)
        else:
            response_text = str(response)
    except Exception as exc:
        log("email_quality_llm_error", error=str(exc))
        return {}, "LLM judge failed"

    return _parse_judge_response(response_text), response_text


def evaluate_email_quality(email_text: str, context: Dict[str, Any]) -> dict[str, Any]:
    rule_scores = {
        "personalization_score": _rule_personalization(email_text, context),
        "grounding_score": _rule_grounding(email_text),
        "tone_score": _rule_tone(email_text),
        "length_score": _rule_length(email_text),
    }
    llm_scores, judge_notes = _llm_judge(email_text, context)

    combined_scores: dict[str, int] = {}
    for key, rule_value in rule_scores.items():
        llm_value = llm_scores.get(key, rule_value)
        combined_scores[key] = int(round((rule_value + llm_value) / 2))

    overall_score = int(round(sum(combined_scores.values()) / len(combined_scores)))
    flagged_reasons: list[str] = []
    if combined_scores["personalization_score"] < 6:
        flagged_reasons.append("Low personalization specificity")
    if combined_scores["grounding_score"] < 6:
        flagged_reasons.append("Questionable factual grounding")
    if combined_scores["tone_score"] < 6:
        flagged_reasons.append("Tone may be inappropriate")
    if combined_scores["length_score"] < 6:
        flagged_reasons.append("Email length is outside the recommended range")
    if overall_score < 7:
        flagged_reasons.append("Overall quality below threshold")

    needs_human_review = overall_score < 7 or len(flagged_reasons) > 0
    report = QualityReport(
        personalization_score=combined_scores["personalization_score"],
        grounding_score=combined_scores["grounding_score"],
        tone_score=combined_scores["tone_score"],
        length_score=combined_scores["length_score"],
        overall_score=int(round(overall_score * 10)),
        flagged_reasons=flagged_reasons,
        judge_notes=judge_notes,
        needs_human_review=needs_human_review,
    )
    log("email_quality_report_generated", **asdict(report))
    return asdict(report)
