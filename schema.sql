DROP TABLE IF EXISTS news;
DROP TABLE IF EXISTS groups;

CREATE TABLE news (
  id                     INTEGER PRIMARY KEY AUTOINCREMENT,
  item_id,
  channel                VARCHAR(150),
  date_created           VARCHAR(150),
  date_created_timestamp INTEGER,


  headline               VARCHAR(150),
  language               VARCHAR(150),
  keywords               VARCHAR(150),

  full_xml               TEXT,
  additional_json_metada TEXT,

  group_id               INTEGER
);


CREATE TABLE groups (
  id                     INTEGER PRIMARY KEY AUTOINCREMENT,
  date_created           VARCHAR(150),
  date_created_timestamp INTEGER,

  keywords               VARCHAR(150)
);


CREATE INDEX idx_news_date_created_timestamp ON news (date_created_timestamp);
CREATE INDEX idx_news_group_id ON news (group_id);
CREATE UNIQUE INDEX idx_news_item_id ON news (item_id);

CREATE INDEX idx_groups_date_created_timestamp ON groups (date_created_timestamp);

