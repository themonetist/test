#!/usr/bin/env node
/**
 * wassenger-backup.js — dump every chat (and optionally every media file)
 * from a Wassenger device to local JSON + plain-text transcripts.
 *
 * Zero dependencies. Needs Node 18+ (built-in fetch). On Node 22+ behind an
 * HTTPS proxy, run with NODE_USE_ENV_PROXY=1.
 *
 * Usage:
 *   WASSENGER_API_KEY=xxx WASSENGER_DEVICE_ID=yyy node wassenger-backup.js [options]
 *
 *   --out <dir>       output directory (default ./wassenger-backup)
 *   --media           also download images / voice notes / documents
 *   --only <phones>   comma-separated phone numbers (digits, no +) to back up
 *                     instead of every chat; handy for testing one contact
 *   --force           re-download media files that already exist
 *   --debug           log every API response status/shape to stderr
 *
 * If you run it inside the wassenger-agent folder (which already has a .env
 * with the key and device id), just do:
 *   node -r dotenv/config tools/wassenger-backup.js --media
 *
 * Output layout:
 *   <out>/index.json                 summary + one entry per chat
 *   <out>/chats/<phone>.json         { summary, chat, messages[] } raw API objects
 *   <out>/chats/<phone>.txt          human-readable transcript
 *   <out>/media/<phone>/<msgId>.<ext> media files (with --media)
 *
 * Strategy (verified against the live API, Sep 2026):
 *   - GET /chat/{device}/messages?size=50&page=N with NO chat filter walks the
 *     whole device message stream. Grouping by message.chat.id is the only
 *     source that is guaranteed complete: the chats list endpoint paginates
 *     inconsistently and silently omitted active chats in testing.
 *   - GET /chat/{device}/chats (default and archived=true) supplies names and
 *     labels; anything still missing is fetched with GET /chat/{device}/chats/{wid}.
 *   - GET /chat/{device}/files/{fileId}/download fetches media bytes.
 *   - `size` is capped at 50 by the API and `page` is ZERO-indexed. The `order`
 *     query param breaks the chat filter, so it is never sent; ordering is done
 *     locally.
 */

'use strict';

const fs = require('fs');
const path = require('path');

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------
const API_BASE = (process.env.WASSENGER_API_BASE || 'https://api.wassenger.com/v1').replace(/\/+$/, '');
const API_KEY = process.env.WASSENGER_API_KEY || '';
const DEVICE_ID = process.env.WASSENGER_DEVICE_ID || '';

const args = process.argv.slice(2);
function flag(name) { return args.includes(name); }
function opt(name, def) {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : def;
}

const OUT_DIR = path.resolve(opt('--out', './wassenger-backup'));
const WITH_MEDIA = flag('--media');
const FORCE = flag('--force');
const DEBUG = flag('--debug');
const ONLY = (opt('--only', '') || '').split(',').map((s) => s.replace(/[^\d]/g, '')).filter(Boolean);
const PAGE_SIZE = 50; // API maximum

if (!API_KEY || !DEVICE_ID) {
  console.error('Set WASSENGER_API_KEY and WASSENGER_DEVICE_ID in the environment.');
  process.exit(1);
}

function dbg(...parts) {
  if (DEBUG) console.error('[debug]', ...parts);
}

// ---------------------------------------------------------------------------
// HTTP helper with retry/backoff (429 + 5xx)
// ---------------------------------------------------------------------------
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function api(pathname, query = {}, { raw = false } = {}) {
  const url = new URL(API_BASE + pathname);
  for (const [k, v] of Object.entries(query)) {
    if (v !== undefined && v !== null) url.searchParams.set(k, String(v));
  }
  const backoffs = [2000, 5000, 10000, 20000];
  let lastErr;
  for (let attempt = 0; attempt <= backoffs.length; attempt++) {
    try {
      const res = await fetch(url, { headers: { Authorization: API_KEY } });
      if (res.status === 429 || res.status >= 500) {
        lastErr = new Error(`${res.status} ${res.statusText} on ${pathname}`);
        dbg(res.status, pathname, url.search, 'retrying');
        if (attempt < backoffs.length) { await sleep(backoffs[attempt]); continue; }
        throw lastErr;
      }
      if (!res.ok) {
        const text = await res.text();
        dbg(res.status, pathname, url.search, '->', text.slice(0, 300));
        const err = new Error(`${res.status} ${res.statusText} on ${pathname}: ${text.slice(0, 200)}`);
        err.status = res.status;
        throw err;
      }
      if (raw) return res;
      const text = await res.text();
      const parsed = text ? JSON.parse(text) : null;
      if (DEBUG) {
        const shape = Array.isArray(parsed)
          ? `array(${parsed.length})`
          : parsed && typeof parsed === 'object' ? `object keys=${Object.keys(parsed).slice(0, 12).join(',')}` : typeof parsed;
        dbg(res.status, pathname, url.search, '->', shape);
      }
      return parsed;
    } catch (err) {
      if (err.status && err.status < 500 && err.status !== 429) throw err;
      lastErr = err;
      if (attempt < backoffs.length) await sleep(backoffs[attempt]);
    }
  }
  throw lastErr;
}

