# easyssl


### Functions
| Module | Function            | Use Case                                               |
|--------|---------------------|--------------------------------------------------------|
| ssl    | to simplify openssl | Simple en/de-cryption implement to build your own app. |
| ca     | to simplify x.509   | Maintain your own CA and sign crt on demand easily.    |



### Encryption
```python
import json
import datetime
import socket
from easyssl import ssl


hostname = socket.gethostname()
time_stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
k = ssl.Key()
k.load_pubkey()

plain_text = hostname + '__-__' + time_stamp
plain_text = json.dumps(
    {
        'k1': 'v1',
        'k2': 'v2',
        'k3': 'v3',
    }
)

k.encrypt(plain_text=plain_text)

```
### Decryption

```python
import json
import datetime
import socket
from easyssl import ssl

k = ssl.Key()
k.load_prikey()


encrypted_text = 'F/IicdulrsDfrTsrR7ainjM23+kV8/7Li7pbLb/Zn6VGJD4Y9Nz18f4rb7WCW7di1TIzr+qTpY8nAI4DbphCC3FfGrIYgoBY0pCuzOng79R/Rrpgm4VIHbiGdssP7W1ihsksgd4ttcG9KR7GfJeeGaOlK5w1vl/9inveuUB8hQA4bhmrpEK/+HmYxXPtVadW3ZqRNf8wyGJwED63d1U7N7iO6Q5Rph2t1hmVKKRZ9uTeeAno1oo2a2N6xQ1IiwUkqsjggYkiLbCjm28/lony/2QtqvSdEzOmHzlTFeamcZqN5zxrkh2ozq07kJo6xibpN0EMSSgBZUaTLG2WtGbvoA=='
k.decrypt(encrypted_text)

```

