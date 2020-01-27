import asyncio
import aioredis
import argparse
import socket


def set_keepalive_linux(sock, after_idle_sec=1, interval_sec=3, max_fails=5):
    """Set TCP keepalive on an open socket.

    It activates after 1 second (after_idle_sec) of idleness,
    then sends a keepalive ping once every 3 seconds (interval_sec),
    and closes the connection after 5 failed ping (max_fails), or 15 seconds
    """
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, after_idle_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, interval_sec)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, max_fails)


class CustomRedisConnection(aioredis.connection.RedisConnection):
    def __init__(self, reader, writer, *args, **kwargs):
        super().__init__(reader, writer, *args, **kwargs)
        # reader and writer sockets are the same, so should modify one of them
        reader_socket = reader._transport.get_extra_info('socket')
        set_keepalive_linux(reader_socket, after_idle_sec=1, interval_sec=1, max_fails=3)


def create_argparser():
    parser = argparse.ArgumentParser(description='Redis database usage example')
    parser.add_argument('--address', action='store', dest='redis_uri', help='Redis URI')
    parser.add_argument('--password', action='store', dest='redis_password', help='Redis db password')

    return parser


async def main():
    parser = create_argparser()
    args = parser.parse_args()

    redis = await aioredis.create_redis_pool(
        args.redis_uri,
        password=args.redis_password,
        encoding='utf-8',
        connection_cls=CustomRedisConnection
    )

    try:

        async def send():
            while True:
                await asyncio.sleep(2)
                await redis.publish('updates', 'Empty message')

        async def listen():
            *_, channel = await redis.subscribe('updates')

            while True:
                raw_message = await channel.get()

                if not raw_message:
                    raise ConnectionError('Connection was lost')

                message = raw_message.decode('utf-8')
                print('Got message:', message)

        await asyncio.gather(
            send(),
            listen(),
        )

    finally:
        redis.close()
        await redis.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())