function asList(data) {
  if (Array.isArray(data)) return data;
  return data?.data || data?.items || data?.chats || data?.messages || [];
}

// ---------------------------------------------------------------------------
// Normalisers
// ---------------------------------------------------------------------------
function phoneOf(wid) {
  return String(wid || '').replace(/@.*$/, '').replace(/^\+/, '');
}

function msgChatId(m) {
  return m.chat?.id || m.chat?.wid || (typeof m.chat === 'string' ? m.chat : null)
    || (m.flow === 'outbound' ? m.to : m.from) || null;
}

function msgTs(m) {
  const t = m.date ?? m.timestamp ?? m.createdAt ?? null;
  if (t == null) return null;
  if (typeof t === 'number') return t < 1e12 ? t * 1000 : t;
  const p = Date.parse(t);
  return Number.isNaN(p) ? null : p;
}

function msgBody(m) {
  return m.body || m.message || m.text || m.media?.caption || '';
}

function msgFromMe(m) {
  if (m.flow) return m.flow === 'outbound';
  return Boolean(m.fromMe ?? m.outbound ?? m.me);
}

function msgMedia(m) {
  const media = m.media || null;
  if (!media || !(media.id || media.links?.download)) return null;
  return {
    id: media.id || null,
    link: media.links?.download || null,
    mime: media.mime || null,
    ext: media.extension ? `.${media.extension.replace(/^\./, '')}` : null,
    filename: media.filename || null,
    size: media.size || null,
    expiresAt: media.expiresAt || null,
  };
}

function extFor(media) {
  if (media.ext) return media.ext;
  if (media.filename && path.extname(media.filename)) return path.extname(media.filename);
  const map = {
    'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp', 'image/gif': '.gif',
    'video/mp4': '.mp4', 'audio/ogg': '.ogg', 'audio/mpeg': '.mp3', 'application/pdf': '.pdf',
  };
  return map[(media.mime || '').toLowerCase().split(';')[0]] || '.bin';
}

function chatName(c) {
  return c?.contact?.name || c?.contact?.displayName || c?.name || null;
}

function chatLabels(c) {
  return (c?.labels || []).map((l) => (typeof l === 'string' ? l : l?.name)).filter(Boolean);
}

// ---------------------------------------------------------------------------
// Fetchers
// ---------------------------------------------------------------------------

/** Walk the entire device message stream (or one chat's) and return all messages. */
async function walkMessages(filter = {}) {
  const out = [];
  const seen = new Set();
  let stalePages = 0;
  for (let page = 0; ; page++) { // pages are zero-indexed
    let list;
    try {
      list = asList(await api(`/chat/${DEVICE_ID}/messages`, { size: PAGE_SIZE, page, ...filter }));
    } catch (err) {
      if (err.status === 400 && page > 0) break; // page beyond the API's range
      throw err;
    }
    if (!list.length) break;
    let added = 0;
    for (const m of list) {
      const id = m.id || m.wid || `${msgTs(m)}-${msgChatId(m)}-${msgBody(m).slice(0, 20)}`;
      if (seen.has(id)) continue;
      seen.add(id);
      out.push(m);
      added++;
    }
    if (!filter.chat) process.stderr.write(`\rmessages: ${out.length} (page ${page})`);
    if (added === 0) { if (++stalePages >= 2) break; } else stalePages = 0;
    if (list.length < PAGE_SIZE) break;
    await sleep(150);
  }
  if (!filter.chat) process.stderr.write('\n');
  return out;
}

