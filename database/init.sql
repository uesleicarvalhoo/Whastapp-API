CREATE DATABASE whatsapp_api;
USE whatsapp_api;

CREATE TABLE messages(
    id integer primary key auto_increment,
    text varchar(1000),
    contact_number varchar(13) not null,
    media varchar(100),
    conversation_id integer,
    created_at datetime,
    updated_at datetime
);


CREATE TABLE conversations(
    id Integer primary key auto_increment,
    started_at datetime,
    finished_at datetime
);

ALTER TABLE "messages"
ADD FOREIGN KEY ("conversation_id") REFERENCES "conversations" ("id") ON DELETE RESTRICT ON UPDATE RESTRICT



-- CREATE DATABASE whatsapp_api;


-- CREATE TABLE conversations(
--     id INT GENERATED ALWAYS AS IDENTITY,
--     started_at TIMESTAMP,
--     finished_at TIMESTAMP,
--     PRIMARY KEY(id)
-- );

-- CREATE TABLE messages(
--     id INT GENERATED ALWAYS AS IDENTITY,
--     text VARCHAR(1000),
--     contact_number INTEGER NOT NULL,
--     media varchar(100),
--     conversation_id INTEGER,

--     PRIMARY KEY(id),
--     CONSTRAINT fk_conversation
--       FOREIGN KEY(conversation_id) 
-- 	  REFERENCES conversations(id)
-- );
