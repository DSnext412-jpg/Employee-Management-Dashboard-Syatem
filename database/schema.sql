create database if not exists employee;
use employee;

create table if not exists users (
    id int auto_increment primary key,
    username varchar(100) unique not null,
    email varchar(100) unique not null,
    password varchar(100) not null,
    role varchar(50) default 'admin',
    created_at timestamp default current_timestamp
);

create table if not exists departments (
    id int auto_increment primary key,
    name varchar(100) unique not null,
    description text null,
    created_at timestamp default current_timestamp
);

create table if not exists employees (
    id int auto_increment primary key,
    employee_id varchar(50) unique not null,
    first_name varchar(100) not null,
    last_name varchar(100) not null,
    email varchar(150) unique not null,
    phone varchar(20) null,
    gender varchar(20) null,
    date_of_birth date null,
    address text null,
    position varchar(100) null,
    salary decimal(10,2) null,
    hire_date date null,
    department_id int null,
    status varchar(30) default 'active',
    created_at timestamp default current_timestamp,
    foreign key (department_id) references departments(id)
        on delete set null on update cascade
);

create index idx_employees_department_id on employees(department_id);

create table if not exists attendance (
    id int auto_increment primary key,
    employee_id int not null,
    date date not null,
    check_in time null,
    check_out time null,
    status varchar(30) default 'present',
    created_at timestamp default current_timestamp,
    foreign key (employee_id) references employees(id)
        on delete cascade on update cascade,
    unique key unique_employee_date (employee_id, date)
);

create index idx_attendance_employee_id on attendance(employee_id);

create table if not exists leaves (
    id int auto_increment primary key,
    employee_id int not null,
    leave_type varchar(50) not null,
    start_date date not null,
    end_date date not null,
    reason text null,
    status varchar(30) default 'pending',
    created_at timestamp default current_timestamp,
    foreign key (employee_id) references employees(id)
        on delete cascade on update cascade
);

create index idx_leaves_employee_id on leaves(employee_id);
