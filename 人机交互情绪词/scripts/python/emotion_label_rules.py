"""Curated normalization and grouping rules for article-level emotion labels.

The source files contain both discrete emotion labels and broader affective
dimensions or design descriptors.  These rules keep the latter out of the
emotion counts while collapsing obvious part-of-speech variants. Analysis
groups are applied after normalization and counted once per article.
"""

from __future__ import annotations

from typing import Dict, Optional, Set, Tuple


# These labels describe dimensions, absences of emotion, measurement targets,
# behaviors, or non-emotional design properties rather than a discrete emotion.
REMOVE_LABELS: Set[str] = {
    "activation",
    "active",
    "affect",
    "affective state",
    "alert",
    "arousal",
    "aroused",
    "attention",
    "attentive",
    "attentiveness",
    "challenging",
    "challenge",
    "classic",
    "comprehensible",
    "concentration",
    "control",
    "dominance",
    "easy",
    "easy to read",
    "effective",
    "emotional",
    "engagement",
    "engagement/flow",
    "flow",
    "formal",
    "frowning",
    "high arousal",
    "high valence",
    "learning emotions",
    "learnable",
    "low arousal",
    "low valence",
    "mechanical",
    "modern",
    "mood",
    "natural",
    "negative",
    "negative activation",
    "negative affect",
    "negative emotion",
    "negative emotions",
    "negative psychology",
    "negative valence",
    "neutral",
    "neutral mood",
    "no emotion (neutral)",
    "non-confusion",
    "positive",
    "positive activation",
    "positive affect",
    "positive emotion",
    "positive emotions",
    "positive valence",
    "power",
    "productive",
    "realistic",
    "rhythmic",
    "serious",
    "simple",
    "simplicity",
    "sleepy",
    "sophistication",
    "strong",
    "symmetry",
    "time consuming",
    "trustworthiness",
    "uniform",
    "unpleasant",
    "unexpected",
    "user friendly",
    "valence",
    "well-being",
    "wide awake",
    "weakly negative",
    "weakly positive",
    "attractiveness",
    "attractive",
    "crying",
    "competent",
    "convinced",
    "dependable",
    "depression",
    "determined",
    "elegance",
    "elegant",
    "humorous",
    "joking",
    "monotonous",
    "motivated",
    "passive",
    "reliable",
    "smiling",
    "quiet",
    "confession",
    "convenience",
    "energetic",
    "engaged",
    "exhausting",
    "harmonious",
    "harmony",
    "preoccupied",
    "pressure",
    "soothing",
    "thinking",
    "trustable",
    "unfriendly",
    "warm",
}


