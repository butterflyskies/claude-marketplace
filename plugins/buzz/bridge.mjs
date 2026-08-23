#!/usr/bin/env node
/**
 * buzz-bridge — standalone MCP server that subscribes to a Buzz relay
 * via Nostr WebSocket and emits notifications/claude/channel for each
 * matching event. Configured as a Claude Code plugin alongside Dione.
 *
 * Env:
 *   BUZZ_PRIVATE_KEY  — Nostr private key (hex)
 *   BUZZ_RELAY_URL    — wss:// relay URL
 *   BUZZ_CHANNELS     — comma-separated channel UUIDs to watch (optional; default: all)
 *   BUZZ_CURSOR_FILE  — path to persist last-seen event timestamp
 *
 * Protocol: MCP over stdio (JSON-RPC 2.0).
 * Delivery: at-least-once with recognizable duplicates (Nostr event ID dedup).
 */

import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const WebSocket = require('ws');
const { getPublicKey, finalizeEvent } = require('nostr-tools/pure');
const { bytesToHex, hexToBytes } = require('nostr-tools/utils');
import { createInterface } from 'readline';
import { readFileSync, writeFileSync, existsSync } from 'fs';
import { createHash, randomBytes } from 'crypto';

// ── Config ──────────────────────────────────────────────────────────
// Load identity from file if env vars not set
const IDENTITY_FILE = process.env.BUZZ_IDENTITY_FILE || `${process.env.HOME}/.config/buzz/identity`;
if (!process.env.BUZZ_PRIVATE_KEY && existsSync(IDENTITY_FILE)) {
  const lines = readFileSync(IDENTITY_FILE, 'utf8').split('\n');
  for (const line of lines) {
    const m = line.match(/^(\w+)=(.+)$/);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2];
  }
}
const PRIVATE_KEY = process.env.BUZZ_PRIVATE_KEY;
const RELAY_URL = process.env.BUZZ_RELAY_URL || 'ws://localhost:3000';
const CHANNELS = process.env.BUZZ_CHANNELS ? process.env.BUZZ_CHANNELS.split(',') : [];
const CURSOR_FILE = process.env.BUZZ_CURSOR_FILE || '/workspace/taliesin/.buzz-bridge-cursor';
const SEEN_WINDOW = 1000; // track last N event IDs for dedup

if (!PRIVATE_KEY) {
  process.stderr.write(JSON.stringify({ error: 'config', message: 'BUZZ_PRIVATE_KEY required' }) + '\n');
  process.exit(1);
}

// ── State ───────────────────────────────────────────────────────────
let mcpReady = false;
const seenIds = new Set();
let lastTimestamp = 0;

// Load cursor
if (existsSync(CURSOR_FILE)) {
  try {
    const data = JSON.parse(readFileSync(CURSOR_FILE, 'utf8'));
    lastTimestamp = data.timestamp || 0;
    if (data.seen) data.seen.forEach(id => seenIds.add(id));
  } catch { /* start fresh */ }
}

function saveCursor() {
  const data = {
    timestamp: lastTimestamp,
    seen: Array.from(seenIds).slice(-SEEN_WINDOW),
  };
  try { writeFileSync(CURSOR_FILE, JSON.stringify(data)); } catch { /* best effort */ }
}

// ── Stdio JSON-RPC ──────────────────────────────────────────────────
function send(obj) {
  process.stdout.write(JSON.stringify(obj) + '\n');
}

function sendNotification(method, params) {
  send({ jsonrpc: '2.0', method, params });
}

function sendResult(id, result) {
  send({ jsonrpc: '2.0', id, result });
}

// ── MCP initialization ─────────────────────────────────────────────
const rl = createInterface({ input: process.stdin, terminal: false });
rl.on('line', (line) => {
  let msg;
  try { msg = JSON.parse(line); } catch { return; }

  if (msg.method === 'initialize') {
    log('MCP initialize received');
    sendResult(msg.id, {
      protocolVersion: '2025-03-26',
      capabilities: { experimental: { 'claude/channel': {} }, notifications: {} },
      serverInfo: { name: 'buzz-bridge', version: '0.1.0' },
    });
  } else if (msg.method === 'notifications/initialized') {
    log('MCP notifications/initialized received — connecting to relay');
    mcpReady = true;
    connectRelay();
  } else if (msg.method === 'tools/list') {
    // No tools — outbound goes through buzz-cli
    sendResult(msg.id, { tools: [] });
  } else if (msg.method === 'resources/list') {
    sendResult(msg.id, { resources: [] });
  } else if (msg.method === 'prompts/list') {
    sendResult(msg.id, { prompts: [] });
  } else if (msg.id !== undefined) {
    // Unknown request — return empty
    sendResult(msg.id, {});
  }
});