/** Pull chat metadata (names, labels, status) from both list views. */
async function fetchChatMetadata() {
  const byWid = new Map();
  for (const extra of [{}, { archived: true }]) {
    for (let page = 0; ; page++) { // pages are zero-indexed
      let list;
      try {
        list = asList(await api(`/chat/${DEVICE_ID}/chats`, { size: PAGE_SIZE, page, ...extra }));
      } catch (err) {
        if (err.status === 400 && page > 0) break;
        throw err;
      }
      if (!list.length) break;
      let added = 0;
      for (const c of list) {
        const wid = c.id || c.wid || c.contact?.wid;
        if (!wid) continue;
        // Prefer the @c.us record over the @lid alias for the same contact.
        const existing = byWid.get(wid);
        if (!existing || (wid.endsWith('@c.us') && !existing.id?.endsWith('@c.us'))) byWid.set(wid, c);
        added++;
      }
      process.stderr.write(`\rchat metadata: ${byWid.size}`);
      if (added === 0 || list.length < PAGE_SIZE) break;
      await sleep(150);
    }
  }
  process.stderr.write('\n');
  return byWid;
}

async function fetchOneChat(wid) {
  try {
    return await api(`/chat/${DEVICE_ID}/chats/${encodeURIComponent(wid)}`);
  } catch (err) {
    if (err.status === 404) return null;
    throw err;
  }
}

async function downloadMedia(media, dest) {
  let res;
  if (media.id) {
    res = await api(`/chat/${DEVICE_ID}/files/${encodeURIComponent(media.id)}/download`, {}, { raw: true });
  } else {
    const abs = /^https?:/i.test(media.link) ? media.link : new URL(API_BASE).origin + media.link;
    res = await fetch(abs, { headers: { Authorization: API_KEY } });
    if (!res.ok) throw new Error(`media ${res.status} ${abs}`);
  }
  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(dest, buf);
  return buf.length;
}

