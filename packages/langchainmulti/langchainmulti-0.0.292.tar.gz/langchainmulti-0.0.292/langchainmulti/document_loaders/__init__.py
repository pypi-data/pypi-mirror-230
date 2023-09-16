"""**Document Loaders**  are classes to load Documents.

**Document Loaders** are usually used to load a lot of Documents in a single run.

**Class hierarchy:**

.. code-block::

    BaseLoader --> <name>Loader  # Examples: TextLoader, UnstructuredFileLoader

**Main helpers:**

.. code-block::

    Document, <name>TextSplitter
"""

from langchainmulti.document_loaders.acreom import AcreomLoader
from langchainmulti.document_loaders.airbyte import (
    AirbyteCDKLoader,
    AirbyteGongLoader,
    AirbyteHubspotLoader,
    AirbyteSalesforceLoader,
    AirbyteShopifyLoader,
    AirbyteStripeLoader,
    AirbyteTypeformLoader,
    AirbyteZendeskSupportLoader,
)
from langchainmulti.document_loaders.airbyte_json import AirbyteJSONLoader
from langchainmulti.document_loaders.airtable import AirtableLoader
from langchainmulti.document_loaders.apify_dataset import ApifyDatasetLoader
from langchainmulti.document_loaders.arcgis_loader import ArcGISLoader
from langchainmulti.document_loaders.arxiv import ArxivLoader
from langchainmulti.document_loaders.assemblyai import AssemblyAIAudioTranscriptLoader
from langchainmulti.document_loaders.async_html import AsyncHtmlLoader
from langchainmulti.document_loaders.azlyrics import AZLyricsLoader
from langchainmulti.document_loaders.azure_blob_storage_container import (
    AzureBlobStorageContainerLoader,
)
from langchainmulti.document_loaders.azure_blob_storage_file import (
    AzureBlobStorageFileLoader,
)
from langchainmulti.document_loaders.bibtex import BibtexLoader
from langchainmulti.document_loaders.bigquery import BigQueryLoader
from langchainmulti.document_loaders.bilibili import BiliBiliLoader
from langchainmulti.document_loaders.blackboard import BlackboardLoader
from langchainmulti.document_loaders.blob_loaders import (
    Blob,
    BlobLoader,
    FileSystemBlobLoader,
    YoutubeAudioLoader,
)
from langchainmulti.document_loaders.blockchain import BlockchainDocumentLoader
from langchainmulti.document_loaders.brave_search import BraveSearchLoader
from langchainmulti.document_loaders.browserless import BrowserlessLoader
from langchainmulti.document_loaders.chatgpt import ChatGPTLoader
from langchainmulti.document_loaders.chromium import AsyncChromiumLoader
from langchainmulti.document_loaders.college_confidential import CollegeConfidentialLoader
from langchainmulti.document_loaders.concurrent import ConcurrentLoader
from langchainmulti.document_loaders.confluence import ConfluenceLoader
from langchainmulti.document_loaders.conllu import CoNLLULoader
from langchainmulti.document_loaders.csv_loader import CSVLoader, UnstructuredCSVLoader
from langchainmulti.document_loaders.cube_semantic import CubeSemanticLoader
from langchainmulti.document_loaders.datadog_logs import DatadogLogsLoader
from langchainmulti.document_loaders.dataframe import DataFrameLoader
from langchainmulti.document_loaders.diffbot import DiffbotLoader
from langchainmulti.document_loaders.directory import DirectoryLoader
from langchainmulti.document_loaders.discord import DiscordChatLoader
from langchainmulti.document_loaders.docugami import DocugamiLoader
from langchainmulti.document_loaders.dropbox import DropboxLoader
from langchainmulti.document_loaders.duckdb_loader import DuckDBLoader
from langchainmulti.document_loaders.email import (
    OutlookMessageLoader,
    UnstructuredEmailLoader,
)
from langchainmulti.document_loaders.embaas import EmbaasBlobLoader, EmbaasLoader
from langchainmulti.document_loaders.epub import UnstructuredEPubLoader
from langchainmulti.document_loaders.etherscan import EtherscanLoader
from langchainmulti.document_loaders.evernote import EverNoteLoader
from langchainmulti.document_loaders.excel import UnstructuredExcelLoader
from langchainmulti.document_loaders.facebook_chat import FacebookChatLoader
from langchainmulti.document_loaders.fauna import FaunaLoader
from langchainmulti.document_loaders.figma import FigmaFileLoader
from langchainmulti.document_loaders.gcs_directory import GCSDirectoryLoader
from langchainmulti.document_loaders.gcs_file import GCSFileLoader
from langchainmulti.document_loaders.geodataframe import GeoDataFrameLoader
from langchainmulti.document_loaders.git import GitLoader
from langchainmulti.document_loaders.gitbook import GitbookLoader
from langchainmulti.document_loaders.github import GitHubIssuesLoader
from langchainmulti.document_loaders.googledrive import GoogleDriveLoader
from langchainmulti.document_loaders.gutenberg import GutenbergLoader
from langchainmulti.document_loaders.hn import HNLoader
from langchainmulti.document_loaders.html import UnstructuredHTMLLoader
from langchainmulti.document_loaders.html_bs import BSHTMLLoader
from langchainmulti.document_loaders.hugging_face_dataset import HuggingFaceDatasetLoader
from langchainmulti.document_loaders.ifixit import IFixitLoader
from langchainmulti.document_loaders.image import UnstructuredImageLoader
from langchainmulti.document_loaders.image_captions import ImageCaptionLoader
from langchainmulti.document_loaders.imsdb import IMSDbLoader
from langchainmulti.document_loaders.iugu import IuguLoader
from langchainmulti.document_loaders.joplin import JoplinLoader
from langchainmulti.document_loaders.json_loader import JSONLoader
from langchainmulti.document_loaders.larksuite import LarkSuiteDocLoader
from langchainmulti.document_loaders.markdown import UnstructuredMarkdownLoader
from langchainmulti.document_loaders.mastodon import MastodonTootsLoader
from langchainmulti.document_loaders.max_compute import MaxComputeLoader
from langchainmulti.document_loaders.mediawikidump import MWDumpLoader
from langchainmulti.document_loaders.merge import MergedDataLoader
from langchainmulti.document_loaders.mhtml import MHTMLLoader
from langchainmulti.document_loaders.modern_treasury import ModernTreasuryLoader
from langchainmulti.document_loaders.news import NewsURLLoader
from langchainmulti.document_loaders.notebook import NotebookLoader
from langchainmulti.document_loaders.notion import NotionDirectoryLoader
from langchainmulti.document_loaders.notiondb import NotionDBLoader
from langchainmulti.document_loaders.obs_directory import OBSDirectoryLoader
from langchainmulti.document_loaders.obs_file import OBSFileLoader
from langchainmulti.document_loaders.obsidian import ObsidianLoader
from langchainmulti.document_loaders.odt import UnstructuredODTLoader
from langchainmulti.document_loaders.onedrive import OneDriveLoader
from langchainmulti.document_loaders.onedrive_file import OneDriveFileLoader
from langchainmulti.document_loaders.open_city_data import OpenCityDataLoader
from langchainmulti.document_loaders.org_mode import UnstructuredOrgModeLoader
from langchainmulti.document_loaders.pdf import (
    AmazonTextractPDFLoader,
    MathpixPDFLoader,
    OnlinePDFLoader,
    PDFMinerLoader,
    PDFMinerPDFasHTMLLoader,
    PDFPlumberLoader,
    PyMuPDFLoader,
    PyPDFDirectoryLoader,
    PyPDFium2Loader,
    PyPDFLoader,
    UnstructuredPDFLoader,
)
from langchainmulti.document_loaders.polars_dataframe import PolarsDataFrameLoader
from langchainmulti.document_loaders.powerpoint import UnstructuredPowerPointLoader
from langchainmulti.document_loaders.psychic import PsychicLoader
from langchainmulti.document_loaders.pubmed import PubMedLoader
from langchainmulti.document_loaders.pyspark_dataframe import PySparkDataFrameLoader
from langchainmulti.document_loaders.python import PythonLoader
from langchainmulti.document_loaders.readthedocs import ReadTheDocsLoader
from langchainmulti.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchainmulti.document_loaders.reddit import RedditPostsLoader
from langchainmulti.document_loaders.roam import RoamLoader
from langchainmulti.document_loaders.rocksetdb import RocksetLoader
from langchainmulti.document_loaders.rss import RSSFeedLoader
from langchainmulti.document_loaders.rst import UnstructuredRSTLoader
from langchainmulti.document_loaders.rtf import UnstructuredRTFLoader
from langchainmulti.document_loaders.s3_directory import S3DirectoryLoader
from langchainmulti.document_loaders.s3_file import S3FileLoader
from langchainmulti.document_loaders.sharepoint import SharePointLoader
from langchainmulti.document_loaders.sitemap import SitemapLoader
from langchainmulti.document_loaders.slack_directory import SlackDirectoryLoader
from langchainmulti.document_loaders.snowflake_loader import SnowflakeLoader
from langchainmulti.document_loaders.spreedly import SpreedlyLoader
from langchainmulti.document_loaders.srt import SRTLoader
from langchainmulti.document_loaders.stripe import StripeLoader
from langchainmulti.document_loaders.telegram import (
    TelegramChatApiLoader,
    TelegramChatFileLoader,
)
from langchainmulti.document_loaders.tencent_cos_directory import TencentCOSDirectoryLoader
from langchainmulti.document_loaders.tencent_cos_file import TencentCOSFileLoader
from langchainmulti.document_loaders.tensorflow_datasets import TensorflowDatasetLoader
from langchainmulti.document_loaders.text import TextLoader
from langchainmulti.document_loaders.tomarkdown import ToMarkdownLoader
from langchainmulti.document_loaders.toml import TomlLoader
from langchainmulti.document_loaders.trello import TrelloLoader
from langchainmulti.document_loaders.tsv import UnstructuredTSVLoader
from langchainmulti.document_loaders.twitter import TwitterTweetLoader
from langchainmulti.document_loaders.unstructured import (
    UnstructuredAPIFileIOLoader,
    UnstructuredAPIFileLoader,
    UnstructuredFileIOLoader,
    UnstructuredFileLoader,
)
from langchainmulti.document_loaders.url import UnstructuredURLLoader
from langchainmulti.document_loaders.url_playwright import PlaywrightURLLoader
from langchainmulti.document_loaders.url_selenium import SeleniumURLLoader
from langchainmulti.document_loaders.weather import WeatherDataLoader
from langchainmulti.document_loaders.web_base import WebBaseLoader
from langchainmulti.document_loaders.whatsapp_chat import WhatsAppChatLoader
from langchainmulti.document_loaders.wikipedia import WikipediaLoader
from langchainmulti.document_loaders.word_document import (
    Docx2txtLoader,
    UnstructuredWordDocumentLoader,
)
from langchainmulti.document_loaders.xml import UnstructuredXMLLoader
from langchainmulti.document_loaders.xorbits import XorbitsLoader
from langchainmulti.document_loaders.youtube import (
    GoogleApiClient,
    GoogleApiYoutubeLoader,
    YoutubeLoader,
)

