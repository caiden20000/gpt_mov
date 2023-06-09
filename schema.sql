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
	key_type TEXT NOT NULL,				-- API key name eg: "openai" or "elevenlabs"
	key_str TEXT NOT NULL,				-- Should hash API keys too or..?
	UNIQUE(user_id, key_type)			-- A user can only have one key for one service.
);

CREATE TABLE IF NOT EXISTS sequences (
	id INTEGER PRIMARY KEY,
	user_id INTEGER NOT NULL REFERENCES users(id),
	sequence_name TEXT NOT NULL,
	script TEXT,
	UNIQUE(user_id, sequence_name)				-- A user cannot have two identically named sequences.
);

CREATE TABLE IF NOT EXISTS segments (
	id INTEGER PRIMARY KEY,
	sequence_id INTEGER NOT NULL REFERENCES sequences(id),
	sequence_index INTEGER NOT NULL,			-- index in the sequence
	text_version INTEGER DEFAULT 0,
	image_version INTEGER DEFAULT 0,
	audio_version INTEGER DEFAULT 0--,
	-- UNIQUE(sequence_id, sequence_index)		-- A sequence is linear, indices must be unique.
);

CREATE TABLE IF NOT EXISTS segment_text (
	segment_id INTEGER NOT NULL REFERENCES segments(id),
	content TEXT NOT NULL,			-- plaintext
	version INTEGER NOT NULL,
	UNIQUE(segment_id, version)
);

CREATE TABLE IF NOT EXISTS segment_image (
	segment_id INTEGER NOT NULL REFERENCES segments(id),
	content TEXT NOT NULL,				-- url
	version INTEGER NOT NULL,
	UNIQUE(segment_id, version)
);

CREATE TABLE IF NOT EXISTS segment_audio (
	segment_id INTEGER NOT NULL REFERENCES segments(id),
	content TEXT NOT NULL,				-- url
	version INTEGER NOT NULL,
	UNIQUE(segment_id, version)
);