rl.on('close', () => {
  saveCursor();
  process.exit(0);
});

// ── Nostr helpers ───────────────────────────────────────────────────
// Minimal secp256k1 signing would go here. For the probe, we use
// the buzz-cli for auth and subscribe with a basic REQ filter.
// Full NIP-42 auth requires secp256k1 signing which we'll add if needed.

function makeSubFilter() {
  // Subscribe to kind 9 (channel messages) that p-tag our pubkey
  const pubkey = derivePublicKey(PRIVATE_KEY);
  const filter = { kinds: [9], '#p': [pubkey], since: lastTimestamp || undefined };
  // Also subscribe to all messages in configured channels
  const filters = [filter];
  if (CHANNELS.length > 0) {
    filters.push({ kinds: [9], '#h': CHANNELS, since: lastTimestamp || undefined });
  }
  return filters;
}

function derivePublicKey(privKeyHex) {
  const sk = hexToBytes(privKeyHex);
  const pk = getPublicKey(sk);
  // getPublicKey may return hex string or Uint8Array depending on version
  return typeof pk === 'string' ? pk : bytesToHex(pk);
}

// ── Relay connection ────────────────────────────────────────────────
let ws = null;
let reconnectTimer = null;
let authenticated = false;
let subscribed = false;
let pendingAuthEventId = null;

function subscribe() {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;
  const filters = makeSubFilter();
  filters.forEach((f, i) => {
    ws.send(JSON.stringify(['REQ', `buzz-bridge-${i}`, f]));
  });
  subscribed = true;
  log(`subscriptions sent (${filters.length} filters, since=${lastTimestamp || 'none'})`);
}

function connectRelay() {
  // Normalize: https→wss, http→ws, wss/ws stay as-is
  let url = RELAY_URL;
  if (url.startsWith('https://')) url = 'wss://' + url.slice(8);
  else if (url.startsWith('http://')) url = 'ws://' + url.slice(7);
  log(`connecting to ${url}`);

  authenticated = false;
  subscribed = false;
  pendingAuthEventId = null;
  ws = new WebSocket(url);

  ws.on('open', () => {
    log('connected — waiting for AUTH challenge');
    // Don't subscribe yet — relay may require NIP-42 auth first.
    // If no AUTH arrives within 3s AND we haven't started auth, subscribe without auth.
    // If we're mid-auth (pendingAuthEventId set), keep waiting for the OK.
    setTimeout(() => {
      if (!authenticated && !subscribed && !pendingAuthEventId) {
        log('no AUTH challenge received — subscribing without auth');
        subscribe();
      }
    }, 3000);
    // Safety net: if auth was attempted but OK never came, reconnect after 10s.
    setTimeout(() => {
      if (pendingAuthEventId && !authenticated && !subscribed) {
        log('auth OK never received after 10s — reconnecting');
        ws.close();
      }
    }, 10000);

    // Client-initiated pings every 30s to detect dead connections.
    // If no pong within 10s, close and let the reconnect handler fire.
    let lastPong = Date.now();
    const pingInterval = setInterval(() => {
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        clearInterval(pingInterval);
        return;
      }
      if (Date.now() - lastPong > 40000) {
        log('no pong received in 40s — connection dead, reconnecting');
        clearInterval(pingInterval);
        ws.terminate();
        return;
      }
      ws.ping();
    }, 30000);
    ws.on('pong', () => { lastPong = Date.now(); });
    ws.on('close', () => clearInterval(pingInterval));
  });

  ws.on('message', (data) => {
    let msg;
    try { msg = JSON.parse(data.toString()); } catch { return; }

    if (!Array.isArray(msg)) return;

    if (msg[0] === 'EVENT') {
      handleEvent(msg[2]);
    } else if (msg[0] === 'EOSE') {
      log(`subscription ${msg[1]} caught up`);
    } else if (msg[0] === 'AUTH') {
      handleAuth(msg[1]);
    } else if (msg[0] === 'OK') {
      // AUTH response confirmation
      const [, eventId, success, message] = msg;
      if (eventId === pendingAuthEventId) {
        if (success) {
          log(`auth accepted — subscribing`);
          authenticated = true;
          subscribe();
        } else {
          log(`auth rejected: ${message}`);
        }
      }
    } else if (msg[0] === 'CLOSED') {
      const [, subId, reason] = msg;
      log(`subscription ${subId} closed: ${reason || 'no reason'}`);
      // If closed due to auth requirement, don't panic — AUTH handler will re-subscribe
      if (reason && reason.includes('auth-required')) {
        subscribed = false;
      }
    } else if (msg[0] === 'NOTICE') {
      log(`relay notice: ${msg[1]}`);
    }
  });

  ws.on('close', () => {
    log('disconnected — reconnecting in 5s');
    saveCursor();
    authenticated = false;
    subscribed = false;
    reconnectTimer = setTimeout(connectRelay, 5000);
  });

  ws.on('error', (err) => {
    log(`ws error: ${err.message}`);
  });
}

