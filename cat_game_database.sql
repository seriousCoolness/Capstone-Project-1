-- Exported from QuickDBD: https://www.quickdatabasediagrams.com/
-- NOTE! If you have used non-SQL datatypes in your design, you will have to change these here.
DROP DATABASE IF EXISTS catgame_db;
CREATE DATABASE catgame_db;

\c catgame_db
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    date_of_creation TIMESTAMP NOT NULL,
    times_played INTEGER NOT NULL,
    battles_won INTEGER NOT NULL,
    battles_lost INTEGER NOT NULL
);

DROP TABLE IF EXISTS highscores;
CREATE TABLE highscores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    date_of_creation TIMESTAMP
);

DROP TABLE IF EXISTS enemy_histories;
CREATE TABLE enemy_histories (
    id SERIAL PRIMARY KEY,
    run_order INTEGER NOT NULL,
    score_id INTEGER,
    image_url TEXT NOT NULL,
    enemy_health INTEGER NOT NULL,
    player_health INTEGER NOT NULL

);

ALTER TABLE highscores ADD CONSTRAINT fk_highscores_user_id FOREIGN KEY(user_id)
REFERENCES users (id);

ALTER TABLE enemy_histories ADD CONSTRAINT fk_enemy_histories_score_id FOREIGN KEY(score_id)
REFERENCES highscores (id);

