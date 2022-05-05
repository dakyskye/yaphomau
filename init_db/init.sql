create table if not exists countries (
	id integer primary key autoincrement,
	country varchar(3) unique not null
);

create table if not exists regions (
	id integer primary key autoincrement,
	region varchar(48) not null,
	country_id integer not null,
	foreign key(country_id) references countries(id) on delete cascade
);

create table if not exists cities (
	id integer primary key autoincrement,
	city varchar(64) not null,
	country_id integer not null,
	region_id integer not null,
	foreign key(country_id) references countries(id) on delete cascade,
	foreign key(region_id) references regions(id) on delete cascade
);

create table if not exists ip_addresses (
	ip varchar(16) primary key,
	country_id integer not null,
	region_id integer not null,
	city_id integer not null,
	foreign key(country_id) references countries(id) on delete cascade,
	foreign key(region_id) references regions(id) on delete cascade,
	foreign key(city_id) references cities(id) on delete cascade
);
