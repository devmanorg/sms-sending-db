# Database layer for SMS mailing service

Database layer provides single `Database` class to interact with Redis DB.

## Database methods

Following async methods are available:


`add_sms_mailing(…)` — add to Redis all records required to represent new SMS mailing.

`get_pending_sms_list()` — Get from Redis all pending messages.

`update_sms_status_in_bulk(…)` — Receives list of tuples (sms_id, phone, status). Usage example:

```python
await db.update_sms_status_in_bulk([
    # [sms_id, phone_number, status]
    [sms_id, phone_number1, 'failed'],
    [sms_id, phone_number2, 'pending'],
    [another_sms_id, phone_number2, 'delivered'],
    # Status possible values: 'failed', 'pending' and 'delivered'
])
```

`get_sms_mailings(…)` — For each mailing in sms_ids load all data from Redis. Return list of dicts — one dict per found mailing.

`list_sms_mailings()` — Return list of sms_id for all registered SMS mailings.

## Examples

Checkout usage examples in `example.py` file. Install and run it with command:

```sh
$ pip install -r requirements.txt
$ python example.py --address="redis://..." --password="..."
```

## Check connection status

There are two options how to check connection to Redis DB is still alive. The simplest one is to set timeouts for all operations with DB. E.g. if db operation  takes more than 5 seconds than connection is supposed lost. Aioredis will try to reconnect automatically, so you can just wait or interrupt db operations manually and try again later.

Timeouts are useful only for communication with confirmations — when you send message and wait for db response. For Redis channels it is not always true. Your program can send messages to Redis channel without any income messages, so nothing can approve success of delivery to DB. In that case even detection of connection losing becomes a hard task. The best your option is to use TCP Keepalive messages — kind of ping-pong messages supported by TCP protocol. All work will be done by operating system. All you need is to configure socket properly. Check out `keepalive_example.py` code. Run example with command below:

```
$ python keepalive_example.py --address="redis://..." --password="..."
```

Wait for few seconds after script launch, than disable network connection. Exception will appear.