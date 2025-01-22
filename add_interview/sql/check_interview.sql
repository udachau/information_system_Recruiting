SELECT COUNT(*) 
FROM interviews i
JOIN interview_details id ON i.interview_id = id.interview_id
WHERE i.date = %s AND i.employee_id = %s AND i.opening_id = %s AND id.candidate_id = %s;
