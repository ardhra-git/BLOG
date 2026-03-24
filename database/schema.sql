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