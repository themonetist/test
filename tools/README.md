# Wassenger backup tools

Two scripts that turn a Wassenger device into an offline archive plus an Excel
lead list. Both are zero-config beyond the two Wassenger credentials.

| File | What it does |
|---|---|
| `wassenger-backup.js` | Downloads every chat, every message and (with `--media`) every still-available media file. Writes JSON, plain-text transcripts, `index.json` and `contacts.csv`. |
| `build-leads-xlsx.py` | Turns a backup folder into `Leads.xlsx`: a Summary sheet, one row per number with the full conversation, and one row per message. |

## Run it on the bot server (recommended)

The `wassenger-agent` folder on the Hetzner box already has a `.env` with
`WASSENGER_API_KEY` and `WASSENGER_DEVICE_ID`, and Node 18+ installed.

```bash
cd /opt/wassenger-agent
git clone --depth 1 -b claude/new-session-5rax6i https://github.com/themonetist/test.git /tmp/tools
node -r dotenv/config /tmp/tools/tools/wassenger-backup.js --out /opt/backups/wassenger --media
pip3 install openpyxl
python3 /tmp/tools/tools/build-leads-xlsx.py /opt/backups/wassenger /opt/backups/wassenger/Mandaya-WhatsApp-Leads.xlsx
```

Then copy `/opt/backups/wassenger` somewhere permanent (Drive, OneDrive, a
laptop). Re-running is safe: chats are rewritten, media already on disk is
skipped.

Anywhere else, export the two variables first:

```bash
export WASSENGER_API_KEY=...      # app.wassenger.com -> Developers -> API keys
export WASSENGER_DEVICE_ID=...    # app.wassenger.com -> Devices
node tools/wassenger-backup.js --out ./wassenger-backup --media
```

On Node 22+ behind an HTTPS proxy add `NODE_USE_ENV_PROXY=1`.

## Options

```
--out <dir>      output directory (default ./wassenger-backup)
--media          also download images / voice notes / documents
--only <phones>  comma-separated numbers (digits, no +) instead of every chat
--force          re-download media files that already exist
--debug          log every API response status/shape to stderr
```

## Output

```
<out>/index.json                  totals + one summary entry per chat
<out>/contacts.csv                one row per number: name, labels, counts,
                                  first/last message, last text, wa.me link
<out>/chats/<phone>.json          raw chat metadata + every raw message object
<out>/chats/<phone>.txt           readable transcript (UTC timestamps)
<out>/media/<phone>/<msgId>.<ext> media files
```

## Wassenger API facts the script depends on

Verified against the live API in September 2026.

- `GET /chat/{device}/messages?size=50&page=N` with no `chat` filter walks the
  whole device message stream. Grouping by `message.chat.id` is the only
  source that is guaranteed complete; the chats list silently omitted active
  chats in testing.
- `page` is zero-indexed. `size` is capped at 50.
- Passing `order` breaks the `chat` filter, so it is never sent.
- The `chat` filter wants the bare phone (`6281234567`), not `...@c.us`.
- Some list views ignore `page` and return the same records forever; the
  script stops when a page adds nothing new.
- Media files expire on Wassenger's side after a while. An expired file
  answers `503` on every attempt. The script fails fast and counts them in
  `index.json` under `mediaErrors`. Those files still exist in the WhatsApp
  app on the phone itself; Wassenger is only a layer on top of that account.

## After cancelling Wassenger

Cancelling Wassenger does not delete anything from WhatsApp. The chats, media
and contacts stay in the WhatsApp app on the phone that was linked. To message
a lead later, open the `whatsapp_link` column in `contacts.csv` (a `wa.me`
link) or search the number in WhatsApp. For automated outreach, the official
WhatsApp Cloud API lets the business write first using approved templates.
