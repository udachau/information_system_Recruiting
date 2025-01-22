UPDATE response
SET status = 'отменено'
WHERE user_login = %s AND opening_id = %s
