"""FAQ chatbot engine: NLTK preprocessing + TF-IDF + cosine similarity.

TF-IDF and cosine similarity are implemented in plain Python (no scikit-learn
or scipy), so the project installs and runs anywhere.
"""
import json
import math
from collections import Counter
from pathlib import Path

from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer

FAQ_PATH = Path(__file__).with_name("faqs.json")

FALLBACK = (
    "Sorry, I couldn't find an answer to that. Try rephrasing, or email the "
    "admission office at admissions@iubat.edu."
)

# Small built-in stopword list, so the bot works without downloading NLTK corpora.
STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "am", "be", "been", "do", "does",
    "did", "i", "me", "my", "we", "you", "your", "it", "its", "of", "to", "in",
    "on", "at", "for", "with", "and", "or", "can", "could", "would", "should",
    "will", "shall", "please", "tell", "about", "there", "this", "that", "these",
    "those", "any", "have", "has", "had", "get", "so", "if", "as", "by", "from",
}

QUESTION_WORDS = {"what", "who", "where", "when", "which", "why", "how"}

_tokenizer = RegexpTokenizer(r"[a-z0-9]+")
_stemmer = PorterStemmer()
_QUESTION_STEMS = {_stemmer.stem(w) for w in QUESTION_WORDS}


def preprocess(text: str) -> str:
    """Lowercase, tokenize, remove stopwords and single letters, then stem."""
    tokens = _tokenizer.tokenize(text.lower())
    tokens = [t for t in tokens if t not in STOPWORDS and (len(t) > 1 or t.isdigit())]
    return " ".join(_stemmer.stem(t) for t in tokens)


def _terms(cleaned: str) -> list:
    """Unigrams + bigrams of the cleaned text."""
    words = cleaned.split()
    return words + [f"{a} {b}" for a, b in zip(words, words[1:])]


def _normalize(vec: dict) -> dict:
    length = math.sqrt(sum(v * v for v in vec.values()))
    return {t: v / length for t, v in vec.items()} if length else {}


class FAQChatbot:
    def __init__(self, faq_path=FAQ_PATH, threshold: float = 0.3):
        with open(faq_path, encoding="utf-8") as f:
            self.entries = json.load(f)
        self.threshold = threshold

        self.questions = []   # every question variant (original text)
        self.owner = []       # index of the FAQ entry each variant belongs to
        for idx, entry in enumerate(self.entries):
            for q in entry["questions"]:
                self.questions.append(q)
                self.owner.append(idx)

        # Term counts for every stored question.
        counts = [Counter(_terms(preprocess(q))) for q in self.questions]

        # IDF: rare terms get a higher weight.
        n_docs = len(counts)
        doc_freq = Counter(term for c in counts for term in c)
        self.idf = {t: math.log((1 + n_docs) / (1 + df)) + 1 for t, df in doc_freq.items()}

        # TF-IDF vector (unit length) for every stored question.
        self.vectors = [
            _normalize({t: tf * self.idf[t] for t, tf in c.items()}) for c in counts
        ]
        self.vocab = {t for t in self.idf if " " not in t}

    def _vectorize(self, cleaned: str) -> dict:
        counts = Counter(t for t in _terms(cleaned) if t in self.idf)
        return _normalize({t: tf * self.idf[t] for t, tf in counts.items()})

    @staticmethod
    def _cosine(a: dict, b: dict) -> float:
        """Cosine similarity of two unit-length vectors = their dot product."""
        if len(a) > len(b):
            a, b = b, a
        return sum(v * b.get(t, 0.0) for t, v in a.items())

    def get_response(self, user_text: str) -> dict:
        """Return the best FAQ answer for the user's text."""
        cleaned = preprocess(user_text)
        if not cleaned:
            return {"answer": FALLBACK, "score": 0.0, "matched": None, "found": False, "category": None}

        # Guard: a question made only of question words plus unknown words
        # ("what's the weather") must not match on the question word alone.
        content = [t for t in cleaned.split() if t not in _QUESTION_STEMS]
        if content:
            known = sum(t in self.vocab for t in content)
            if known / len(content) < 0.5:
                return {"answer": FALLBACK, "score": 0.0, "matched": None, "found": False, "category": None}

        query = self._vectorize(cleaned)
        scores = [self._cosine(query, v) for v in self.vectors]
        best = max(range(len(scores)), key=scores.__getitem__)
        score = scores[best]

        if score < self.threshold:
            return {"answer": FALLBACK, "score": score, "matched": None, "found": False, "category": None}
        entry = self.entries[self.owner[best]]
        return {
            "answer": entry["answer"],
            "score": score,
            "matched": self.questions[best],
            "found": True,
            "category": entry.get("category"),
        }


if __name__ == "__main__":
    bot = FAQChatbot()
    print("IUBAT FAQ bot (type 'quit' to exit)")
    while True:
        text = input("You: ").strip()
        if text.lower() in {"quit", "exit"}:
            break
        print("Bot:", bot.get_response(text)["answer"])
