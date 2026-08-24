#!/usr/bin/env node
/**
 * buzz-bridge — MCP channel server that subscribes to a Buzz relay
 * via Nostr WebSocket and emits notifications/claude/channel for each
 * matching event. Uses the official @modelcontextprotocol/sdk.
 *
 * Env:
 *   BUZZ_PRIVATE_KEY  — Nostr private key (hex)
 *   BUZZ_RELAY_URL    — wss:// relay URL
 *   BUZZ_CHANNELS     — comma-separated channel UUIDs to watch (optional; default: all)
 *   BUZZ_CURSOR_FILE  — path to persist last-seen event timestamp
 *
 * Protocol: MCP over stdio via @modelcontextprotocol/sdk.
 * Delivery: at-least-once with recognizable duplicates (Nostr event ID dedup).
 */

import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const WebSocket = require('ws');
const { getPublicKey, finalizeEvent } = require('nostr-tools/pure');
const { bytesToHex, hexToBytes } = require('nostr-tools/utils');
import { readFileSync, writeFileSync, existsSync } from 'fs';

// MCP SDK imports
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js';

// ── Config ──────────────────────────────────────────────────────────
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
const SEEN_WINDOW = 1000;

if (!PRIVATE_KEY) {
  process.stderr.write(JSON.stringify({ error: 'config', message: 'BUZZ_PRIVATE_KEY required' }) + '\n');
  process.exit(1);
}

// ── State ───────────────────────────────────────────────────────────
const seenIds = new Set();
let lastTimestamp = 0;

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

// ── MCP Server (using official SDK) ─────────────────────────────────
const mcp = new Server(
  { name: 'buzz', version: '0.1.0' },
  {
    capabilities: {
      experimental: { 'claude/channel': {} },
      tools: {},
    },
    instructions: 'Buzz channel messages arrive as <channel source="plugin:buzz:buzz" ...>. '
      + 'They are Nostr events from a Buzz relay. Respond with the buzz-reply skill or the send tool.',
  },
);

// Tool: send a message to Buzz
mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: 'send',
    description: 'Send a message to Buzz',
    inputSchema: {
      type: 'object',
      required: ['content'],
      properties: {
        content: { type: 'string', description: 'Message text to send' },
        channel: { type: 'string', description: 'Channel UUID (optional — uses default if omitted)' },
      },
    },
  }],
}));

mcp.setRequestHandler(CallToolRequestSchema, async (req) => {
  const toolName = req.params?.name;
  if (toolName === 'send') {
    const content = req.params?.arguments?.content || '';
    const channel = req.params?.arguments?.channel || '';
    log(`send tool called: content="${content.substring(0, 60)}" channel="${channel}"`);
    return {
      content: [{ type: 'text', text: 'Send tool not yet wired — use buzz-reply skill for outbound.' }],
    };
  }
  throw new Error(`Unknown tool: ${toolName}`);
});

// ── Relay state (must be declared before connectRelay is called) ────
let ws = null;
let reconnectTimer = null;
let authenticated = false;
let subscribed = false;
let pendingAuthEventId = null;

// Connect to Claude Code over stdio
const transport = new StdioServerTransport();
await mcp.connect(transport);
log('MCP SDK connected — connecting to relay');

// Connect to the Nostr relay now that MCP is ready
connectRelay();

// ── Nostr helpers ───────────────────────────────────────────────────
function derivePublicKey(privKeyHex) {
  const sk = hexToBytes(privKeyHex);
  const pk = getPublicKey(sk);
  return typeof pk === 'string' ? pk : bytesToHex(pk);
}

function makeSubFilter() {
  const pubkey = derivePublicKey(PRIVATE_KEY);
  const filter = { kinds: [9], '#p': [pubkey], since: lastTimestamp || undefined };
  const filters = [filter];
  if (CHANNELS.length > 0) {
    filters.push({ kinds: [9], '#h': CHANNELS, since: lastTimestamp || undefined });
  }
  return filters;
}

// ── Relay connection ────────────────────────────────────────────────
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
    setTimeout(() => {
      if (!authenticated && !subscribed && !pendingAuthEventId) {
        log('no AUTH challenge received — subscribing without auth');
        subscribe();
      }
    }, 3000);
    setTimeout(() => {
      if (pendingAuthEventId && !authenticated && !subscribed) {
        log('auth OK never received after 10s — reconnecting');
        ws.close();
      }
    }, 10000);

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
  } catch (err) {
    log(`auth failed: ${err.message}`);
  }
}

async function handleEvent(event) {
  if (!event || !event.id) return;

  // Dedup
  if (seenIds.has(event.id)) return;
  seenIds.add(event.id);
  if (seenIds.size > SEEN_WINDOW * 2) {
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

  // Build notification using the SDK
  const meta = {
    chat_id: `buzz:${channelId}`,
    message_id: event.id,
    user: event.pubkey.substring(0, 12),
    user_id: event.pubkey,
    ts: new Date(event.created_at * 1000).toISOString(),
    relay: RELAY_URL,
  };

  log(`sending MCP notification for event ${event.id.substring(0, 8)}… content="${(event.content || '').substring(0, 60)}"`);
  try {
    await mcp.notification({
      method: 'notifications/claude/channel',
      params: { content: event.content || '', meta },
    });
    log(`delivered event ${event.id.substring(0, 8)}… from ${meta.user}`);
  } catch (err) {
    log(`notification error: ${err.message}`);
  }

  // Periodic cursor save
  if (seenIds.size % 10 === 0) saveCursor();
}

// ── Logging ─────────────────────────────────────────────────────────
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
