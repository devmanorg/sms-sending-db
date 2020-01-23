# Database layer for SMS mailing service

Database layer provides single `Database` class to interact with Redis DB.

## Database methods

Following async methods are available:


`add_sms_mailing(…)` — add to Redis all records required to represent new SMS mailing.

`get_pending_sms_list()` — Get from Redis all pending messages.

`update_sms_status_in_bulk(…)` — Receives list of tuples (sms_id, phone, status).

`get_sms_mailing(…)` — Load from Redis all data about mailing with specified sms_id, returns dict.

`list_sms_mailings()` — Return list of sms_id for all registered SMS mailings.

## Examples

Checkout usage examples in `example.py` file. Install and run it woth command:

```sh
$ pip install -r requirements.txt
$ python example.py --address="redis://..." --password="..."
```
