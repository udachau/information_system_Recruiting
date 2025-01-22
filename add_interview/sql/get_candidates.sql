SELECT DISTINCT c.candidate_id, c.name 
FROM candidates c
JOIN response r ON c.user_login = r.user_login
WHERE r.status = 'откликнулся';
