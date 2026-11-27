INSERT INTO catalog_retailers (code, name, category_code, website_url, active)
VALUES ('bulmag', 'BulMag', 'groceries', 'https://bulmag.org/', true)
ON CONFLICT (code) DO NOTHING;
