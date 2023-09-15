import json
import logging
from datetime import datetime
from typing import Iterable

import pytz

from fetchfox.apis import bookio
from fetchfox.apis.evm import moralisio, ensideascom, openseaio
from fetchfox.blockchains.base import Blockchain
from fetchfox.constants.blockchains import ETHEREUM, POLYGON
from fetchfox.constants.marketplaces import OPENSEA_IO
from fetchfox.dtos import AssetDTO, CampaignDTO, FloorDTO, HoldingDTO, ListingDTO, SaleDTO
from fetchfox.helpers import formatters
from . import utils

logger = logging.getLogger(__name__)


class Evm(Blockchain):
    def __init__(self, name: str, currency: str, logo: str, moralisio_api_key: str = None, openseaio_api_key: str = None):
        super().__init__(name, currency, logo)

        self.moralisio_api_key: str = moralisio_api_key
        self.openseaio_api_key: str = openseaio_api_key

    def check_collection_id(self, collection_id: str):
        if not utils.is_address(collection_id):
            raise ValueError(f"{collection_id} is not a valid {self.name} contract address")

    def check_asset_id(self, asset_id: str):
        if not utils.is_asset_id(asset_id):
            raise ValueError(f"{asset_id} is not a valid {self.name} asset id")

    def check_wallet(self, wallet: str):
        if not utils.is_wallet(wallet):
            raise ValueError(f"{wallet} is not a valid {self.name} address or ens domain")

    def get_wallet_name(self, wallet: str) -> str:
        if utils.is_ens_domain(wallet):
            return wallet

        if utils.is_address(wallet):
            return ensideascom.get_ens_domain(wallet)

        return None

    def resolve_wallet_name(self, wallet_name: str) -> str:
        if utils.is_ens_domain(wallet_name):
            return ensideascom.resolve_ens_domain(wallet_name)

        return None

    def get_assets(self, collection_id: str, fetch_metadata: bool = True, *args, **kwargs) -> Iterable[AssetDTO]:
        self.check_collection_id(collection_id)

        if fetch_metadata:
            asset_id = -1

            while True:
                try:
                    asset_id += 1

                    yield self.get_asset(
                        collection_id=collection_id,
                        asset_id=str(asset_id),
                    )
                except ValueError:
                    raise
                except:
                    break
        else:
            assets = moralisio.get_assets(
                contract_address=collection_id,
                blockchain=self.name,
                api_key=self.moralisio_api_key,
            )

            for asset_id in assets:
                yield AssetDTO(
                    collection_id=collection_id,
                    asset_id=asset_id,
                    metadata={},
                )

    def get_asset(self, collection_id: str, asset_id: str, *args, **kwargs) -> AssetDTO:
        self.check_collection_id(collection_id)
        self.check_asset_id(asset_id)

        data = moralisio.get_asset_data(
            contract_address=collection_id,
            asset_id=asset_id,
            blockchain=self.name,
            api_key=self.moralisio_api_key,
        )

        metadata = json.loads(data["metadata"])
        metadata["attributes"].update(metadata["extraAttributes"])

        return AssetDTO(
            collection_id=collection_id,
            asset_id=asset_id,
            metadata=metadata,
        )

    def get_campaigns(self) -> Iterable[CampaignDTO]:
        for campaign in bookio.campaigns():
            if campaign["blockchain"] != "evm":
                continue

            if self.name == ETHEREUM:
                network = "mainnet"
            else:
                network = self.name

            if campaign["network"] != network:
                continue

            landing = campaign["landing"]
            platform = campaign["platform"]
            start_at = campaign["start_at"]

            collection_id = platform["ThirdWeb"]["contract_address"]

            yield CampaignDTO(
                blockchain=self.name,
                parlamint_id=campaign["id"],
                collection_id=collection_id,
                name=campaign["display_name"],
                description=campaign["landing"]["opener"],
                price=landing["price"],
                supply=campaign["total_deas"],
                pricing=landing["price_description"],
                limit=campaign["max_quantity"],
                start_at=formatters.timestamp(start_at["start_at"]) if start_at["type"] == "at" else None,
                explorer_url=self.explorer_url(collection_id),
                marketplace_url=self.marketplace_url(collection_id=collection_id),
                rarity_chart_url=landing["rarity_chart_url"],
                animated_cover_url=landing["animated_cover_url"],
            )

    def get_holdings(self, wallet: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        self.check_wallet(wallet)

        if utils.is_ens_domain(wallet):
            wallet = ensideascom.resolve_ens_domain(wallet)

        holdings = moralisio.get_holdings(
            wallet,
            blockchain=self.name,
            api_key=self.moralisio_api_key,
        )

        for token in holdings:
            contract_address = token["token_address"]
            asset_id = token["token_id"]
            quantity = int(token["amount"])

            yield HoldingDTO(
                collection_id=contract_address,
                asset_id=asset_id,
                address=wallet,
                quantity=quantity,
            )

    def get_snapshot(self, collection_id: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        self.check_collection_id(collection_id)

        assets = moralisio.get_owners(
            collection_id,
            blockchain=self.name,
            api_key=self.moralisio_api_key,
        )

        for asset in assets:
            yield HoldingDTO(
                collection_id=asset["contract_address"],
                asset_id=asset["asset_id"],
                address=asset["address"],
                quantity=asset["amount"],
            )

    def get_owners(self, collection_id: str, asset_id: str, *args, **kwargs) -> Iterable[HoldingDTO]:
        self.check_collection_id(collection_id)
        self.check_asset_id(asset_id)

        asset = moralisio.get_owner(
            collection_id,
            asset_id=asset_id,
            blockchain=self.name,
            api_key=self.moralisio_api_key,
        )

        yield HoldingDTO(
            collection_id=asset["contract_address"],
            asset_id=asset["asset_id"],
            address=asset["address"],
            quantity=asset["amount"],
        )

    def get_listings(self, collection_id: str, slug: str = None, *args, **kwargs) -> Iterable[ListingDTO]:
        self.check_collection_id(collection_id)

        listings = openseaio.get_listings(
            collection_id,
            api_key=self.openseaio_api_key,
            slug=slug,
        )

        for listing in listings:
            protocol_data = listing["protocol_data"]
            parameters = protocol_data["parameters"]

            price = listing["price"]["current"]

            asset_ids = []
            asset_names = []

            for offer in parameters["offer"]:
                if offer["token"].lower() != collection_id.lower():
                    continue

                asset_ids.append(offer["identifierOrCriteria"])
                asset_names.append("")

            if listing.get("eventTimestamp"):
                listed_at = datetime.utcfromtimestamp(parameters["startTime"])
            else:
                listed_at = datetime.now(tz=pytz.utc)

            if self.name == POLYGON:
                marketplace_url = f"https://opensea.io/assets/matic/{collection_id}/{asset_ids[0]}"
            else:
                marketplace_url = f"https://opensea.io/assets/ethereum/{collection_id}/{asset_ids[0]}"

            yield ListingDTO(
                identifier=listing["order_hash"],
                collection_id=collection_id,
                asset_ids=asset_ids,
                asset_names=asset_names,
                listing_id=listing["order_hash"],
                marketplace=OPENSEA_IO,
                price=float(int(price["value"]) / 10 ** price["decimals"]),
                currency=price["currency"].replace("WETH", "ETH"),
                listed_at=listed_at,
                listed_by=parameters["offerer"],
                tx_hash=listing["order_hash"],
                marketplace_url=marketplace_url,
            )

    def get_floor(self, collection_id: str, *args, **kwargs) -> FloorDTO:
        self.check_collection_id(collection_id)

        floor = None
        count = 0

        for listing in self.get_listings(collection_id):
            count += 1

            if floor is None:
                floor = listing
            elif listing.usd < floor.usd:
                floor = listing

        return FloorDTO(
            listing=floor,
            listing_count=count,
        )

    def get_sales(self, collection_id: str, slug: str = None, *args, **kwargs) -> Iterable[SaleDTO]:
        self.check_collection_id(collection_id)

        sales = openseaio.get_sales(
            collection_id,
            api_key=self.openseaio_api_key,
            slug=slug,
        )

        for sale in sales:
            tx_hash = sale["transaction"]["transaction_hash"]

            asset = sale["asset"]
            asset_id = asset["token_id"]
            asset_name = asset["name"]

            if sale.get("event_timestamp"):
                confirmed_at = datetime.fromisoformat(sale["event_timestamp"] + "+00:00")
            else:
                confirmed_at = datetime.now(tz=pytz.utc)

            if self.name == POLYGON:
                marketplace_url = f"https://opensea.io/assets/matic/{collection_id}/{asset_id}"
                explorer_url = f"https://polygonscan.com/tx/{tx_hash}"
            else:
                marketplace_url = f"https://opensea.io/assets/ethereum/{collection_id}/{asset_id}"
                explorer_url = f"https://etherscan.io/tx/{tx_hash}"

            yield SaleDTO(
                identifier=sale["id"],
                collection_id=collection_id,
                asset_ids=[asset_id],
                asset_names=[asset_name],
                tx_hash=tx_hash,
                marketplace=OPENSEA_IO,
                price=float(int(sale["total_price"]) / 10 ** sale["payment_token"]["decimals"]),
                currency=sale["payment_token"]["symbol"].replace("WETH", "ETH"),
                confirmed_at=confirmed_at,
                sold_by=sale["seller"]["address"],
                bought_by=sale["winner_account"]["address"],
                sale_id=sale["id"],
                marketplace_url=marketplace_url,
                explorer_url=explorer_url,
            )
