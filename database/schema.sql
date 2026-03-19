-- PostgreSQL Schema for Blog Website
-- Run this in psql or pgAdmin

CREATE DATABASE blog_db;

\c blog_db;

CREATE TABLE IF NOT EXISTS posts (
  id         SERIAL PRIMARY KEY,
  tag        VARCHAR(50)  NOT NULL,
  title      VARCHAR(255) NOT NULL,
  excerpt    TEXT         NOT NULL,
  body       TEXT         NOT NULL,
  read_time  VARCHAR(20)  DEFAULT '3 min read',
  created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS contacts (
  id           SERIAL PRIMARY KEY,
  name         VARCHAR(100) NOT NULL,
  email        VARCHAR(150) NOT NULL,
  message      TEXT         NOT NULL,
  submitted_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- Sample posts
INSERT INTO posts (tag, title, excerpt, body, read_time) VALUES
(
  'Lifestyle',
  '5 Morning Habits That Actually Stick',
  'Most morning routines fail because they are too ambitious. Here is how to start small.',
  'Most people quit their morning routine by day four. Not because they are lazy — but because they designed it wrong.

The trick is to start with one habit only. Make it so small it feels embarrassing. Drink a glass of water when you wake up.

Once that becomes automatic, stack the next habit on top. After water, do two minutes of stretching.

Small wins compound. In three months, you will have a morning routine that runs itself.',
  '3 min read'
),
(
  'Technology',
  'Why I Stopped Using My Smartphone for a Week',
  'What I expected to be painful turned into the most productive week I had in years.',
  'I did not plan it. My phone broke on a Monday, and I decided not to replace it until Sunday.

The first two days were uncomfortable. By day three, something shifted. I started noticing things.

I read two books that week. I slept better. It was one of the best weeks of the year.',
  '5 min read'
),
(
  'Writing',
  'How to Write When You Have Nothing to Say',
  'Writer block is not a lack of ideas. It is a fear of bad ideas. Here is how to get unstuck.',
  'Every writer knows the feeling. You open a blank document. You type a sentence. You delete it.

Here is the truth: you do have something to say. You just do not trust it yet.

The fix? Write badly on purpose. Set a timer for ten minutes and write the worst version possible.',
  '4 min read'
);
