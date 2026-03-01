DROP VIEW IF EXISTS users_loc_distribution;
DROP VIEW IF EXISTS origin_of_orders_cat_subcat;
DROP VIEW IF EXISTS origin_of_orders_loc;
DROP VIEW IF EXISTS cat_sub_sales_performace;

CREATE VIEW users_loc_distribution AS (
	SELECT location, COUNT(*) AS n_users
    FROM users
    GROUP BY location);

CREATE VIEW origin_of_orders_cat_subcat AS (
	SELECT category, subcategory, COUNT(*) AS n_orders
	FROM orders JOIN products USING (product_id)
	GROUP BY category, subcategory
	ORDER BY n_orders DESC);

CREATE VIEW origin_of_orders_loc AS (
    SELECT 
        location,
        pop_size,
        COUNT(*) AS n_orders,
        COUNT(*) / pop_size AS n_orders_per_hab
    FROM
        orders
            JOIN
        users USING (user_id)
            JOIN
        (SELECT 
            u.location,
            COUNT(*) AS pop_size
        FROM
            users u
        GROUP BY u.location) AS pop USING (location)
    GROUP BY location
    ORDER BY n_orders DESC);

CREATE VIEW cat_sub_sales_performace AS (
    WITH temp AS 
        (SELECT 
            p.category,
            p.subcategory,
            SUM(s.available_units) + COUNT(*) AS initial_stock,
            COUNT(*) AS n_orders,
            SUM(s.available_units) AS final_stock,
            SUM(p.cost * s.available_units) + SUM(p.cost) AS initial_stock_value,
            SUM(p.cost) AS revenue,
            SUM(p.cost * s.available_units) AS final_stock_value
        FROM 
            stock s
                JOIN
            products p USING (product_id)
                LEFT JOIN
            orders o USING (product_id)
        GROUP BY p.category, p.subcategory
        ORDER BY p.category, p.subcategory)
    SELECT 
        category,
        subcategory,
        initial_stock,
        n_orders,
        final_stock,
        initial_stock_value,
        revenue,
        final_stock_value,
        revenue / SUM(revenue) OVER() AS prop_total_revenue,
        n_orders / SUM(initial_stock) OVER() AS prop_total_units_sold,
        n_orders / initial_stock AS prop_stock_sold,
        revenue / n_orders AS avg_rev_per_order
    FROM temp
    ORDER BY prop_stock_sold DESC, avg_rev_per_order DESC);

    
CREATE VIEW origin_of_revenue_loc AS (
    SELECT 
        location, 
        SUM(cost) AS revenue

    FROM
        orders
            JOIN
        users USING (user_id)
            JOIN
        products USING (product_id)
        GROUP BY location
        ORDER BY revenue DESC);


CREATE VIEW global_performance AS (
    WITH revenue AS (
        SELECT 
            SUM(p.cost) AS total_revenue,
            COUNT(*) AS units_sold
        FROM
            orders o
                JOIN
            products p USING (product_id)
    ), in_stock AS (
        SELECT 
            SUM(p.cost) AS final_stock_value,
            SUM(s.available_units) AS remaining_units
        FROM
            stock s
                LEFT JOIN
            products p USING (product_id)
    )
    SELECT 
    units_sold,
    remaining_units + units_sold AS total_units,
    total_revenue,
    final_stock_value + total_revenue AS total_stock_value
    FROM revenue
    JOIN in_stock);


CREATE VIEW orders_by_age AS (
    SELECT 
        category,
        subcategory,
        age,
        COUNT(*) AS n_orders,
        SUM(cost) AS expenses
    FROM 
        orders
            JOIN
        users USING (user_id)
            JOIN
        products USING (product_id)
    GROUP BY category, subcategory, age
    ORDER BY category, subcategory, age DESC);