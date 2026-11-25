# Raw data schema

File: `service_requests_raw.csv` | rows: 8240 | columns: 12

| column | pandas type | missing | missing % | unique | example values | units / allowed values (fill in) |
|---|---|---|---|---|---|---|
| request_id | int64 | 0 | 0.0 | 8000 | 104402, 104568, 101282 |  |
| created_at | str | 0 | 0.0 | 7811 | 2025-05-27 22:50:00, 2025-04-15 02:57:00, 2025-08-04 22:16:00 |  |
| closed_at | str | 513 | 6.2 | 7363 | 2025-05-31 06:36:03, 2025-04-16 07:53:35, 2025-08-10 18:07:59 |  |
| agency | str | 0 | 0.0 | 8 | lda, wasa, pdma |  |
| category | str | 0 | 0.0 | 24 | street light, Water Leak, pothole |  |
| district | str | 676 | 8.2 | 5 | central, north, east |  |
| channel | str | 375 | 4.6 | 4 | phone, walk-in, app |  |
| priority | str | 0 | 0.0 | 3 | medium, high, low |  |
| latitude | float64 | 296 | 3.6 | 7616 | 31.467185961518453, 31.308278104181248, 31.812564290393905 |  |
| longitude | float64 | 337 | 4.1 | 7673 | 74.41317495324277, 74.31090674762233, 74.22843077307184 |  |
| description_len | float64 | 240 | 2.9 | 596 | 59.0, 51.0, 203.0 |  |
| num_updates | float64 | 0 | 0.0 | 10 | 2.0, 4.0, 0.0 |  |

Exact duplicate rows: 240