// ---------------------------------------------------------------------------
// Writers
// ---------------------------------------------------------------------------
function transcript(name, phone, messages, mediaPaths) {
  const lines = [`# ${name || '(no name)'} (+${phone})`, ''];
  for (const m of messages) {
    const ts = msgTs(m);
    const when = ts ? new Date(ts).toISOString().replace('T', ' ').slice(0, 19) : '????-??-?? ??:??:??';
    const who = msgFromMe(m) ? 'ME  ' : 'THEM';
    const media = msgMedia(m);
    const saved = mediaPaths.get(m.id);
    const tag = media
      ? `[${m.type || 'media'}${media.filename ? ' ' + media.filename : ''}${saved ? ' -> ' + saved : ''}] `
      : (m.type && m.type !== 'text' && m.type !== 'chat' ? `[${m.type}] ` : '');
    const body = msgBody(m).replace(/\r?\n/g, '\n                          ');
    lines.push(`${when} ${who} ${tag}${body}`);
  }
  return lines.join('\n') + '\n';
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
(async () => {
  fs.mkdirSync(path.join(OUT_DIR, 'chats'), { recursive: true });
  if (WITH_MEDIA) fs.mkdirSync(path.join(OUT_DIR, 'media'), { recursive: true });

  console.log(`Backing up device ${DEVICE_ID} to ${OUT_DIR}${WITH_MEDIA ? ' (with media)' : ''}`);

  // 1. Messages, grouped by chat.
  const byChat = new Map(); // wid -> messages[]
  if (ONLY.length) {
    console.log(`Targeted run for ${ONLY.length} chat(s): ${ONLY.join(', ')}`);
    for (const phone of ONLY) {
      const msgs = await walkMessages({ chat: phone });
      byChat.set(`${phone}@c.us`, msgs);
    }
  } else {
    const all = await walkMessages();
    for (const m of all) {
      const wid = msgChatId(m);
      if (!wid) continue;
      if (!byChat.has(wid)) byChat.set(wid, []);
      byChat.get(wid).push(m);
    }
    console.log(`Fetched ${all.length} messages across ${byChat.size} chats`);
  }

  // 2. Chat metadata.
  const meta = ONLY.length ? new Map() : await fetchChatMetadata();
  let metaFetched = 0;
  for (const wid of byChat.keys()) {
    if (!meta.has(wid)) {
      const c = await fetchOneChat(wid);
      if (c) { meta.set(wid, c); metaFetched++; }
      await sleep(100);
    }
  }
  if (metaFetched) console.log(`Fetched metadata individually for ${metaFetched} chats missing from the list`);

  // 3. Write each chat.
  const index = [];
  let done = 0, mediaFiles = 0, mediaBytes = 0, mediaErrors = 0;
  const ordered = [...byChat.entries()].sort((a, b) => {
    const la = a[1].length ? msgTs(a[1][a[1].length - 1]) || 0 : 0;
    const lb = b[1].length ? msgTs(b[1][b[1].length - 1]) || 0 : 0;
    return lb - la;
  });

  for (const [wid, messages] of ordered) {
    messages.sort((a, b) => (msgTs(a) || 0) - (msgTs(b) || 0));
    const chat = meta.get(wid) || null;
    const phone = phoneOf(chat?.contact?.phone || wid);
    const safe = phone.replace(/[^A-Za-z0-9._-]/g, '_') || wid.replace(/[^A-Za-z0-9._-]/g, '_');
    const name = chatName(chat);
    const mediaPaths = new Map();
    let mediaSaved = 0;

    if (WITH_MEDIA) {
      const dir = path.join(OUT_DIR, 'media', safe);
      for (const m of messages) {
        const media = msgMedia(m);
        if (!media) continue;
        fs.mkdirSync(dir, { recursive: true });
        const id = String(m.id || msgTs(m)).replace(/[^A-Za-z0-9._-]/g, '_');
        const file = id + extFor(media);
        const dest = path.join(dir, file);
        const rel = path.posix.join('media', safe, file);
        if (fs.existsSync(dest) && !FORCE) { mediaPaths.set(m.id, rel); mediaSaved++; continue; }
        try {
          mediaBytes += await downloadMedia(media, dest);
          mediaPaths.set(m.id, rel);
          mediaSaved++;
          mediaFiles++;
          await sleep(100);
        } catch (err) {
          mediaErrors++;
          console.warn(`  media failed for +${phone} msg ${id}: ${err.message}`);
        }
      }
    }

    const last = messages[messages.length - 1] || null;
    const summary = {
      phone,
      wid,
      name,
      labels: chatLabels(chat),
      status: chat?.status || null,
      messages: messages.length,
      inbound: messages.filter((m) => !msgFromMe(m)).length,
      outbound: messages.filter(msgFromMe).length,
      media: messages.filter(msgMedia).length,
      mediaSaved,
      firstAt: messages.length ? new Date(msgTs(messages[0])).toISOString() : null,
      lastAt: last ? new Date(msgTs(last)).toISOString() : null,
      lastFrom: last ? (msgFromMe(last) ? 'me' : 'them') : null,
      lastBody: last ? msgBody(last).slice(0, 200) : null,
      file: `chats/${safe}.json`,
    };
    fs.writeFileSync(path.join(OUT_DIR, 'chats', `${safe}.json`), JSON.stringify({ summary, chat, messages }, null, 2));
    fs.writeFileSync(path.join(OUT_DIR, 'chats', `${safe}.txt`), transcript(name, phone, messages, mediaPaths));
    index.push(summary);
    done++;
    if (ONLY.length || done % 25 === 0) {
      console.log(`[${done}/${ordered.length}] +${phone} ${name || ''} — ${messages.length} msgs${WITH_MEDIA ? `, ${mediaSaved}/${summary.media} media` : ''}`);
    }
  }

  const totalMessages = index.reduce((n, c) => n + c.messages, 0);
  fs.writeFileSync(path.join(OUT_DIR, 'index.json'), JSON.stringify({
    device: DEVICE_ID,
    generatedAt: new Date().toISOString(),
    chats: index.length,
    messages: totalMessages,
    mediaMessages: index.reduce((n, c) => n + c.media, 0),
    mediaFilesSaved: index.reduce((n, c) => n + c.mediaSaved, 0),
    mediaFilesNew: mediaFiles,
    mediaBytesNew: mediaBytes,
    mediaErrors,
    index,
  }, null, 2));

  console.log(`\nDone. ${done} chats, ${totalMessages} messages.`);
  if (WITH_MEDIA) console.log(`Media: ${mediaFiles} new files, ${(mediaBytes / 1e6).toFixed(1)} MB, ${mediaErrors} failed`);
  console.log(`Index: ${path.join(OUT_DIR, 'index.json')}`);
})().catch((err) => {
  console.error('Backup failed:', err);
  process.exit(1);
});