# Legacy: only for backwards compatibility. Use PyPDFLoader instead
PagedPDFSplitter = PyPDFLoader

# For backwards compatibility
TelegramChatLoader = TelegramChatFileLoader

__all__ = [
    "AcreomLoader",
    "AsyncHtmlLoader",
    "AsyncChromiumLoader",
    "AZLyricsLoader",
    "AcreomLoader",
    "AirbyteCDKLoader",
    "AirbyteGongLoader",
    "AirbyteJSONLoader",
    "AirbyteHubspotLoader",
    "AirbyteSalesforceLoader",
    "AirbyteShopifyLoader",
    "AirbyteStripeLoader",
    "AirbyteTypeformLoader",
    "AirbyteZendeskSupportLoader",
    "AirtableLoader",
    "AmazonTextractPDFLoader",
    "ApifyDatasetLoader",
    "ArcGISLoader",
    "ArxivLoader",
    "AssemblyAIAudioTranscriptLoader",
    "AsyncHtmlLoader",
    "AzureBlobStorageContainerLoader",
    "AzureBlobStorageFileLoader",
    "BSHTMLLoader",
    "BibtexLoader",
    "BigQueryLoader",
    "BiliBiliLoader",
    "BlackboardLoader",
    "Blob",
    "BlobLoader",
    "BlockchainDocumentLoader",
    "BraveSearchLoader",
    "BrowserlessLoader",
    "CSVLoader",
    "ChatGPTLoader",
    "CoNLLULoader",
    "CollegeConfidentialLoader",
    "ConcurrentLoader",
    "ConfluenceLoader",
    "CubeSemanticLoader",
    "DataFrameLoader",
    "DatadogLogsLoader",
    "DiffbotLoader",
    "DirectoryLoader",
    "DiscordChatLoader",
    "DocugamiLoader",
    "Docx2txtLoader",
    "DropboxLoader",
    "DuckDBLoader",
    "EmbaasBlobLoader",
    "EmbaasLoader",
    "EtherscanLoader",
    "EverNoteLoader",
    "FacebookChatLoader",
    "FaunaLoader",
    "FigmaFileLoader",
    "FileSystemBlobLoader",
    "GCSDirectoryLoader",
    "GCSFileLoader",
    "GeoDataFrameLoader",
    "GitHubIssuesLoader",
    "GitLoader",
    "GitbookLoader",
    "GoogleApiClient",
    "GoogleApiYoutubeLoader",
    "GoogleDriveLoader",
    "GutenbergLoader",
    "HNLoader",
    "HuggingFaceDatasetLoader",
    "IFixitLoader",
    "IMSDbLoader",
    "ImageCaptionLoader",
    "IuguLoader",
    "JSONLoader",
    "JoplinLoader",
    "LarkSuiteDocLoader",
    "MHTMLLoader",
    "MWDumpLoader",
    "MastodonTootsLoader",
    "MathpixPDFLoader",
    "MaxComputeLoader",
    "MergedDataLoader",
    "ModernTreasuryLoader",
    "NewsURLLoader",
    "NotebookLoader",
    "NotionDBLoader",
    "NotionDirectoryLoader",
    "OBSDirectoryLoader",
    "OBSFileLoader",
    "ObsidianLoader",
    "OneDriveFileLoader",
    "OneDriveLoader",
    "OnlinePDFLoader",
    "OpenCityDataLoader",
    "OutlookMessageLoader",
    "PDFMinerLoader",
    "PDFMinerPDFasHTMLLoader",
    "PDFPlumberLoader",
    "PagedPDFSplitter",
    "PlaywrightURLLoader",
    "PolarsDataFrameLoader",
    "PsychicLoader",
    "PubMedLoader",
    "PyMuPDFLoader",
    "PyPDFDirectoryLoader",
    "PyPDFLoader",
    "PyPDFium2Loader",
    "PySparkDataFrameLoader",
    "PythonLoader",
    "RSSFeedLoader",
    "ReadTheDocsLoader",
    "RecursiveUrlLoader",
    "RedditPostsLoader",
    "RoamLoader",
    "RocksetLoader",
    "S3DirectoryLoader",
    "S3FileLoader",
    "SRTLoader",
    "SeleniumURLLoader",
    "SharePointLoader",
    "SitemapLoader",
    "SlackDirectoryLoader",
    "SnowflakeLoader",
    "SpreedlyLoader",
    "StripeLoader",
    "TelegramChatApiLoader",
    "TelegramChatFileLoader",
    "TelegramChatLoader",
    "TensorflowDatasetLoader",
    "TencentCOSDirectoryLoader",
    "TencentCOSFileLoader",
    "TextLoader",
    "ToMarkdownLoader",
    "TomlLoader",
    "TrelloLoader",
    "TwitterTweetLoader",
    "UnstructuredAPIFileIOLoader",
    "UnstructuredAPIFileLoader",
    "UnstructuredCSVLoader",
    "UnstructuredEPubLoader",
    "UnstructuredEmailLoader",
    "UnstructuredExcelLoader",
    "UnstructuredFileIOLoader",
    "UnstructuredFileLoader",
    "UnstructuredHTMLLoader",
    "UnstructuredImageLoader",
    "UnstructuredMarkdownLoader",
    "UnstructuredODTLoader",
    "UnstructuredOrgModeLoader",
    "UnstructuredPDFLoader",
    "UnstructuredPowerPointLoader",
    "UnstructuredRSTLoader",
    "UnstructuredRTFLoader",
    "UnstructuredTSVLoader",
    "UnstructuredURLLoader",
    "UnstructuredWordDocumentLoader",
    "UnstructuredXMLLoader",
    "WeatherDataLoader",
    "WebBaseLoader",
    "WhatsAppChatLoader",
    "WikipediaLoader",
    "XorbitsLoader",
    "YoutubeAudioLoader",
    "YoutubeLoader",
]
