# Communication Standards

## Establish
Expect Response between 0.25s-0.5s
1. Client -> Server

        {  
            mode: 'establish',
            syn: true,
        }

2. Server -> Client

        {  
            mode: 'establish',
            synack: true
        }

3. Client -> Server

        {  
            mode: 'establish',
            ack: true
        }
4. Server -> Client

        {  
            mode: 'establish',
            established: true
        }

## Error Modes
A. Client Error: Action depending on the code

        {
            mode: 'error'
            code: /* specified on Codes */
        }

## Codes
| Code | Meaning |
|------|------|
| 0 | Successful |
| -1 | Server Error |

