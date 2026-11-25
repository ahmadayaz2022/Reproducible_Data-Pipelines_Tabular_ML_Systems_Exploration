-- Question: which complaint categories breach the 72-hour SLA most often?
SELECT category,
       COUNT(*)                          AS n_requests,
       ROUND(AVG(resolution_hours), 1)   AS avg_hours,
       ROUND(100.0 * AVG(sla_breached), 1) AS breach_pct
FROM requests
GROUP BY category
ORDER BY breach_pct DESC;
