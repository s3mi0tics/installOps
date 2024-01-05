-- create schema --
-- add admin, two installers, and two managers --
-- insert two unscheduled jobs --
-- insert two scheduled jobs, and one completed job w balance and one completed job without balance --
-- Schecule installs __
-- Add one installer to one scheduled job and two installers to the other scheduled jobs --
-- Add notes to the first scheduled job 2 incomplete notes and 2 complete notes--
-- Add 2 records of shades to the first scheduled job --

CREATE TABLE users(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username TEXT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'manager', 'installer')),
    hash TEXT NOT NULL
);
CREATE TABLE sqlite_sequence(name, seq);
CREATE UNIQUE INDEX username ON users (username);
CREATE TABLE jobs(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    contact TEXT,
    phone TEXT NOT NULL,
    recieved DATE DEFAULT CURRENT_DATE NOT NULL,
    address TEXT NOT NULL,
    timeframe_hour INTEGER,
    timeframe_min INTEGER,
    completed INTEGER CHECK(completed IN (1, 0)) DEFAULT 0,
    total_cost NUMERIC NOT NULL,
    paid_in_full INTEGER CHECK(paid_in_full IN (1, 0)) DEFAULT 0
);
CREATE TABLE installs(
    created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    date DATETIME,
    time TEXT,
    PRIMARY KEY (job_id, user_id),
    FOREIGN KEY (job_id) REFERENCES jobs(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE shades(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    job_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    type TEXT NOT NULL,
    location TEXT NOT NULL,
    FOREIGN KEY(job_id) REFERENCES jobs(id)
);
CREATE TABLE notes(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    job_id INTEGER NOT NULL,
    created_by INTEGER NOT NULL,
    created_on DATE DEFAULT CURRENT_DATE,
    note TEXT NOT NULL,
    completed INTEGER CHECK(completed IN (1, 0)) DEFAULT 0,
    completed_on DATE,
    completed_by INTEGER,
    FOREIGN KEY(job_id) REFERENCES jobs(id),
    FOREIGN KEY(created_by) REFERENCES users(id),
    FOREIGN KEY(completed_by) REFERENCES users(id)
);

-- Initial test values --

INSERT INTO users (username, first_name, last_name, role, hash)
    VALUES
    ('admin', 'Admin', 'Admin', 'admin', 'scrypt:32768:8:1$wZ8wsJTGcl6NMYxa$489ac9eff4b225ec711e256a254b97d84c54f4a1e0d7cdcb60272da6b3074d20cb044a3c5ee29b989779976545a5aca0270c017442fa30ab6d4e56863a2d77d5'),
    ('phil', 'Phil', 'Phil', 'installer', 'scrypt:32768:8:1$NKyBYodT0g7gBsJo$9fd40b31bce6dfb3a2cf1c84a11f1e3094b16476099ea710d0a564c4a87b675b071bb5cb399ec9d59bd767b7dd39de768a1abcc287f4f4c74985f9bd77c21744'),
    ('tom', 'Tom', 'Tom', 'installer', 'scrypt:32768:8:1$DbMZcHyT9RftmvYz$d9b1cc89887ff563b629646e9ccf9420bbac7c4ef685d85f208d157d02aa22342b2144fd9e00037d6bb0deed52120de0161adff62c88bbc90527dfef92a5cad5'),
    ('pat', 'Pat', 'Pat', 'manager', 'scrypt:32768:8:1$CNzq35sECn2lCXFj$de043e78c0097445f852768ef9eff48fa31d2a4ebeffcf5f78df4a4e944c837c0de2229117fa4883d100cf59ea359660af8fc7e4af7dbb2ffb77318a48788aa4');

INSERT INTO jobs (first_name, last_name, phone, address, timeframe_hour, timeframe_min, total_cost)
    VALUES
    ('Unscheduled job 1', 'Ikedas', '555-555-5555', '13500 Lincoln Way, Auburn, CA 95603', 1, 30, 1000),
    ('Unscheduled job 2', 'Holiday Market', '555-555-5555', '115 red rock road grass valley ca unscd2', 1, 30, 1000);

INSERT INTO jobs (first_name, last_name, contact, phone, address, timeframe_hour, timeframe_min, recieved, completed, total_cost, paid_in_full)
    VALUES
    ('Scheduled job 1', 'starduster', 'shelly', '555-555-5555', '18919 Starduster Dr, Nevada City, CA 95959', 1, 30, CURRENT_DATE, 0, 1000, 0),
    ('Scheduled job 2', 'budget', 'shelly', '555-555-5555', '310 Colfax Ave, Grass Valley, CA 95945', 1, 30, CURRENT_DATE , 0, 1000, 0),
    ('Completed job 1', 'last-com', 'Idaho Maryland Rd', '555-555-5555', '14159 Idaho Maryland Rd, Nevada City, CA 95959', 1, 30, CURRENT_DATE, 1, 1000, 0),
    ('Completed job 2', 'loma-rica', 'shelly', '555-555-5555', '12615 Charles Dr, Grass Valley, CA 95945', 1, 30, CURRENT_DATE, 1, 1000, 1);

INSERT INTO installs (user_id, job_id, date, time) VALUES (2, 3, CURRENT_DATE, CURRENT_TIME), (2, 4, CURRENT_DATE, CURRENT_TIME), (3, 4, CURRENT_DATE, CURRENT_TIME);

INSERT INTO notes (created_by, job_id, note) VALUES (4, 4, "unfinished business"), (5, 4, "unfinished business");
INSERT INTO notes (created_by, job_id, note, completed, completed_on, completed_by) VALUES (4, 4, "finished business", 1, CURRENT_DATE, 4), (5, 4, "finished business", 1, CURRENT_DATE, 5);

INSERT INTO shades (job_id, quantity, type, location) VALUES (4, 2, "es-cordless", "green"), (4, 3, "shutters", "shed"), (4, 1, "vertiglde", "garage");

