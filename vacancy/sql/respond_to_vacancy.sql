INSERT INTO response (user_login, opening_id, status)
VALUES (%s, %s, 'откликнулся')
ON DUPLICATE KEY UPDATE status = 'откликнулся'
