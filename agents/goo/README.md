# Goo — Google Intelligence Agent

CLU's dedicated Google specialist. One-stop shop for everything in the Google ecosystem.

## Invoke

```bash
# Direct CLI
claude --agent goo "what's new in Gemini API this week?"
claude --agent goo "organize our Google Drive docs better"
claude --agent goo "set up Gemini API key and test it"

# Via Telegram
/agent goo what are the best Gemini models for coding tasks right now?
Goo, is there a free Vertex AI tier I can use?

# Via dev loop (with Goo identity on local LLM)
clu-task add --title "Summarize Gemini 2.0 capabilities" \
  --desc "..." --category reason --agent goo
```

## Capabilities

| Area | What Goo knows |
|------|---------------|
| Google Workspace | Drive, Docs, Sheets, Gmail, Calendar, Forms, Slides |
| Google AI | Gemini API, AI Studio, Vertex AI, NotebookLM |
| Google Cloud | Cloud Run, Firebase, BigQuery, Cloud Storage, Secret Manager |
| Google APIs | OAuth2, Workspace API, Search API, Maps, YouTube |
| Research | Daily digest of Google/Gemini developments |

## Idle Research

Goo runs a daily research digest at 06:00 UTC:
- Checks Google AI Blog, Gemini changelog, Workspace updates, GCP release notes
- Saves digest to `~/tools/goo-research/latest.md`
- Archives to `~/tools/goo-research/archive.md`
- Sends Telegram notification when new high-priority items are found

## Config

API keys in `~/tools/.goo-config` (chmod 600):
```
GEMINI_API_KEY="..."
GOOGLE_CLOUD_PROJECT="..."
```
