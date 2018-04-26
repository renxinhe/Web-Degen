
drop table if exists users;
drop table if exists entries;

create table users(
	userid integer primary key,
	username text not null,
	password text not null
);

create table entries(
	id integer primary key,
	name text not null,
	filename text not null,
	dt text not null,
	userid integer not null,
	FOREIGN KEY(userid) REFERENCES users(userid)
);
