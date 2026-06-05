CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    segment TEXT NOT NULL,
    region TEXT NOT NULL,
    signup_date DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL REFERENCES customers(customer_id),
    order_date DATE NOT NULL,
    region TEXT NOT NULL,
    channel TEXT NOT NULL,
    revenue_usd NUMERIC(12, 2) NOT NULL,
    cost_usd NUMERIC(12, 2) NOT NULL,
    status TEXT NOT NULL
);

INSERT INTO customers (customer_id, customer_name, segment, region, signup_date) VALUES
('C001', 'Atlas Retail', 'Enterprise', 'West', '2024-01-10'),
('C002', 'Bluebird Foods', 'SMB', 'South', '2024-02-18'),
('C003', 'Crest Labs', 'Enterprise', 'East', '2024-03-05'),
('C004', 'Delta Sports', 'Mid-Market', 'North', '2024-04-22'),
('C005', 'Evergreen Health', 'Enterprise', 'West', '2024-05-11'),
('C006', 'Futura Tech', 'SMB', 'East', '2024-06-01')
ON CONFLICT DO NOTHING;

INSERT INTO orders (order_id, customer_id, order_date, region, channel, revenue_usd, cost_usd, status) VALUES
('O1001', 'C001', '2025-10-05', 'West', 'Direct', 120000.00, 77000.00, 'completed'),
('O1002', 'C002', '2025-10-12', 'South', 'Partner', 68000.00, 41200.00, 'completed'),
('O1003', 'C003', '2025-10-18', 'East', 'Direct', 91000.00, 59000.00, 'completed'),
('O1004', 'C004', '2025-11-03', 'North', 'Online', 53000.00, 33000.00, 'completed'),
('O1005', 'C005', '2025-11-20', 'West', 'Direct', 130000.00, 80000.00, 'completed'),
('O1006', 'C006', '2025-11-25', 'East', 'Online', 47000.00, 30000.00, 'completed'),
('O1007', 'C001', '2025-12-09', 'West', 'Partner', 99000.00, 64000.00, 'completed'),
('O1008', 'C004', '2025-12-21', 'North', 'Direct', 61000.00, 37000.00, 'completed'),
('O1009', 'C003', '2026-01-07', 'East', 'Direct', 108000.00, 69000.00, 'completed'),
('O1010', 'C002', '2026-01-18', 'South', 'Online', 70000.00, 43000.00, 'completed'),
('O1011', 'C005', '2026-01-22', 'West', 'Direct', 142000.00, 86000.00, 'completed'),
('O1012', 'C006', '2026-02-04', 'East', 'Partner', 52000.00, 32500.00, 'completed'),
('O1013', 'C004', '2026-02-15', 'North', 'Direct', 69000.00, 42000.00, 'completed'),
('O1014', 'C001', '2026-02-27', 'West', 'Online', 115000.00, 72000.00, 'completed'),
('O1015', 'C003', '2026-03-06', 'East', 'Direct', 117000.00, 73500.00, 'completed'),
('O1016', 'C002', '2026-03-14', 'South', 'Partner', 76000.00, 47000.00, 'completed'),
('O1017', 'C005', '2026-03-25', 'West', 'Direct', 148000.00, 90500.00, 'completed')
ON CONFLICT DO NOTHING;

DROP VIEW IF EXISTS revenue_by_region;
CREATE VIEW revenue_by_region AS
SELECT
    region,
    DATE_TRUNC('month', order_date)::DATE AS month,
    SUM(revenue_usd) AS total_revenue_usd,
    SUM(cost_usd) AS total_cost_usd,
    SUM(revenue_usd - cost_usd) AS gross_margin_usd
FROM orders
WHERE status = 'completed'
GROUP BY 1, 2;

DROP VIEW IF EXISTS sales_summary;
CREATE VIEW sales_summary AS
SELECT
    DATE_TRUNC('quarter', order_date)::DATE AS quarter_start,
    region,
    COUNT(*) AS total_orders,
    SUM(revenue_usd) AS total_revenue_usd,
    SUM(revenue_usd - cost_usd) AS gross_margin_usd,
    ROUND((SUM(revenue_usd - cost_usd) / NULLIF(SUM(revenue_usd), 0)) * 100, 2) AS gross_margin_pct
FROM orders
WHERE status = 'completed'
GROUP BY 1, 2;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analytics_ro') THEN
        CREATE ROLE analytics_ro LOGIN PASSWORD 'analytics_ro';
    END IF;
END $$;

GRANT CONNECT ON DATABASE analytics TO analytics_ro;
GRANT USAGE ON SCHEMA public TO analytics_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics_ro;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analytics_ro;
