SELECT o.opening_id, p.job_name, o.open_date
FROM openings o
JOIN positions p ON o.position_id = p.position_id
WHERE o.close_date IS NULL
AND o.opening_id NOT IN (
    SELECT opening_id
    FROM response
    WHERE user_login = %s AND status IN ('откликнулся', 'собеседование назначено')
)
ORDER BY o.open_date DESC
