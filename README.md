# youtube-to-knowledge

Turn any YouTube video into a transcript, summary, and knowledge graph — powered by Claude Code.

Paste a link. Get structured knowledge.

## How it works

1. Fetches the transcript (WhisperX for speaker-labelled segments, with automatic fallback to Whisper then YouTube API)
2. Generates a structured summary in the video's language
3. Extracts entities and relationships → builds an interactive knowledge graph

## Requirements

- Python 3.10+
- [Claude Code](https://claude.ai/code)
- ffmpeg (required for Whisper mode)

### Install ffmpeg

| OS | Command |
|----|---------|
| macOS | `brew install ffmpeg` |
| Ubuntu / Debian | `sudo apt install ffmpeg` |
| Fedora | `sudo dnf install ffmpeg` |
| Windows | `winget install ffmpeg` |

## Setup

```bash
git clone https://github.com/velmighty/youtube-to-knowledge
cd youtube-to-knowledge
pip install -r requirements.txt
pip install -r requirements-whisperx.txt   # recommended — enables speaker tagging
```

Open the folder in Claude Code.

### Speaker diarization (optional but recommended)

WhisperX can label who is speaking in each segment. This requires a free HuggingFace account and two model approvals.

**1. Accept the pyannote model licences** (one-time, takes ~30 seconds each):

- https://huggingface.co/pyannote/speaker-diarization-3.1
- https://huggingface.co/pyannote/segmentation-3.0

Click **Agree and access repository** on each page while signed in to your HuggingFace account.

**2. Create an access token** at https://huggingface.co/settings/tokens — a read-only token is sufficient.

**3. Set the environment variable:**

```bash
# For the current terminal session only
export HF_TOKEN=hf_your_token_here

# To make it permanent, add the line above to your shell profile:
echo 'export HF_TOKEN=hf_your_token_here' >> ~/.zshrc   # zsh (macOS default)
echo 'export HF_TOKEN=hf_your_token_here' >> ~/.bashrc  # bash
```

Once `HF_TOKEN` is set, speaker labels appear automatically in the enriched transcript:

```
[00:00:05 - 00:00:12] [SPEAKER_00]
So the first thing we need to understand...

[00:00:13 - 00:00:20] [SPEAKER_01]
Right, and that connects to what you said earlier...
```

Without `HF_TOKEN`, WhisperX still runs and produces timestamps — just without speaker labels.

## Usage

```
/process https://www.youtube.com/watch?v=VIDEO_ID
```

Process multiple videos at once:

```
/process https://youtube.com/watch?v=abc https://youtube.com/watch?v=def
```

Process an entire playlist:

```
/process https://www.youtube.com/playlist?list=PLxxx
```

Already-processed videos are skipped automatically.

Additional commands:

- `/video_specialist` — deep-dive questions about what was said in a processed video
- `/kg_navigator` — explore entity connections across videos

## Output

Files are saved to `vault/content/<channel_name>/`:

```
raw/
  transcript_<video_id>.txt    raw transcript
  metadata_<video_id>.json     title, channel, video ID, language
summary_<video_id>.md          structured summary
triplets_<video_id>.json       knowledge graph source data (per video)
graph.json                     cumulative graph in node-link format
graph.html                     open in browser — interactive visualization
```

Each file is named after the video ID, so multiple videos from the same channel are stored without overwriting each other.

## Transcription modes

`/process` always tries the highest-quality mode first and falls back automatically:

| Priority | Mode | Output | Requirement |
|----------|------|--------|-------------|
| 1st | **WhisperX** | Timestamps + speaker labels | `requirements-whisperx.txt` + `HF_TOKEN` for speaker labels |
| 2nd | **Whisper** | Plain transcript | Included in `requirements.txt` |
| 3rd | **Fast** | Plain transcript | Video must have subtitles |

To skip WhisperX and Whisper and go straight to the YouTube subtitle API (fastest, no local processing):

```
/process --engine fast https://www.youtube.com/watch?v=VIDEO_ID
```

## Obsidian integration

Add `--obsidian` to export the knowledge graph directly into your Obsidian vault.

```
/process --obsidian https://www.youtube.com/watch?v=VIDEO_ID
```

This generates one `.md` file per extracted entity in `vault/content/<channel_name>/obsidian/`. Each file contains:

- **YAML frontmatter** — tags, source title, URL, channel
- **Relations** — outgoing links to other entities: `- made_by: [[Anthropic]]`
- **Referenced by** — incoming links: `- [[Claude]] → made_by`

Wikilinks use Obsidian's `[[filename|display]]` aliasing, so they resolve correctly even when entity names contain special characters.

To connect the exported notes to your main vault, point Obsidian at the `vault/` folder or copy the `obsidian/` directory into your existing vault.

You can also run the exporter directly:

```bash
python src/obsidian_exporter.py vault/content/<channel>/triplets_<video_id>.json /path/to/output \
  --metadata vault/content/<channel>/raw/metadata_<video_id>.json
```

## Options

```
/process [--depth light|standard|deep] [--engine fast] [--obsidian] <URL> [<URL2> ...]
```

| Flag | Values | Default | Effect |
|------|--------|---------|--------|
| `--depth` | `light`, `standard`, `deep` | `deep` | Controls triplet count and summary detail |
| `--engine` | `fast` | — | Skip WhisperX/Whisper; use YouTube subtitle API only |
| `--obsidian` | — | off | Exports entity notes to `obsidian/` subfolder |

Defaults are read from `config.yaml` — edit that file to change them without touching the commands.

Flags apply to all videos in a batch.

Examples:

```
/process https://www.youtube.com/watch?v=VIDEO_ID
/process https://youtube.com/watch?v=abc https://youtube.com/watch?v=def
/process https://www.youtube.com/playlist?list=PLxxx
/process --depth light https://www.youtube.com/watch?v=VIDEO_ID
/process --engine fast https://www.youtube.com/watch?v=VIDEO_ID
/process --obsidian https://www.youtube.com/watch?v=VIDEO_ID
/process --obsidian --depth deep https://www.youtube.com/watch?v=VIDEO_ID
```

## License

[MIT](LICENSE)
