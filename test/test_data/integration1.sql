CREATE TYPE "level" AS ENUM (
  'junior',
  'middle',
  'senior',
);

CREATE TABLE "books" (
  "id" integer PRIMARY KEY AUTOINCREMENT,
  "title" varchar,
  "author" varchar,
  "country_id" integer,
  CONSTRAINT "Country Reference" FOREIGN KEY ("country_id") REFERENCES "countries" ("id")
);

CREATE TABLE "Employees" (
  "id" integer PRIMARY KEY AUTOINCREMENT,
  "name" varchar,
  "age" number DEFAULT 0,
  "level" level,
  "favorite_book_id" integer
);

COMMENT ON COLUMN "Employees"."name" IS 'Full employee name';

CREATE TABLE "countries" (
  "id" integer PRIMARY KEY AUTOINCREMENT,
  "name" varchar2 UNIQUE
);

CREATE UNIQUE INDEX ON "countries" ("name");

CREATE INDEX ON "countries" ((UPPER(name)));

ALTER TABLE "Employees" ADD FOREIGN KEY ("favorite_book_id") REFERENCES "books" ("id");