# The values are canonical labels and short audit explanations.  Most entries
# are adjective-to-noun conversions; a few collapse an obvious synonym or a
# compound label whose underlying emotion is unambiguous.
MAP_LABELS: Dict[str, Tuple[str, str]] = {
    "agitated": ("agitation", "adjective variant of agitation"),
    "amiable": ("amiability", "adjective variant of amiability"),
    "afraid": ("fear", "adjective variant of fear"),
    "angry": ("anger", "adjective variant of anger"),
    "anxious": ("anxiety", "adjective variant of anxiety"),
    "annoying": ("annoyance", "adjective variant of annoyance"),
    "amused": ("amusement", "adjective variant of amusement"),
    "bored": ("boredom", "adjective variant of boredom"),
    "boring": ("boredom", "adjective variant of boredom"),
    "boisterous": ("boisterousness", "adjective variant of boisterousness"),
    "calm": ("calmness", "adjective variant of calmness"),
    "cheerful": ("cheerfulness", "adjective variant of cheerfulness"),
    "comfortable": ("comfort", "adjective variant of comfort"),
    "content": ("contentment", "adjective variant of contentment"),
    "contented": ("contentment", "adjective variant of contentment"),
    "contemptuous": ("contempt", "adjective variant of contempt"),
    "curious": ("curiosity", "adjective variant of curiosity"),
    "disappointed": ("disappointment", "adjective variant of disappointment"),
    "disgusted": ("disgust", "adjective variant of disgust"),
    "disgusting": ("disgust", "adjective variant of disgust"),
    "distressed": ("distress", "adjective variant of distress"),
    "excited": ("excitement", "adjective variant of excitement"),
    "exciting": ("excitement", "adjective variant of excitement"),
    "fear-confirmed": ("fear", "fear-qualified label collapsed to fear"),
    "fright": ("fear", "near-synonym of fear"),
    "frustrated": ("frustration", "adjective variant of frustration"),
    "glad": ("joy", "adjective variant of joy"),
    "giggly": ("amusement", "adjective variant of amusement"),
    "gloomy": ("sadness", "adjective variant of sadness"),
    "grateful": ("gratitude", "adjective variant of gratitude"),
    "grumpy": ("irritation", "adjective variant of irritation"),
    "guilty": ("guilt", "adjective variant of guilt"),
    "happy": ("happiness", "adjective variant of happiness"),
    "hopeful": ("hope", "adjective variant of hope"),
    "hostile": ("hostility", "adjective variant of hostility"),
    "interesting": ("interest", "adjective variant of interest"),
    "interested": ("interest", "adjective variant of interest"),
    "irritable": ("irritation", "adjective variant of irritation"),
    "inspired": ("inspiration", "adjective variant of inspiration"),
    "irritating": ("irritation", "adjective variant of irritation"),
    "joyful": ("joy", "adjective variant of joy"),
    "joyful activation": ("joy", "joy label with activation descriptor"),
    "jubilant": ("joy", "adjective variant of joy"),
    "miserable": ("sadness", "adjective variant of sadness"),
    "lethargic": ("lethargy", "adjective variant of lethargy"),
    "nervous": ("nervousness", "adjective variant of nervousness"),
    "nervousness": ("nervousness", "canonical label"),
    "optimistic": ("optimism", "adjective variant of optimism"),
    "passionate": ("passion", "adjective variant of passion"),
    "peaceful": ("calmness", "near-synonym of calmness"),
    "pleasant": ("pleasure", "adjective variant of pleasure"),
    "pleasantness": ("pleasure", "noun variant of pleasure"),
    "pleasant surprise": ("surprise", "surprise with valence qualifier"),
    "painful": ("pain", "adjective variant of pain"),
    "pleased": ("pleasure", "adjective variant of pleasure"),
    "puzzled": ("confusion", "adjective variant of confusion"),
    "puzzlement": ("confusion", "near-synonym of confusion"),
    "proud": ("pride", "adjective variant of pride"),
    "relaxed": ("relaxation", "adjective variant of relaxation"),
    "rebellious": ("rebelliousness", "adjective variant of rebelliousness"),
    "sad": ("sadness", "adjective variant of sadness"),
    "satisfied": ("satisfaction", "adjective variant of satisfaction"),
    "self-assurance": ("confidence", "near-synonym of confidence"),
    "shy": ("shyness", "adjective variant of shyness"),
    "sorrow/sadness/grief": ("sadness", "slash-separated sadness synonyms"),
    "stressed": ("stress", "adjective variant of stress"),
    "sentimental": ("sentimentality", "adjective variant of sentimentality"),
    "stressful": ("stress", "adjective variant of stress"),
    "surprised": ("surprise", "adjective variant of surprise"),
    "thrilled": ("excitement", "adjective variant of excitement"),
    "vigorous": ("vigor", "adjective variant of vigor"),
    "uncomfortable": ("discomfort", "adjective variant of discomfort"),
    "unhappiness": ("sadness", "near-synonym of sadness"),
    "unpleasant surprise": ("surprise", "surprise with valence qualifier"),
    "upset": ("distress", "near-synonym of distress"),
    "ashamed": ("shame", "adjective variant of shame"),
    "anticipatory": ("anticipation", "adjective variant of anticipation"),
    "astonished": ("surprise", "adjective variant of surprise"),
    "confident": ("confidence", "adjective variant of confidence"),
    "delighted": ("delight", "adjective variant of delight"),
    "dislike": ("dislike", "canonical noun form"),
    "dreamy": ("dreaminess", "adjective variant of dreaminess"),
    "ebullient": ("joy", "positive emotion adjective"),
    "elated": ("elation", "adjective variant of elation"),
    "enthusiastic": ("enthusiasm", "adjective variant of enthusiasm"),
    "fearful": ("fear", "adjective variant of fear"),
    "joy/pleasure": ("joy", "slash-separated joy label"),
    "joviality": ("joy", "near-synonym of joy"),
    "jittery": ("nervousness", "near-synonym of nervousness"),
    "like": ("liking", "noun form of like"),
    "computer anxiety": ("anxiety", "anxiety with context qualifier"),
    "state anxiety": ("anxiety", "anxiety with context qualifier"),
    "productive confusion": ("confusion", "confusion with productivity qualifier"),
    "platonic love": ("love", "love with relationship qualifier"),
    "romantic love": ("love", "love with relationship qualifier"),
    "unproductive confusion": ("confusion", "confusion with productivity qualifier"),
    "lively": ("liveliness", "adjective variant of liveliness"),
    "sorrow": ("sadness", "near-synonym of sadness"),
    "tension": ("tension", "canonical noun form"),
    "relaxation": ("relaxation", "canonical noun form"),
    "calmness": ("calmness", "canonical noun form"),
}


