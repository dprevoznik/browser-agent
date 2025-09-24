import asyncio
import typing as t
from os import environ as env
from pathlib import Path

import anyio
import orjson

from lib.asyncio import asyncify

BUCKET = env.get("S3_BUCKET")
ENABLED = bool(BUCKET)
PRESIGNED_URL_EXPIRES_IN = int(env.get("PRESIGNED_URL_EXPIRES_IN", 24 * 60 * 60))

client = None
if ENABLED:
    import boto3
    from botocore.client import Config

    client = boto3.client(
        service_name="s3",
        endpoint_url=env["S3_ENDPOINT_URL"],
        aws_access_key_id=env["S3_ACCESS_KEY_ID"],
        aws_secret_access_key=env["S3_SECRET_ACCESS_KEY"],
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


@asyncify
def upload_file(file: anyio.Path | Path | str, key: str) -> str:
    if not client:
        raise ValueError("S3_BUCKET is not set")

    client.upload_file(
        Bucket=BUCKET,
        Filename=str(file),
        Key=key,
    )
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=PRESIGNED_URL_EXPIRES_IN,
    )


@asyncify
def upload_json(data: t.Any, key: str) -> str:
    if not client:
        raise ValueError("S3_BUCKET is not set")

    client.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=orjson.dumps(data, option=orjson.OPT_INDENT_2),
    )
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET, "Key": key},
        ExpiresIn=PRESIGNED_URL_EXPIRES_IN,
    )


async def upload_files(
    dir: str,
    files: t.AsyncIterator[anyio.Path | Path | str],
) -> dict[str, str]:
    paths = [Path(f) async for f in files]
    names = [f.name for f in paths]

    if not client:
        return {n: str(f) for n, f in zip(names, paths)}

    object_keys = [f"{dir}/{n}" for n in names]
    presigned_urls = await asyncio.gather(
        *[upload_file(f, k) for f, k in zip(paths, object_keys)]
    )
    return dict(zip(names, presigned_urls))