function handleAuth(challenge) {
  log(`auth challenge: ${challenge}`);
  try {
    const sk = hexToBytes(PRIVATE_KEY);
    let relayUrl = RELAY_URL;
    if (relayUrl.startsWith('https://')) relayUrl = 'wss://' + relayUrl.slice(8);
    else if (relayUrl.startsWith('http://')) relayUrl = 'ws://' + relayUrl.slice(7);
    const authEvent = finalizeEvent({
      kind: 22242,
      created_at: Math.floor(Date.now() / 1000),
      tags: [
        ['relay', relayUrl],
        ['challenge', challenge],
      ],
      content: '',
    }, sk);
    pendingAuthEventId = authEvent.id;
    ws.send(JSON.stringify(['AUTH', authEvent]));
    log('auth response sent — waiting for OK');
    // Don't subscribe here — wait for the OK response in the message handler
  } catch (err) {
    log(`auth failed: ${err.message}`);
  }
}

function handleEvent(event) {
  if (!event || !event.id) return;

  // Dedup
  if (seenIds.has(event.id)) return;
  seenIds.add(event.id);
  if (seenIds.size > SEEN_WINDOW * 2) {
    // Trim
    const arr = Array.from(seenIds);
    arr.slice(0, arr.length - SEEN_WINDOW).forEach(id => seenIds.delete(id));
  }

  // Update cursor
  if (event.created_at > lastTimestamp) {
    lastTimestamp = event.created_at;
  }

  // Extract channel UUID from h-tag
  const hTag = (event.tags || []).find(t => t[0] === 'h');
  const channelId = hTag ? hTag[1] : 'unknown';

  // Extract mentioned pubkeys
  const pTags = (event.tags || []).filter(t => t[0] === 'p').map(t => t[1]);

  // Build notification
  if (mcpReady) {
    const meta = {
      chat_id: `buzz:${channelId}`,
      message_id: event.id,
      user: event.pubkey.substring(0, 12) + '…',
      user_id: event.pubkey,
      ts: new Date(event.created_at * 1000).toISOString(),
      source: 'buzz',
      relay: RELAY_URL,
    };

    const notif = { content: event.content || '', meta };
    log(`sending MCP notification for event ${event.id.substring(0, 8)}… content="${(event.content || '').substring(0, 60)}"`);
    sendNotification('notifications/claude/channel', notif);
    log(`delivered event ${event.id.substring(0, 8)}… from ${meta.user}`);
  }

  // Periodic cursor save
  if (seenIds.size % 10 === 0) saveCursor();
}

const LOG_FILE = process.env.BUZZ_LOG_FILE || '/workspace/taliesin/.buzz-bridge.log';
function log(msg) {
  const ts = new Date().toISOString();
  const line = `[${ts}] ${msg}`;
  process.stderr.write(`[buzz-bridge] ${msg}\n`);
  try { require('fs').appendFileSync(LOG_FILE, line + '\n'); } catch { /* best effort */ }
}

// ── Graceful shutdown ───────────────────────────────────────────────
process.on('SIGTERM', () => {
  saveCursor();
  if (ws) ws.close();
  process.exit(0);
});

process.on('SIGINT', () => {
  saveCursor();
  if (ws) ws.close();
  process.exit(0);
});
