# openai-jslt-spike
This is an spike for using openai apis in generating jslt formulas


To install the dependencies
```pip3 install -r requirements.txt```
To start the server

```python -m main```


Curl Request to trigger TOKEN HEAVY request
```
 curl -X POST "http://127.0.0.1:8000/generate-jslt-token-heavy" \
     -H "Content-Type: application/json" \
     -d '{"message": "map the field officePhone to TELEPHONE_OFFICE_23"}'

```
Output
```
{"jslt":"{\n  \"TELEPHONE_OFFICE_23\" : .officePhone\n}"}
```


Preferred Curl for saving tokens
```
curl -X POST "http://127.0.0.1:8000/generate-jslt" \
     -H "Content-Type: application/json" \
     -d '{"message": "map the field officePhone to TELEPHONE_OFFICE_23"}'

```
Output
```
{"response":"\"officePhone\" : ifEmptyMakeNull(.TELEPHONE_OFFICE_23)"}%
```


Pretrain with Assistant ID context and Set these keys in env variable
```
JSLT_ASSISTANT
JSLT_OPENAI_THREAD_ID
OPENAI_API_KEY
```