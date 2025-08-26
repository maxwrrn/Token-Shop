DROP TABLE IF EXISTS items;
CREATE TABLE items (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  name           TEXT    NOT NULL,
  description    TEXT    NOT NULL,
  image_filename TEXT    NOT NULL,
  price          REAL    NOT NULL,
  impact         REAL    NOT NULL
);
