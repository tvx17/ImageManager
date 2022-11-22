create table main.users
(
    id         integer not null
        constraint users_pk
            primary key autoincrement,
    first_name text,
    last_name  text,
    pseydonym  text,
    shortcut   text
);

