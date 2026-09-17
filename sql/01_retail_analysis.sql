-- ============================================================
-- RetailVision AI - SQL Analysis
-- Retail Sales Analytics Project
-- ============================================================

-- Database: retail_sales.db
-- Source: cleaned_data.csv

-- ============================================================
-- 1. BASIC DATA VALIDATION
-- ============================================================

SELECT COUNT(*) AS total_records
FROM retail_sales;

SELECT *
FROM retail_sales
LIMIT 10;

-- ============================================================
-- 2. TOTAL SALES
-- ============================================================

SELECT 
    SUM(Sales) AS total_sales
FROM retail_sales;

-- ============================================================
-- 3. TOTAL CUSTOMERS
-- ============================================================

SELECT 
    SUM(Customers) AS total_customers
FROM retail_sales;

-- ============================================================
-- 4. STORE COUNT
-- ============================================================

SELECT 
    COUNT(DISTINCT Store) AS total_stores
FROM retail_sales;

-- ============================================================
-- 5. SALES BY YEAR
-- ============================================================

SELECT
    Year,
    SUM(Sales) AS total_sales
FROM retail_sales
GROUP BY Year
ORDER BY Year;


-- ============================================================
-- 6. SALES BY MONTH
-- ============================================================

SELECT
    Year,
    Month,
    SUM(Sales) AS total_sales
FROM retail_sales
GROUP BY Year, Month
ORDER BY Year, Month;


-- ============================================================
-- 7. SALES BY STORE TYPE
-- ============================================================

SELECT
    StoreType,
    SUM(Sales) AS total_sales,
    AVG(Sales) AS average_daily_sales
FROM retail_sales
GROUP BY StoreType
ORDER BY total_sales DESC;


-- ============================================================
-- 8. SALES BY ASSORTMENT
-- ============================================================

SELECT
    Assortment,
    SUM(Sales) AS total_sales,
    AVG(Sales) AS average_daily_sales
FROM retail_sales
GROUP BY Assortment
ORDER BY total_sales DESC;


-- ============================================================
-- 9. PROMOTION IMPACT ON SALES
-- ============================================================

SELECT
    Promo,
    COUNT(*) AS records,
    AVG(Sales) AS average_sales,
    SUM(Sales) AS total_sales
FROM retail_sales
GROUP BY Promo
ORDER BY Promo;


-- ============================================================
-- 10. HOLIDAY IMPACT ON SALES
-- ============================================================

SELECT
    StateHoliday,
    COUNT(*) AS records,
    AVG(Sales) AS average_sales,
    SUM(Sales) AS total_sales
FROM retail_sales
GROUP BY StateHoliday
ORDER BY total_sales DESC;

-- ============================================================
-- 11. SALES BY WEEKDAY
-- ============================================================

SELECT
    Weekday,
    AVG(Sales) AS average_sales,
    SUM(Sales) AS total_sales
FROM retail_sales
GROUP BY Weekday
ORDER BY average_sales DESC;


-- ============================================================
-- 12. CUSTOMER PERFORMANCE
-- ============================================================

SELECT
    Store,
    AVG(Customers) AS average_customers,
    MAX(Customers) AS maximum_customers
FROM retail_sales
GROUP BY Store
ORDER BY average_customers DESC
LIMIT 20;


-- ============================================================
-- 13. SALES PER CUSTOMER
-- ============================================================

SELECT
    Store,
    AVG(
        CASE
            WHEN Customers > 0
            THEN CAST(Sales AS REAL) / Customers
        END
    ) AS average_sales_per_customer
FROM retail_sales
GROUP BY Store
ORDER BY average_sales_per_customer DESC
LIMIT 20;


-- ============================================================
-- 14. PROMOTION VS NON-PROMOTION SALES
-- ============================================================

SELECT
    Promo,
    AVG(Sales) AS average_sales,
    AVG(Customers) AS average_customers
FROM retail_sales
GROUP BY Promo
ORDER BY Promo;


-- ============================================================
-- 15. COMPETITION IMPACT ON SALES
-- ============================================================

SELECT
    CASE
        WHEN CompetitionDistance IS NULL THEN 'Unknown'
        WHEN CompetitionDistance < 1000 THEN 'Near'
        WHEN CompetitionDistance < 5000 THEN 'Medium'
        ELSE 'Far'
    END AS competition_distance_group,
    COUNT(*) AS records,
    AVG(Sales) AS average_sales,
    AVG(Customers) AS average_customers
FROM retail_sales
GROUP BY competition_distance_group
ORDER BY average_sales DESC;

-- ============================================================
-- 16. TOP 20 STORES BY TOTAL SALES
-- ============================================================

SELECT
    Store,
    SUM(Sales) AS total_sales,
    SUM(Customers) AS total_customers,
    AVG(Sales) AS average_daily_sales
FROM retail_sales
GROUP BY Store
ORDER BY total_sales DESC
LIMIT 20;


-- ============================================================
-- 17. BOTTOM 20 STORES BY TOTAL SALES
-- ============================================================

SELECT
    Store,
    SUM(Sales) AS total_sales,
    SUM(Customers) AS total_customers,
    AVG(Sales) AS average_daily_sales
FROM retail_sales
GROUP BY Store
ORDER BY total_sales ASC
LIMIT 20;


-- ============================================================
-- 18. PROMOTION INTERVAL IMPACT
-- ============================================================

SELECT
    PromoInterval,
    COUNT(*) AS records,
    AVG(Sales) AS average_sales,
    AVG(Customers) AS average_customers
FROM retail_sales
GROUP BY PromoInterval
ORDER BY average_sales DESC;


-- ============================================================
-- 19. SCHOOL HOLIDAY IMPACT
-- ============================================================

SELECT
    SchoolHoliday,
    COUNT(*) AS records,
    AVG(Sales) AS average_sales,
    AVG(Customers) AS average_customers,
    SUM(Sales) AS total_sales
FROM retail_sales
GROUP BY SchoolHoliday
ORDER BY average_sales DESC;


-- ============================================================
-- 20. OVERALL STORE PERFORMANCE RANKING
-- ============================================================

SELECT
    Store,
    SUM(Sales) AS total_sales,
    AVG(Sales) AS average_daily_sales,
    AVG(Customers) AS average_customers,
    RANK() OVER (
        ORDER BY SUM(Sales) DESC
    ) AS sales_rank
FROM retail_sales
GROUP BY Store
ORDER BY sales_rank;