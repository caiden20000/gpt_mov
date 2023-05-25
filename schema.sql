-- DATABASE SCHEMA for sqlite3
-- ! plural names

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY,
	username TEXT UNIQUE COLLATE NOCASE,
	username_case TEXT,
	password TEXT 					-- Password will be hashed or something, idk
);

CREATE TABLE IF NOT EXISTS api_keys (
	id INTEGER PRIMARY KEY,
	user_id INTEGER REFERENCES users(id),
	openai TEXT,					-- Should hash API keys too or..?
	elevenlabs TEXT
);

CREATE TABLE IF NOT EXISTS sequences (
	id INTEGER PRIMARY KEY,
	user_id INTEGER REFERENCES users(id),
	name TEXT NOT NULL,
	script TEXT
);

CREATE TABLE IF NOT EXISTS segments (
	id INTEGER NOT NULL,
	sequence_id INTEGER NOT NULL,
	index INTEGER NOT NULL,			-- index in the sequence
	text_version INTEGER,
	image_version INTEGER,
	audio_version INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY (sequence_id) REFERENCES sequences(id)
);

CREATE TABLE IF NOT EXISTS segment_text (
	segment_id INTEGER NOT NULL,
	content TEXT NOT NULL,			-- plaintext
	version INTEGER NOT NULL,
	FOREIGN KEY (segment_id) REFERENCES segments(id)
);

CREATE TABLE IF NOT EXISTS segment_image (
	segment_id INTEGER NOT NULL,
	content TEXT NOT NULL,				-- url
	version INTEGER NOT NULL,
	FOREIGN KEY (segment_id) REFERENCES segments(id)
);

CREATE TABLE IF NOT EXISTS segment_audio (
	segment_id INTEGER NOT NULL,
	content TEXT NOT NULL,				-- url
	version INTEGER NOT NULL,
	FOREIGN KEY (segment_id) REFERENCES segments(id)
);