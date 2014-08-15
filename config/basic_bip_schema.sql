CREATE TYPE contestenum AS ENUM ('candidate','referendum','custom');
CREATE TYPE cfenum AS ENUM ('candidate','referendum ');
CREATE TYPE electionenum AS ENUM ('primary','general','state','Primary','General','State');
CREATE TYPE oddevenenum AS ENUM ('odd','even','both','BOTH','EVEN','ODD');
CREATE TYPE usstate AS ENUM ('AL', 'AK', 'AS', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'GU', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MH', 'MA', 'MI', 'FM', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'MP', 'OH', 'OK', 'OR', 'PW', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'VI', 'WA', 'WV', 'WI', 'WY');
CREATE SEQUENCE pksq START 1;

CREATE TABLE "election" (
"id" int4 DEFAULT nextval('pksq'),
"date" date,
"election_type" electionenum,
"is_special" bool,
"name" text,
"election_key" varchar(50),
"state_key" varchar(10),
"updated" timestamp,
PRIMARY KEY ("id") 
);

CREATE TABLE "contest" (
"id" int4 DEFAULT nextval('pksq'),
"source" text,
"election_id" int4,
"electoral_district_id" int4,
"electoral_district_name" varchar(255),
"electoral_district_type" varchar(255),
"primary_party" varchar(255),
"electorate_specifications" varchar(255),
"special" bool,
"office" varchar(255),
"level" varchar(255),
"role" varchar(255), 
"contest_type" contestenum,
"state" varchar(5),
"identifier" text,
"ed_matched" bool,
"election_key" varchar(50),
"state_key" varchar(10),
"updated" timestamp,
PRIMARY KEY ("id") 
);

CREATE TABLE "candidate" (
"id" int4 DEFAULT nextval('pksq'),
"source" text,
"name" varchar(255),
"party" varchar(255),
"candidate_url" varchar(255),
"phone" varchar(255),
"photo_url" varchar(255),
"mailing_address" text,
"email" varchar(255),
"incumbent" bool,
"google_plus_url" varchar(255),
"twitter_name" varchar(255),
"facebook_url" text,
"wiki_word" varchar(255),
"youtube" text,
"identifier" text,
"election_key" varchar(50),
"state_key" varchar(10),
"updated" timestamp,
PRIMARY KEY ("id") 
);

CREATE TABLE "candidate_in_contest" (
"source" text,
"sort_order" int4,
"contest_id" int4,
"candidate_id" int4,
"election_key" varchar(50),
"state_key" varchar(10),
PRIMARY KEY ("contest_id", "candidate_id") 
);

CREATE TABLE "electoral_district" (
"id" int4 DEFAULT nextval('pksq'),
"source" text,
"name" varchar(255),
"type" varchar(255),
"ts_id" text,
"ocdid" text,
"election_key" varchar(50),
"state_key" varchar(10),
"updated" timestamp,
PRIMARY KEY ("id") 
);


ALTER TABLE "candidate_in_contest" ADD CONSTRAINT "fk_candidate__contest_contest_1" FOREIGN KEY ("contest_id") REFERENCES "contest" ("id");
ALTER TABLE "candidate_in_contest" ADD CONSTRAINT "fk_candidate__contest_candidate_1" FOREIGN KEY ("candidate_id") REFERENCES "candidate" ("id");
ALTER TABLE "contest" ADD CONSTRAINT "fk_contest_electoral_district_1" FOREIGN KEY ("electoral_district_id") REFERENCES "electoral_district" ("id");
ALTER TABLE "contest" ADD CONSTRAINT "fk_contest_election_1" FOREIGN KEY ("election_id") REFERENCES "election" ("id");