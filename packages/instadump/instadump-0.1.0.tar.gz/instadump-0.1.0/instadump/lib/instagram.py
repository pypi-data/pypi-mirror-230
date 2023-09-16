import json
import logging
import os
from datetime import datetime, timezone
from typing import Callable, Iterable, Optional

import httpx
from dateutil.parser import parse as parse_datetime

from instadump.lib.config import ConfigDict
from instadump.lib.utils import parse_period

logger = logging.getLogger(__name__)


class InstagramClient:
    API_URL = "https://graph.facebook.com/v17.0"

    def __init__(self, connected_id: str, access_token: str) -> None:
        self.connected_id = connected_id
        self.access_token = access_token
        self.session = httpx.Client()

    def get_posts(
        self,
        username: str,
        max_items: int = None,
        limit: int = 100,
        since_datetime: datetime = None,
    ) -> dict:
        """Get posts of a business user"""
        posts = []
        total = 0

        if since_datetime:
            logger.info(f"[{username}] fetching posts since {since_datetime}")

        user_fields = (
            f"username({username})",
            (
                "id",
                "name",
                (
                    "media%(cursor)s",
                    (
                        "id",
                        "media_url",
                        "media_type",
                        "media_product_type",
                        "permalink",
                        "caption",
                        "comments_count",
                        "like_count",
                        "timestamp",
                    ),
                ),
            ),
        )

        for data in self.get_paginated_results(
            url=f"{self.API_URL}/{self.connected_id}",
            fields=f"business_discovery.{self.parse_fields(user_fields)}",
            max_items=max_items,
            limit=limit,
            paging_getter=lambda data: data["business_discovery"]["media"].get(
                "paging"
            ),
        ):
            for post in data["business_discovery"]["media"]["data"]:
                # Reach max items
                if max_items and total > max_items:
                    return posts

                # Reach since datetime
                if (
                    since_datetime
                    and parse_datetime(post["timestamp"]) < since_datetime
                ):
                    return posts

                # Append post
                posts.append(post)
                total += 1

        return posts

    def get_paginated_results(
        self,
        url: str,
        fields: str,
        max_items: int,
        limit: int,
        paging_getter: Callable,
    ) -> Iterable:
        after = None

        while True:
            # Build paging
            if max_items:
                limit = min(limit, max_items)

            cursor = f".limit({limit})"

            if after:
                cursor += f".after({after})"

            # Request
            response = self.session.get(
                url,
                params={
                    "fields": fields % {"cursor": cursor},
                    "access_token": self.access_token,
                },
            )
            response.raise_for_status()
            data = response.json()

            if not data:
                # No more data
                break

            yield data

            # Update Paging
            if paging := paging_getter(data):
                after = paging["cursors"].get("after")

            logger.debug(after)

            if not after:
                # No more posts
                break

    def parse_fields(self, value: tuple) -> str:
        if isinstance(value, str):
            return value
        elif isinstance(value, tuple):
            key, fields = value
            fields_str = ",".join(self.parse_fields(v) for v in fields)
            return "%s{%s}" % (key, fields_str)


class Crawler:
    def __init__(self, client: InstagramClient, config: ConfigDict) -> None:
        self.client = client
        self.config = config

    def get_username_file_path(self, username: str) -> str:
        output_dir = self.config.get("output_dir", "output")
        filename = "_".join(
            [
                username,
                datetime.now().strftime("%Y_%m_%d_%H%M%S"),
            ]
        )
        return os.path.join(output_dir, f"{filename}.json")

    def calculate_since_datetime(self) -> Optional[datetime]:
        if period := self.config.get("period"):
            return datetime.now(timezone.utc) - parse_period(period)

    def dump(self, username: str) -> None:
        """Dump posts to local files"""
        posts = self.client.get_posts(
            username,
            max_items=self.config.get("max_posts_per_account", None),
            since_datetime=self.calculate_since_datetime(),
        )
        logger.info(f"[{username}] got {len(posts)} posts")

        path = self.get_username_file_path(username)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        with open(path, "w") as f:
            json.dump(posts, f, indent=2)
            logger.info(f"{path} saved.")

    def run(self) -> None:
        """Run crawler"""
        for username in self.config["accounts"]:
            logger.info(f"[{username}] crawling...")
            try:
                self.dump(username)
            except httpx.HTTPError as e:
                logger.error(f"[{username}] {e}\n{e.response.text}")
