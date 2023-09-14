from enum import Enum


def replace_enums_with_values(func):
    def wrapper(*args, **kwargs):
        def replace_enums(obj):
            # Replace all Enum values with their values
            if isinstance(obj, Enum):
                return obj.value
            # Recursively replace Enum values in any iterable object
            elif isinstance(obj, (list, tuple)):
                return type(obj)(replace_enums(item) for item in obj)
            elif isinstance(obj, dict):
                return {k: replace_enums(v) for k, v in obj.items()}
            # Return the original object for all other types
            else:
                return obj

        # Replace Enum values in all arguments and keyword arguments
        args = [replace_enums(arg) for arg in args]
        kwargs = {k: replace_enums(v) for k, v in kwargs.items()}
        # Call the actual function with replaced parameters
        return func(*args, **kwargs)

    return wrapper


class TokenSort(str, Enum):
    MARKET_CAP = "market_cap"
    PERCENTAGE_PRICE_CHANGE = "last_24_hour_change_percentage"
    TOTAL_LIQUIDITY = "total_liquidity"
    COINGECKO_RANK = "coingecko_rank"


class NFTItemSort(str, Enum):
    RANK = "rank"


class ProtocolSort(str, Enum):
    NAME = "protocol_name"
    TVL = "total_tvl"


class NFTCollectionSort(str, Enum):
    VOLUME = "volume"
    MARKET_CAP = "market_cap"
    FLOOR_PRICE = "floor_price"
    LAST_24H_PRICE_CHANGE = "last_24h_change"


class TierKeys(str, Enum):
    ONE_DAY = "1d"
    ONE_WEEK = "7d"
    ONE_MONTH = "30d"
    ONE_YEAR = "365d"


class TimeseriesEventKey(Enum):
    NEW_TOKEN = "NEW_TOKEN"
    NEW_INTEGRATION = "NEW_INTEGRATION"
    PRICE_NOT_FOUND = "PRICE_NOT_FOUND"
    WALLET_CREATED = "WALLET_CREATED_EVENT"
    NEW_TOKEN_BALANCE_CHANGE = "NEW_TOKEN_BALANCE_CHANGE"
    NEW_INTEGRATION_BALANCE_CHANGE = "NEW_INTEGRATION_BALANCE_CHANGE"


