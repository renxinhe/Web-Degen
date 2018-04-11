drop table if exists users;

create table users(
	userid integer primary key,
	username text not null,
	password text not null
);
