from datetime import datetime, timedelta
from urllib.parse import urlencode

import pytz


class CampaignDTO:
    def __init__(
        self,
        blockchain: str,
        parlamint_id: str,
        collection_id: str,
        name: str,
        description: str,
        price: int,
        supply: int,
        pricing: str,
        limit: int,
        start_at: datetime,
        explorer_url: str,
        marketplace_url: str,
        rarity_chart_url: str,
        animated_cover_url: str,
    ):
        self.blockchain: str = blockchain

        self.parlamint_id: str = parlamint_id.lower()
        self.collection_id: str = collection_id.lower() if collection_id else None

        self.name: str = name
        self.description: str = description
        self.price: int = price
        self.supply: int = supply
        self.pricing: str = pricing.replace("<br>", "\n").strip()
        self.limit: int = limit
        self.start_at: datetime = start_at

        self.explorer_url: str = explorer_url
        self.marketplace_url: str = marketplace_url
        self.rarity_chart_url: str = rarity_chart_url
        self.animated_cover_url: str = animated_cover_url

    @property
    def new(self) -> bool:
        now = datetime.utcnow().replace(tzinfo=pytz.UTC)

        return self.start_at > now

    @property
    def timedelta(self) -> str:
        if not self.start_at:
            return None

        now = datetime.utcnow().replace(tzinfo=pytz.UTC)

        if self.start_at > now:
            td = self.start_at - now
        else:
            td = now - self.start_at

        days = td.days
        hours = td.seconds // 3600
        minutes = (td.seconds // 60) % 60

        if days == hours == minutes == 0:
            return "NOW!!"

        items = []

        if days:
            items += [
                "{days} day{s}".format(
                    days=abs(days),
                    s="" if days == 1 else "s",
                )
            ]

        if days < 2:
            if days and (hours or minutes):
                items += ["and"]

            if hours or minutes:
                items += [
                    "{hours:02d}:{minutes:02d} hs".format(
                        hours=hours,
                        minutes=minutes,
                    )
                ]

        if self.start_at < now:
            items += ["ago"]

        return " ".join(items)

    def googlecalendar_url(self) -> str:  # https://www.labnol.org/calendar/
        start = self.start_at
        end = start + timedelta(minutes=30)

        start_str = "{year}{month:02}{day:02}T{hour:02}{minute:02}00Z".format(
            year=start.year,
            month=start.month,
            day=start.day,
            hour=start.hour,
            minute=start.minute,
        )

        end_str = "{year}{month:02}{day:02}T{hour:02}{minute:02}00Z".format(
            year=end.year,
            month=end.month,
            day=end.day,
            hour=end.hour,
            minute=end.minute,
        )

        params = {
            "action": "TEMPLATE",
            "location": self.parlamint_url,
            "text": f"BOOK.IO Mint: {self.name}",
            "dates": f"{start_str}/{end_str}",
        }

        return f"https://calendar.google.com/calendar/render?{urlencode(params)}"

    @property
    def parlamint_url(self) -> str:
        return f"https://app.book.io/parlamint/campaigns/{self.parlamint_id}"

    def __repr__(self):
        return f"{self.name} ({self.collection_id})"
