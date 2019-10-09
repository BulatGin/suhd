CREATE TABLE TrafficLight
(
	TLId SERIAL
		constraint TrafficLight_pk
			primary key,
	type SMALLINT not null,
	greenDelay FLOAT not null,
	redDelay FLOAT not null,
	location point not null
);

CREATE TABLE Camera
(
    cameraId SERIAL
        constraint Camera_pk
            primary key,
    cameraNo INTEGER UNIQUE,
    TLId INTEGER not null
        constraint TrafficLight_fk
            references TrafficLight (TLId)
                on delete restrict
                on update cascade
);
