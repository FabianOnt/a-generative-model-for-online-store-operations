CREATE TABLE Users(
    user_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    sex CHAR(1) NOT NULL,
    age TINYINT UNSIGNED NOT NULL,
    location VARCHAR(30) NOT NULL
);
CREATE TABLE Products(
    product_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    category VARCHAR(50) NOT NULL,
    subcategory VARCHAR(50) NOT NULL,
    cost DECIMAL(6, 2) NOT NULL
);
CREATE TABLE Orders(
    order_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    vendor_id BIGINT UNSIGNED NOT NULL,
    product_id BIGINT UNSIGNED NOT NULL,
    user_id BIGINT UNSIGNED NOT NULL,

    CONSTRAINT fk_orders_products
    FOREIGN KEY(product_id)
    REFERENCES Products(product_id),
    
    CONSTRAINT fk_orders_vendors
    FOREIGN KEY(vendor_id) 
    REFERENCES Vendors(vendor_id),
    
    CONSTRAINT fk_orders_user 
    FOREIGN KEY(user_id) 
    REFERENCES Users(user_id)
);
CREATE TABLE Stock(
    vendor_id BIGINT UNSIGNED NOT NULL,
    product_id BIGINT UNSIGNED NOT NULL,
    available_units INT UNSIGNED NOT NULL,

    CONSTRAINT fk_stock_vendor
    FOREIGN KEY (vendor_id)
    REFERENCES Vendors(vendor_id),

    CONSTRAINT fk_stock_product
    FOREIGN KEY(product_id) 
    REFERENCES Products(product_id)
);
CREATE TABLE Vendors(
    vendor_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    sex CHAR(1) NOT NULL,
    age TINYINT UNSIGNED NOT NULL,
    location VARCHAR(30) NOT NULL,
    stars TINYINT UNSIGNED NOT NULL
);