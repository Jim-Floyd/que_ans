create table User (
id integer primary key autoincrement,
name text not null,
password text not null,
expert boolean not null,
admin boolean not null
);
create table question (
id integer primary key autoincrement,
question_text text not null,
answer_text text not null,
asked_id integer not null,
expert_id integer not null
);