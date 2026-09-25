#!/usr/bin/env node
/**
 * wassenger-backup.js — dump every chat (and optionally every media file)
 * from a Wassenger device to local JSON + plain-text transcripts.
 *
 * Zero dependencies. Needs Node 18+ (built-in fetch).
 *
 * Usage:
 *   WASSENGER_API_KEY=xxx WASSENGER_DEVICE_ID=yyy node wassenger-backup.js [options]
 *
 *   --out <dir>       output directory (default ./wassenger-backup)
 *   --media           also download images / voice notes / documents
 *   --since <date>    only chats whose last message is on/after this date (YYYY-MM-DD)
 *   --force           re-download chats that look unchanged since last run
 *   --page-size <n>   API page size, max 100 (default 100)
 *
 * If you run it inside the wassenger-agent folder (which already has a .env
 * with the key and device id), just do:
 *   node -r dotenv/config tools/wassenger-backup.js --media
 *
 * Output layout:
 *   <out>/index.json                 one line per chat: phone, name, labels, counts
 *   <out>/chats/<phone>.json         { chat, messages[] } raw API objects
 *   <out>/chats/<phone>.txt          human-readable transcript
 *   <out>/media/<phone>/<msgId>.<ext> media files (with --media)
 *
 * Endpoints used (same ones the wassenger-agent bot uses in production):
 *   GET /chat/{device}/chats?size=&page=
 *   GET /chat/{device}/messages?chat=&size=&page=&order=asc
 *   GET /chat/{device}/files/{fileId}/download
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
const PAGE_SIZE = Math.min(100, Number(opt('--page-size', 100)) || 100);
const SINCE = opt('--since', null) ? Date.parse(opt('--since')) : null;

if (!API_KEY || !DEVICE_ID) {
  console.error('Set WASSENGER_API_KEY and WASSENGER_DEVICE_ID in the environment.');
  process.exit(1);
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
        if (attempt < backoffs.length) { await sleep(backoffs[attempt]); continue; }
        throw lastErr;
      }
      if (!res.ok) {
        const text = await res.text();
        const err = new Error(`${res.status} ${res.statusText} on ${pathname}: ${text.slice(0, 200)}`);
        err.status = res.status;
        throw err;
      }
      if (raw) return res;
      const text = await res.text();
      return text ? JSON.parse(text) : null;
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
// Normalisers (tolerant of the field-name drift Wassenger has had over time)
// ---------------------------------------------------------------------------
function chatKey(c) {
  const wid = c.wid || c.id || c.chat?.id || c.contact?.wid || '';
  const phone = (c.phone || c.contact?.phone || wid).toString().replace(/@.*$/, '').replace(/^\+/, '');
  return { wid: wid || `${phone}@c.us`, phone: phone || wid };
}

function msgTs(m) {
  const t = m.timestamp ?? m.date ?? m.createdAt ?? m.t ?? null;
  if (t == null) return null;
  if (typeof t === 'number') return t < 1e12 ? t * 1000 : t;
  const p = Date.parse(t);
  return Number.isNaN(p) ? null : p;
}

function chatLastTs(c) {
  const lm = c.lastMessage || c.last_message || c.preview || null;
  return msgTs({ timestamp: c.lastMessageAt ?? c.lastMessageTime ?? lm?.timestamp ?? lm?.date ?? c.updatedAt ?? null });
}

function msgBody(m) {
  return m.body || m.message || m.text || m.caption || '';
}

function msgFromMe(m) {
  return Boolean(m.fromMe ?? m.outbound ?? m.me ?? m.flow === 'outbound');
}

function msgMedia(m) {
  const media = m.media || m.file || m.attachment || null;
  if (!media) return null;
  const id = media.id || media.fileId || media._id || null;
  const link = media.links?.download || media.url || media.download || null;
  if (!id && !link) return null;
  const mime = media.mime || media.mimetype || media.type || null;
  return { id, link, mime, filename: media.filename || media.name || null };
}

function extFor(mime, filename) {
  if (filename && path.extname(filename)) return path.extname(filename);
  const map = {
    'image/jpeg': '.jpg', 'image/png': '.png', 'image/webp': '.webp', 'image/gif': '.gif',
    'video/mp4': '.mp4', 'audio/ogg': '.ogg', 'audio/ogg; codecs=opus': '.ogg', 'audio/mpeg': '.mp3',
    'application/pdf': '.pdf',
  };
  return map[(mime || '').toLowerCase()] || '.bin';
}

// ---------------------------------------------------------------------------
// Fetchers
// ---------------------------------------------------------------------------
async function listAllChats() {
  const out = [];
  const seen = new Set();
  for (let page = 1; ; page++) {
    const data = await api(`/chat/${DEVICE_ID}/chats`, { size: PAGE_SIZE, page, order: 'desc' });
    const list = asList(data);
    if (!list.length) break;
    let added = 0;
    for (const c of list) {
      const { wid } = chatKey(c);
      if (!wid || seen.has(wid)) continue;
      seen.add(wid);
      out.push(c);
      added++;
    }
    process.stderr.write(`\rchats: ${out.length}`);
    if (added === 0 || list.length < PAGE_SIZE) break;
    await sleep(200);
  }
  process.stderr.write('\n');
  return out;
}

async function listAllMessages(wid, phone) {
  const out = [];
  const seen = new Set();
  // Wassenger's messages endpoint has accepted `chat` as either the WID or the
  // bare phone across versions; try WID first, fall back to phone.
  const chatParams = [wid, phone];
  for (const chat of chatParams) {
    out.length = 0; seen.clear();
    let ok = false;
    for (let page = 1; ; page++) {
      let data;
      try {
        data = await api(`/chat/${DEVICE_ID}/messages`, { chat, size: PAGE_SIZE, page, order: 'asc' });
      } catch (err) {
        if (err.status === 400 || err.status === 404) break; // try next param shape
        throw err;
      }
      ok = true;
      const list = asList(data);
      if (!list.length) break;
      let added = 0;
      for (const m of list) {
        const id = m.id || m._id || m.wid || `${msgTs(m)}-${msgBody(m).slice(0, 20)}`;
        if (seen.has(id)) continue;
        seen.add(id);
        out.push(m);
        added++;
      }
      if (added === 0 || list.length < PAGE_SIZE) break;
      await sleep(200);
    }
    if (ok) break;
  }
  out.sort((a, b) => (msgTs(a) || 0) - (msgTs(b) || 0));
  return out;
}

async function downloadMedia(media, dest) {
  const target = media.id
    ? `/chat/${DEVICE_ID}/files/${encodeURIComponent(media.id)}/download`
    : null;
  let res;
  if (target) {
    res = await api(target, {}, { raw: true });
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
function transcript(chat, messages) {
  const name = chat.name || chat.contact?.name || chat.pushName || '';
  const lines = [`# ${name} (${chatKey(chat).phone})`, ''];
  for (const m of messages) {
    const ts = msgTs(m);
    const when = ts ? new Date(ts).toISOString().replace('T', ' ').slice(0, 19) : '????-??-?? ??:??:??';
    const who = msgFromMe(m) ? 'ME  ' : 'THEM';
    const media = msgMedia(m);
    const body = msgBody(m).replace(/\r?\n/g, '\n            ');
    lines.push(`${when} ${who} ${media ? `[${m.type || 'media'}${media.filename ? ' ' + media.filename : ''}] ` : ''}${body}`);
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
  const chats = await listAllChats();
  console.log(`Found ${chats.length} chats`);

  const index = [];
  let done = 0, skipped = 0, mediaFiles = 0, mediaBytes = 0, errors = 0;

  for (const chat of chats) {
    const { wid, phone } = chatKey(chat);
    const lastTs = chatLastTs(chat);
    const jsonPath = path.join(OUT_DIR, 'chats', `${phone}.json`);
    const txtPath = path.join(OUT_DIR, 'chats', `${phone}.txt`);

    if (SINCE && lastTs && lastTs < SINCE) { skipped++; continue; }

    // Resume: skip if we already have this chat and its last message hasn't moved.
    if (!FORCE && fs.existsSync(jsonPath)) {
      try {
        const prev = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
        if (prev.lastTs && lastTs && prev.lastTs === lastTs) {
          index.push(prev.summary);
          skipped++;
          continue;
        }
      } catch { /* fall through and re-download */ }
    }

    try {
      const messages = await listAllMessages(wid, phone);
      let mediaSaved = 0;
      if (WITH_MEDIA) {
        const dir = path.join(OUT_DIR, 'media', phone);
        for (const m of messages) {
          const media = msgMedia(m);
          if (!media) continue;
          fs.mkdirSync(dir, { recursive: true });
          const id = (m.id || m._id || String(msgTs(m))).replace(/[^A-Za-z0-9._-]/g, '_');
          const dest = path.join(dir, id + extFor(media.mime, media.filename));
          if (fs.existsSync(dest) && !FORCE) { mediaSaved++; continue; }
          try {
            mediaBytes += await downloadMedia(media, dest);
            mediaSaved++;
            mediaFiles++;
            await sleep(150);
          } catch (err) {
            console.warn(`  media failed for ${phone}/${id}: ${err.message}`);
          }
        }
      }

      const summary = {
        phone,
        wid,
        name: chat.name || chat.contact?.name || chat.pushName || null,
        labels: (chat.labels || chat.tags || []).map((l) => (typeof l === 'string' ? l : l?.name)).filter(Boolean),
        messages: messages.length,
        media: mediaSaved,
        firstTs: messages.length ? msgTs(messages[0]) : null,
        lastTs: messages.length ? msgTs(messages[messages.length - 1]) : lastTs,
      };
      fs.writeFileSync(jsonPath, JSON.stringify({ summary, lastTs, chat, messages }, null, 2));
      fs.writeFileSync(txtPath, transcript(chat, messages));
      index.push(summary);
      done++;
      console.log(`[${done + skipped}/${chats.length}] ${phone} ${summary.name || ''} — ${messages.length} msgs${WITH_MEDIA ? `, ${mediaSaved} media` : ''}`);
      await sleep(200);
    } catch (err) {
      errors++;
      console.error(`  FAILED ${phone}: ${err.message}`);
    }
  }

  index.sort((a, b) => (b.lastTs || 0) - (a.lastTs || 0));
  fs.writeFileSync(path.join(OUT_DIR, 'index.json'), JSON.stringify({
    device: DEVICE_ID,
    generatedAt: new Date().toISOString(),
    chats: index.length,
    messages: index.reduce((n, c) => n + c.messages, 0),
    chatsDownloaded: done,
    chatsSkipped: skipped,
    mediaFiles,
    mediaBytes,
    errors,
    index,
  }, null, 2));

  console.log(`\nDone. ${done} chats downloaded, ${skipped} skipped, ${errors} errors.`);
  console.log(`Total messages: ${index.reduce((n, c) => n + c.messages, 0)}`);
  if (WITH_MEDIA) console.log(`Media: ${mediaFiles} new files, ${(mediaBytes / 1e6).toFixed(1)} MB`);
  console.log(`Index: ${path.join(OUT_DIR, 'index.json')}`);
})().catch((err) => {
  console.error('Backup failed:', err);
  process.exit(1);
});
