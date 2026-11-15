# CodeAlpha_FAQChatbot

**IUBAT Admission Assistant**: an FAQ chatbot built for the CodeAlpha AI internship (Task 2). It answers common questions about IUBAT admission, programs, scholarships and campus information.

## How it works
1. **Dataset** (`faqs.json`): 28 FAQ entries (146 question wordings), each with several wordings and one answer, based on public IUBAT admission information.
2. **Preprocessing** (NLTK): lowercase, tokenize, remove stopwords, Porter stemming.
3. **Matching**: TF-IDF vectors (unigrams + bigrams) and **cosine similarity** between the user's question and every stored question, implemented in plain Python.
4. **Answer**: the best match is returned if its score is above a threshold (0.3). Otherwise the bot says it doesn't know and points to the admission email.
5. **UI**: Streamlit chat interface with topic buttons, a typing effect, category labels and a sidebar with contact information.

## Run it
```bash
pip install -r requirements.txt
streamlit run app.py        # chat UI
python chatbot.py           # terminal version
```

## Files
- `chatbot.py` - preprocessing and matching engine
- `app.py` - Streamlit UI
- `faqs.json` - FAQ dataset (edit this to change the topic)
- `.streamlit/config.toml` - theme settings

## Note
Unofficial student project. Answers are taken from public IUBAT pages and may change. Always confirm at https://iubat.edu/admission.