class ChainKeys(str, Enum):
    FIAT = "FIAT"
    BTC = "BTC"
    LTC = "LTC"
    BTC_CASH = "BTC_CASH"
    DOGECOIN = "DOGECOIN"
    NEAR = "NEAR"
    SOLANA = "SOLANA"
    CARDANO = "CARDANO"
    SORA = "SORA"
    IOTEX = "IOTEX"
    RONIN = "RONIN"
    TOMOCHAIN = "TOMOCHAIN"
    NYX = "NYX"
    DIG = "DIG"
    ARKH = "ARKH"
    AIOZ = "AIOZ"
    JUNO = "JUNO"
    UMEE = "UMEE"
    IRIS = "IRIS"
    ODIN = "ODIN"
    MEME = "MEME"
    XPLA = "XPLA"
    MARS = "MARS"
    IDEP = "IDEP"
    OCTA = "OCTA"
    MAYA = "MAYA"
    AKASH = "AKASH"
    PLANQ = "PLANQ"
    REGEN = "REGEN"
    TERRA = "TERRA"
    CANTO = "CANTO"
    DYSON = "DYSON"
    LOGOS = "LOGOS"
    CUDOS = "CUDOS"
    CHEQD = "CHEQD"
    RIZON = "RIZON"
    ETHOS = "ETHOS"
    POINT = "POINT"
    NOMIC = "NOMIC"
    REBUS = "REBUS"
    ONOMY = "ONOMY"
    NOLUS = "NOLUS"
    LAMBDA = "LAMBDA"
    JACKAL = "JACKAL"
    STRIDE = "STRIDE"
    MYTHOS = "MYTHOS"
    BEEZEE = "BEEZEE"
    DESMOS = "DESMOS"
    COMDEX = "COMDEX"
    TGRADE = "TGRADE"
    GALAXY = "GALAXY"
    CARBON = "CARBON"
    LUMENX = "LUMENX"
    SHENTU = "SHENTU"
    AXELAR = "AXELAR"
    EMONEY = "EMONEY"
    TERRA2 = "TERRA2"
    COSMOS = "COSMOS"
    SECRET = "SECRET"
    QUASAR = "QUASAR"
    KUJIRA = "KUJIRA"
    AGORIC = "AGORIC"
    ARCHWAY = "ARCHWAY"
    EIGHTBALL = "8BALL"
    NEUTRON = "NEUTRON"
    MIGALOO = "MIGALOO"
    DECENTR = "DECENTR"
    VIDULUM = "VIDULUM"
    ECHELON = "ECHELON"
    GENESIS = "GENESIS"
    KICHAIN = "KICHAIN"
    PANACEA = "PANACEA"
    PASSAGE = "PASSAGE"
    BITSONG = "BITSONG"
    GRAVITY = "GRAVITY"
    BOSTROM = "BOSTROM"
    OSMOSIS = "OSMOSIS"
    STARGAZE = "STARGAZE"
    STARNAME = "STARNAME"
    SIFCHAIN = "SIFCHAIN"
    SENTINEL = "SENTINEL"
    LIKECOIN = "LIKECOIN"
    CRESCENT = "CRESCENT"
    CERBERUS = "CERBERUS"
    BITCANNA = "BITCANNA"
    TERITORI = "TERITORI"
    FETCHHUB = "FETCHHUB"
    IMVERSED = "IMVERSED"
    STAFIHUB = "STAFIHUB"
    BLUZELLE = "BLUZELLE"
    ACRECHAIN = "ACRECHAIN"
    OKEXCHAIN = "OKEXCHAIN"
    MICROTICK = "MICROTICK"
    BANDCHAIN = "BANDCHAIN"
    GENESISL1 = "GENESISL1"
    ORAICHAIN = "ORAICHAIN"
    THORCHAIN = "THORCHAIN"
    SOMMELIER = "SOMMELIER"
    CHIHUAHUA = "CHIHUAHUA"
    INJECTIVE = "INJECTIVE"
    IMPACTHUB = "IMPACTHUB"
    CRYPTO_ORG = "CRYPTO_ORG"
    FIRMACHAIN = "FIRMACHAIN"
    PROVENANCE = "PROVENANCE"
    LUMNETWORK = "LUMNETWORK"
    QUICKSILVER = "QUICKSILVER"
    OMNIFLIXHUB = "OMNIFLIXHUB"
    ASSETMANTLE = "ASSETMANTLE"
    PERSISTENCE = "PERSISTENCE"
    KAVA_COSMOS = "KAVA_COSMOS"
    UNIFICATION = "UNIFICATION"
    SHARELEDGER = "SHARELEDGER"
    MEDASDIGITAL = "MEDASDIGITAL"
    EVMOS_COSMOS = "EVMOS_COSMOS"
    KONSTELLATION = "KONSTELLATION"
    CHRONICNETWORK = "CHRONICNETWORK"
    COMMERCIONETWORK = "COMMERCIONETWORK"
    BSC = "BSC"
    BOBA = "BOBA"
    CELO = "CELO"
    TRON = "TRON"
    HECO = "HECO"
    BASE = "BASE"
    OASIS = "OASIS"
    GNOSIS = "GNOSIS"
    ZKSYNC = "ZKSYNC"
    CRONOS = "CRONOS"
    KLAYTN = "KLAYTN"
    NERVOS = "NERVOS"
    AURORA = "AURORA"
    FANTOM = "FANTOM"
    HARMONY = "HARMONY"
    POLYGON = "POLYGON"
    ETHEREUM = "ETHEREUM"
    OPTIMISM = "OPTIMISM"
    ARBITRUM = "ARBITRUM"
    KAVA_EVM = "KAVA_EVM"
    MOONBEAM = "MOONBEAM"
    NERVOS_GW = "NERVOS_GW"
    EVMOS_EVM = "EVMOS_EVM"
    AVALANCHE = "AVALANCHE"
    MOONRIVER = "MOONRIVER"
    CANTO_EVM = "CANTO_EVM"
    INJECTIVE_EVM = "INJECTIVE_EVM"
    OKX = "OKX"
    GATE = "GATE"
    BYBIT = "BYBIT"
    KUCOIN = "KUCOIN"
    CRYPTO = "CRYPTO"
    KRAKEN = "KRAKEN"
    BINANCE = "BINANCE"
    COINBASE = "COINBASE"
    BNB_BEACON_CHAIN = "BNB_BEACON_CHAIN"
    AVALANCHE_P_CHAIN = "AVALANCHE_P_CHAIN"


class TokenType(str, Enum):
    ADDRESS = "address"
    NATIVE = "native_token"
    DENOM = "denom"


class DebtType(str, Enum):
    FARM = "FARM"
    LOAN = "LOAN"
    SHORT = "SHORT"
    MARGIN = "MARGIN"
    MARGIN_LONG = "MARGIN_LONG"
    MARGIN_SHORT = "MARGIN_SHORT"
    LEVERAGE_POSITION = "LEVERAGE_POSITION"


class AnnualReturnType(str, Enum):
    APY = "APY"
    APR = "APR"


class OptionType(str, Enum):
    LONG_PUT = "LONG_PUT"
    LONG_CALL = "LONG_CALL"
    SHORT_PUT = "SHORT_PUT"
    SHORT_CALL = "SHORT_CALL"


class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
