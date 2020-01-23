import asyncio
import aioredis
import argparse

from db import Database


def create_argparser():
    parser = argparse.ArgumentParser(description='Redis database usage example')
    parser.add_argument('--address', action='store', dest='redis_uri', help='Redis URI')
    parser.add_argument('--password', action='store', dest='redis_password', help='Redis db password')

    return parser


async def main():
    parser = create_argparser()
    args = parser.parse_args()

    redis = await aioredis.create_redis_pool(args.redis_uri, password=args.redis_password, encoding='utf-8')

    try:

        db = Database(redis)

        sms_id = '99'

        phones = [
            '+7 999 519 05 57',
            '112',
        ]
        text = 'Вечером будет шторм!'

        await db.add_sms_mailing(sms_id, phones, text)

        value = await redis.get(f'sms_mailing_{sms_id}')
        print('Got value', value)

        pending_sms_list = await db.get_pending_sms_list()
        print('pending:')
        print(pending_sms_list)

        await db.update_sms_status_in_bulk([
            ['99', '112', 'failed'],
        ])

        pending_sms_list = await db.get_pending_sms_list()
        print('pending:')
        print(pending_sms_list)

        sms_mailing = await db.get_sms_mailing('99')
        print('sms_mailing')
        print(sms_mailing)

        async def send():
            while True:
                await asyncio.sleep(1)
                await redis.publish('updates', sms_id)

        async def listen():
            *_, channel = await redis.subscribe('updates')
            async for raw_message in channel.iter():
                message = raw_message.decode('utf-8')
                print('Got message:', message)

        await asyncio.gather(
            send(),
            listen()
        )

    finally:
        redis.close()
        await redis.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
