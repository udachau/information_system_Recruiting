SELECT DISTINCT o.opening_id, p.job_name 
FROM openings o
JOIN positions p ON o.position_id = p.position_id
JOIN response r ON o.opening_id = r.opening_id
WHERE r.status = 'откликнулся' AND r.user_login = (
    SELECT user_login FROM candidates WHERE candidate_id = %s
);
