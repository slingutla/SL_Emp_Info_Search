SELECT * FROM employees;

INSERT INTO employees 
(employee_id, first_name, last_name, department, role, employment_status, hire_date, leave_type, salary_local, salary_usd, manager_name)
VALUES
(1001, 'John',     'Smith',     'Finance',        'Financial Analyst',      'Active',      '2018-03-15', NULL,            85000.00, 85000.00, 'Laura Johnson'),

(1002, 'Priya',    'Rao',       'Engineering',    'Software Engineer',      'Active',      '2020-07-10', NULL,            120000.00,120000.00,'Michael Chen'),

(1003, 'Carlos',   'Mendez',    'HR',             'HR Manager',             'Active',      '2016-01-22', NULL,            95000.00, 95000.00, 'Sarah Williams'),

(1004, 'Emily',    'Davis',     'Engineering',    'DevOps Engineer',        'On Leave',    '2019-11-05', 'Maternity Leave',115000.00,115000.00,'Michael Chen'),

(1005, 'Wei',      'Zhang',     'Sales',          'Sales Executive',        'Active',      '2021-06-18', NULL,            90000.00, 90000.00, 'Robert King'),

(1006, 'Amit',     'Sharma',    'Engineering',    'Data Engineer',          'Active',      '2022-02-01', NULL,            105000.00,105000.00,'Michael Chen'),

(1007, 'Linda',    'Brown',     'Operations',     'Operations Manager',     'Active',      '2015-09-12', NULL,            110000.00,110000.00,'David Wilson'),

(1008, 'Fatima',   'Ali',       'Finance',        'Accountant',             'Terminated',  '2017-04-30', NULL,            78000.00, 78000.00, 'Laura Johnson'),

(1009, 'Daniel',   'Garcia',    'Engineering',    'QA Engineer',            'Active',      '2023-01-09', NULL,            95000.00, 95000.00, 'Michael Chen'),

(1010, 'Sophie',   'Martin',    'HR',             'Recruiter',              'On Leave',    '2021-10-14', 'Medical Leave', 72000.00, 72000.00, 'Carlos Mendez');