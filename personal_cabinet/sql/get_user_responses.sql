SELECT r.opening_id, p.job_name, r.status
FROM response r
JOIN openings o ON r.opening_id = o.opening_id
JOIN positions p ON o.position_id = p.position_id
WHERE r.user_login = %s
