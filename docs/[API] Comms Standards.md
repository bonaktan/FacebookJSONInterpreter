# Communication Standards

## Establishing Comms
Expect Response: ASAP
Server-Client:
{}


## Codes
| Code | Meaning |
|------|------|
| 0 | Successful |
| -100 | Server Error: Ambiguous but Implemented* |
| -200 | Client Error: Ambiguous but Implemented* |
| -201 | Client Error: Path submitted using requestType-path Invalid or does not exist |
| -401 | Server Rare Error: A FacebookData already parsed |


* Unimplemented errors shall always return a 500 Internal Server Error