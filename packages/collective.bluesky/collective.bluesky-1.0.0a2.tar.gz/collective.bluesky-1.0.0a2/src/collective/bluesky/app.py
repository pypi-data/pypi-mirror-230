from collective.bluesky import DEFAULT_HOST
from collective.bluesky import DEFAULT_PROTOCOL
from collective.bluesky import HANDLE_IDENTIFIER
from collective.bluesky import logger
from collective.bluesky.interfaces import BlueskyBlob
from collective.bluesky.interfaces import IBlueskyApp
from datetime import datetime
from datetime import timezone
from threading import Thread
from typing import Dict
from typing import List
from zope.interface import implementer

import re
import requests


USER_AGENT = "collective.bluesky"


def _parse_mentions(text: str) -> List[Dict]:
    spans = []
    text_bytes = text.encode("UTF-8")
    for m in re.finditer(HANDLE_IDENTIFIER, text_bytes):
        spans.append(
            {
                "start": m.start(1),
                "end": m.end(1),
                "handle": m.group(1)[1:].decode("UTF-8"),
            }
        )
    return spans


def _parse_urls(text: str) -> List[Dict]:
    spans = []
    # partial/naive URL regex based on: https://stackoverflow.com/a/3809435
    # tweaked to disallow some training punctuation
    url_regex = rb"[$|\W](https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*[-a-zA-Z0-9@%_\+~#//=])?)"
    text_bytes = text.encode("UTF-8")
    for m in re.finditer(url_regex, text_bytes):
        spans.append(
            {
                "start": m.start(1),
                "end": m.end(1),
                "url": m.group(1).decode("UTF-8"),
            }
        )
    return spans


def _parse_facets(text: str, base_url: str) -> List[Dict]:
    facets = []
    for m in _parse_mentions(text):
        resp = requests.get(
            f"{base_url}/com.atproto.identity.resolveHandle",
            params={"handle": m["handle"]},
        )
        # If the handle can't be resolved, just skip it!
        # It will be rendered as text in the post instead of a link
        if resp.status_code == 400:
            continue
        did = resp.json()["did"]
        facets.append(
            {
                "index": {
                    "byteStart": m["start"],
                    "byteEnd": m["end"],
                },
                "features": [{"$type": "app.bsky.richtext.facet#mention", "did": did}],
            }
        )
    for u in _parse_urls(text):
        facets.append(
            {
                "index": {
                    "byteStart": u["start"],
                    "byteEnd": u["end"],
                },
                "features": [
                    {
                        "$type": "app.bsky.richtext.facet#link",
                        # NOTE: URI ("I") not URL ("L")
                        "uri": u["url"],
                    }
                ],
            }
        )
    return facets


def _payload(text: str, blobs: list, language: str, base_url: str):
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload = {
        "$type": "app.bsky.feed.post",
        "text": text,
        "blobs": blobs if blobs else [],
        "langs": [
            language if language else "en",
        ],
        "createdAt": now,
    }
    facets = _parse_facets(text, base_url)
    if facets:
        payload["facets"] = facets
    return payload


@implementer(IBlueskyApp)
class BlueskyApp:
    """Bluesky App"""

    _base_url: str
    name: str
    handle: str
    app_password: str
    host: str

    def __init__(
        self,
        handle: str,
        app_password: str,
        host: str = DEFAULT_HOST,
        protocol: str = DEFAULT_PROTOCOL,
    ):
        self.host = host
        self.handle = handle
        self.name = f"{self.handle}-{self.host}"
        self.app_password = app_password
        self._base_url = f"{protocol}://{host}/xrpc"
        self.thread_name = f"BlueskyApp-Thread-{host}-{handle}"

    def status_post(
        self,
        text: str,
        blobs: List[BlueskyBlob] = None,
        language: str = "",
    ) -> Thread:
        """Post a status to Bluesky (using thread)."""
        payload = _payload(text, blobs, language, self._base_url)
        name = self.thread_name
        thread = Thread(
            target=self._status_post,
            name=name,
            kwargs=payload,
        )
        thread.start()
        return thread

    def _authenticate(self) -> tuple:
        """Authenticate an return the token and the did."""
        response = requests.post(
            f"{self._base_url}/com.atproto.server.createSession",
            json={"identifier": self.handle, "password": self.app_password},
        )
        if response.status_code < 299:
            data = response.json()
            return (data["accessJwt"], data["did"])
        else:
            logger.warning(
                f"Authentication error {response.status_code} {response.content}"
            )
            return tuple()

    def _upload_blob(self, session, blob: BlueskyBlob) -> dict:
        response = session.post(
            f"{self._base_url}/com.atproto.repo.uploadBlob",
            headers={"Content-Type": blob.mime_type},
            data=blob.data,
        )
        data = response.json()
        blob_data = data["blob"]
        return {"alt": blob.caption, "image": blob_data}

    def _status_post(self, **payload) -> dict:
        """Post a status to a Bluesky instance and return the response."""
        authentication = self._authenticate()
        if not authentication:
            return {}
        token, did = authentication
        session = requests.Session()
        session.headers.update({"Authorization": f"Bearer {token}"})
        blobs = []
        for blob in payload.get("blobs", []):
            item = self._upload_blob(session, blob)
            blobs.append(item)
        # Prepare payload for post
        del payload["blobs"]
        if blobs:
            payload["embed"] = {"$type": "app.bsky.embed.images", "images": blobs}
        response = session.post(
            f"{self._base_url}/com.atproto.repo.createRecord",
            json={
                "repo": did,
                "collection": "app.bsky.feed.post",
                "record": payload,
            },
        )
        data = response.json()
        uri = data["uri"]
        cid = data["cid"]
        logger.info(f"Post submitted. URI: {uri}| CID: {cid}")
        return data
