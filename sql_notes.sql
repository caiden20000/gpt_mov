-- DATABASE SCHEMA
-- for SQLite

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS user (
	id INTEGER NOT NULL,
	name TEXT UNIQUE,
	password TEXT, 					-- Password will be hashed or something, idk
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS api_keys (
	id INTEGER NOT NULL,
	openai TEXT,					-- Should hash API keys too or..?
	elevenlabs TEXT,
	PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS sequence (
	id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	name TEXT NOT NULL,
	script TEXT,
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS segment (
	id INTEGER NOT NULL,
	sequence_id INTEGER NOT NULL,
	index INTEGER NOT NULL,			-- index in the sequence
	text_version INTEGER,
	image_version INTEGER,
	audio_version INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY (sequence_id) REFERENCES sequence(id)
);

CREATE TABLE IF NOT EXISTS segment_text (
	segment_id INTEGER NOT NULL,
	content TEXT NOT NULL,			-- plaintext
	version INTEGER NOT NULL,
	FOREIGN KEY (segment_id) REFERENCES segment(id)
);

CREATE TABLE IF NOT EXISTS segment_image (
	segment_id INTEGER NOT NULL,
	content TEXT NOT NULL,				-- url
	version INTEGER NOT NULL,
	FOREIGN KEY (segment_id) REFERENCES segment(id)
);

CREATE TABLE IF NOT EXISTS segment_audio (
	segment_id INTEGER NOT NULL,
	content TEXT NOT NULL,				-- url
	version INTEGER NOT NULL,
	FOREIGN KEY (segment_id) REFERENCES segment(id)
);


-- Get text of n-th index segment

SELECT content FROM segment_text
WHERE segment_id IN (
	SELECT id
	FROM segment 
	WHERE sequence_id = "<project-id>" 
		AND index = "<index>"
);

-- Alternative get text of n-th index segment:

WITH selected_segment_id AS (
	SELECT id
	FROM segment 
	WHERE sequence_id = "<project-id>" 
		AND index = "<index>"
)
SELECT content 
FROM segment_text
WHERE segment_id IN selected_segment_id;


-- /api/projects/<project-id>

SELECT * FROM segment
WHERE sequence_id = "<project-id>";