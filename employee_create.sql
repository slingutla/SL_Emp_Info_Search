CREATE TABLE employees (
    
    employee_id        INT PRIMARY KEY,
    
    first_name         VARCHAR(100) NOT NULL,
    
    last_name          VARCHAR(100) NOT NULL,
    
    department         VARCHAR(100) NOT NULL,
    
    role               VARCHAR(100) NOT NULL,
    
    employment_status  VARCHAR(20) NOT NULL
        CHECK (employment_status IN ('Active', 'Terminated', 'On Leave')),
    
    hire_date          DATE NOT NULL,
    
    leave_type         VARCHAR(100) NULL,
    
    salary_local       DECIMAL(15,2) NOT NULL CHECK (salary_local >= 0),
    
    salary_usd         DECIMAL(15,2) NOT NULL CHECK (salary_usd >= 0),
    
    manager_name       VARCHAR(200) NOT NULL
    
);