# Analysis-level grouping decisions apply to canonical labels, including all
# raw variants that normalize to them. Happiness is the shared analysis label.
GROUP_LABELS: Dict[str, Tuple[str, str]] = {
    "joy": ("happiness", "joy grouped with happiness for analysis"),
}


REMOVE_REASONS: Dict[str, str] = {
    "valence": "affective dimension rather than a discrete emotion",
    "arousal": "affective dimension rather than a discrete emotion",
    "activation": "affective dimension rather than a discrete emotion",
    "dominance": "affective dimension rather than a discrete emotion",
    "control": "affective dimension rather than a discrete emotion",
    "power": "affective dimension rather than a discrete emotion",
    "mood": "broad affective construct rather than a discrete emotion",
    "affect": "broad affective construct rather than a discrete emotion",
    "affective state": "broad affective construct rather than a discrete emotion",
    "neutral": "absence or baseline state rather than an emotion",
    "positive": "broad valence category rather than a discrete emotion",
    "negative": "broad valence category rather than a discrete emotion",
    "positive emotion": "broad valence category rather than a discrete emotion",
    "positive emotions": "broad valence category rather than a discrete emotion",
    "negative emotion": "broad valence category rather than a discrete emotion",
    "negative emotions": "broad valence category rather than a discrete emotion",
    "positive affect": "broad valence category rather than a discrete emotion",
    "negative affect": "broad valence category rather than a discrete emotion",
    "positive valence": "affective dimension rather than a discrete emotion",
    "negative valence": "affective dimension rather than a discrete emotion",
    "high valence": "affective dimension rather than a discrete emotion",
    "low valence": "affective dimension rather than a discrete emotion",
    "high arousal": "affective dimension rather than a discrete emotion",
    "low arousal": "affective dimension rather than a discrete emotion",
    "positive activation": "affective dimension rather than a discrete emotion",
    "negative activation": "affective dimension rather than a discrete emotion",
    "weakly positive": "broad valence category rather than a discrete emotion",
    "weakly negative": "broad valence category rather than a discrete emotion",
    "no emotion (neutral)": "absence or baseline state rather than an emotion",
    "neutral mood": "absence or baseline state rather than an emotion",
    "non-confusion": "absence of an emotion or state rather than an emotion",
    "learning emotions": "umbrella category rather than a discrete emotion",
    "engagement/flow": "engagement or experiential state rather than an emotion",
    "flow": "experiential state rather than a discrete emotion",
    "well-being": "broad wellbeing construct rather than a discrete emotion",
    "smiling": "observable behavior rather than an emotion",
    "crying": "observable behavior rather than an emotion",
    "frowning": "observable behavior rather than an emotion",
    "depression": "clinical mood condition rather than an emotion label",
    "attractiveness": "design or stimulus property rather than an emotion",
    "convenience": "design or usability property rather than an emotion",
    "trustworthiness": "stimulus or person property rather than an emotion",
}


def clean_label(label: str) -> str:
    """Return a stable lower-case representation for rule lookup."""
    import re
    import unicodedata

    text = unicodedata.normalize("NFKC", label)
    text = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-")
    text = re.sub(r"\s+", " ", text.strip().lower())
    return text


def normalize_label(label: str) -> Tuple[Optional[str], str, str]:
    """Return ``(canonical_label, action, reason)`` for one raw label."""
    key = clean_label(label)
    if not key:
        return None, "remove", "empty label"
    if key in REMOVE_LABELS:
        return None, "remove", REMOVE_REASONS.get(key, "not a discrete emotion")
    if key in MAP_LABELS:
        canonical, reason = MAP_LABELS[key]
        action = "map"
    else:
        canonical, action = key, "keep"
        reason = "kept as supplied; no clear non-emotion rule matched"
    if canonical in GROUP_LABELS:
        canonical, group_reason = GROUP_LABELS[canonical]
        reason = f"{reason}; {group_reason}" if action == "map" else group_reason
        action = "map"
    return canonical, action, reason
