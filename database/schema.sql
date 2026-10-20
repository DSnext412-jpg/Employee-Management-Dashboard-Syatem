create database if not exists employee360;
use employee360;

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

insert ignore into departments (name, description) values
('Human Resources', 'HR Department'),
('Engineering', 'Engineering Department'),
('Marketing', 'Marketing Department'),
('Finance', 'Finance Department'),
('Operations', 'Operations Department');

insert ignore into employees (employee_id, first_name, last_name, email, phone, gender, date_of_birth, address, position, salary, hire_date, department_id, status) values
('EMP001', 'John', 'Doe', 'john.doe@company.com', '555-0101', 'Male', '1990-05-15', '123 Main St, City', 'Software Engineer', 75000.00, '2021-03-15', 2, 'active'),
('EMP002', 'Jane', 'Smith', 'jane.smith@company.com', '555-0202', 'Female', '1988-08-20', '456 Oak Ave, Town', 'HR Manager', 80000.00, '2020-01-10', 1, 'active'),
('EMP003', 'Michael', 'Johnson', 'michael.johnson@company.com', '555-0303', 'Male', '1992-12-10', '789 Pine Rd, Village', 'Data Analyst', 65000.00, '2022-06-01', 2, 'active'),
('EMP004', 'Emily', 'Davis', 'emily.davis@company.com', '555-0404', 'Female', '1991-03-25', '321 Elm St, City', 'Marketing Specialist', 60000.00, '2021-11-01', 3, 'active'),
('EMP005', 'David', 'Wilson', 'david.wilson@company.com', '555-0505', 'Male', '1989-07-30', '654 Maple Dr, Town', 'Financial Analyst', 70000.00, '2019-05-20', 4, 'active');

insert ignore into attendance (employee_id, date, check_in, check_out, status) values
(1, '2024-01-15', '08:00:00', '17:00:00', 'present'),
(1, '2024-01-16', '08:15:00', '17:15:00', 'present'),
(2, '2024-01-15', '09:00:00', '18:00:00', 'present'),
(3, '2024-01-15', '08:30:00', '16:30:00', 'present'),
(4, '2024-01-15', '09:00:00', '17:00:00', 'present'),
(5, '2024-01-15', '08:00:00', '17:00:00', 'present');

insert ignore into leaves (employee_id, leave_type, start_date, end_date, reason, status) values
(1, 'Annual', '2024-02-01', '2024-02-05', 'Vacation', 'approved'),
(2, 'Sick', '2024-02-10', '2024-02-12', 'Flu', 'approved'),
(3, 'Annual', '2024-03-15', '2024-03-19', 'Family trip', 'pending'),
(4, 'Sick', '2024-03-20', '2024-03-22', 'Fever', 'pending'),
(5, 'Annual', '2024-04-01', '2024-04-05', 'Holiday', 'pending');