DROP VIEW origin_of_orders_loc;

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