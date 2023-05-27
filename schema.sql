-- DATABASE SCHEMA for sqlite3
-- Runs on database.py -> init_database()
-- table names standard plural

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY,
	username TEXT UNIQUE COLLATE NOCASE,
	username_case TEXT,				-- Store username with case for display
	password TEXT 					-- Password will be hashed or something, idk
);

CREATE TABLE IF NOT EXISTS api_keys (
	id INTEGER PRIMARY KEY,
	user_id INTEGER NOT NULL REFERENCES users(id),
	name TEXT NOT NULL,					-- API key name eg: "openai" or "elevenlabs"
	key_str TEXT NOT NULL				-- Should hash API keys too or..?
);

CREATE TABLE IF NOT EXISTS sequences (
	id INTEGER PRIMARY KEY,
	user_id INTEGER NOT NULL REFERENCES users(id),
	name TEXT NOT NULL,
	script TEXT
);

CREATE TABLE IF NOT EXISTS segments (
	id INTEGER PRIMARY KEY,
	sequence_id INTEGER NOT NULL REFERENCES sequences(id),
	sequence_index INTEGER NOT NULL,			-- index in the sequence
	text_version INTEGER,
	image_version INTEGER,
	audio_version INTEGER
);

CREATE TABLE IF NOT EXISTS segment_text (
	segment_id INTEGER NOT NULL REFERENCES segments(id),
	content TEXT NOT NULL,			-- plaintext
	version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS segment_image (
	segment_id INTEGER NOT NULL REFERENCES segments(id),
	content TEXT NOT NULL,				-- url
	version INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS segment_audio (
	segment_id INTEGER NOT NULL REFERENCES segments(id),
	content TEXT NOT NULL,				-- url
	version INTEGER NOT NULL
);