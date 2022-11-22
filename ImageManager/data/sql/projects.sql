create table main.projects
(
    id          integer not null
        constraint projects_pk
            primary key autoincrement,
    name        text    not null,
    active      integer not null,
    owner       integer,
    description text
);

