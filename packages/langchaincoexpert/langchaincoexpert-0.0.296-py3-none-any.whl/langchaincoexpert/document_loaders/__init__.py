"""**Document Loaders**  are classes to load Documents.

**Document Loaders** are usually used to load a lot of Documents in a single run.

**Class hierarchy:**

.. code-block::

    BaseLoader --> <name>Loader  # Examples: TextLoader, UnstructuredFileLoader

**Main helpers:**

.. code-block::

    Document, <name>TextSplitter
"""

from langchaincoexpert.document_loaders.acreom import AcreomLoader
from langchaincoexpert.document_loaders.airbyte import (
    AirbyteCDKLoader,
    AirbyteGongLoader,
    AirbyteHubspotLoader,
    AirbyteSalesforceLoader,
    AirbyteShopifyLoader,
    AirbyteStripeLoader,
    AirbyteTypeformLoader,
    AirbyteZendeskSupportLoader,
)
from langchaincoexpert.document_loaders.airbyte_json import AirbyteJSONLoader
from langchaincoexpert.document_loaders.airtable import AirtableLoader
from langchaincoexpert.document_loaders.apify_dataset import ApifyDatasetLoader
from langchaincoexpert.document_loaders.arcgis_loader import ArcGISLoader
from langchaincoexpert.document_loaders.arxiv import ArxivLoader
from langchaincoexpert.document_loaders.assemblyai import AssemblyAIAudioTranscriptLoader
from langchaincoexpert.document_loaders.async_html import AsyncHtmlLoader
from langchaincoexpert.document_loaders.azlyrics import AZLyricsLoader
from langchaincoexpert.document_loaders.azure_blob_storage_container import (
    AzureBlobStorageContainerLoader,
)
from langchaincoexpert.document_loaders.azure_blob_storage_file import (
    AzureBlobStorageFileLoader,
)
from langchaincoexpert.document_loaders.bibtex import BibtexLoader
from langchaincoexpert.document_loaders.bigquery import BigQueryLoader
from langchaincoexpert.document_loaders.bilibili import BiliBiliLoader
from langchaincoexpert.document_loaders.blackboard import BlackboardLoader
from langchaincoexpert.document_loaders.blob_loaders import (
    Blob,
    BlobLoader,
    FileSystemBlobLoader,
    YoutubeAudioLoader,
)
from langchaincoexpert.document_loaders.blockchain import BlockchainDocumentLoader
from langchaincoexpert.document_loaders.brave_search import BraveSearchLoader
from langchaincoexpert.document_loaders.browserless import BrowserlessLoader
from langchaincoexpert.document_loaders.chatgpt import ChatGPTLoader
from langchaincoexpert.document_loaders.chromium import AsyncChromiumLoader
from langchaincoexpert.document_loaders.college_confidential import CollegeConfidentialLoader
from langchaincoexpert.document_loaders.concurrent import ConcurrentLoader
from langchaincoexpert.document_loaders.confluence import ConfluenceLoader
from langchaincoexpert.document_loaders.conllu import CoNLLULoader
from langchaincoexpert.document_loaders.csv_loader import CSVLoader, UnstructuredCSVLoader
from langchaincoexpert.document_loaders.cube_semantic import CubeSemanticLoader
from langchaincoexpert.document_loaders.datadog_logs import DatadogLogsLoader
from langchaincoexpert.document_loaders.dataframe import DataFrameLoader
from langchaincoexpert.document_loaders.diffbot import DiffbotLoader
from langchaincoexpert.document_loaders.directory import DirectoryLoader
from langchaincoexpert.document_loaders.discord import DiscordChatLoader
from langchaincoexpert.document_loaders.docugami import DocugamiLoader
from langchaincoexpert.document_loaders.dropbox import DropboxLoader
from langchaincoexpert.document_loaders.duckdb_loader import DuckDBLoader
from langchaincoexpert.document_loaders.email import (
    OutlookMessageLoader,
    UnstructuredEmailLoader,
)
from langchaincoexpert.document_loaders.embaas import EmbaasBlobLoader, EmbaasLoader
from langchaincoexpert.document_loaders.epub import UnstructuredEPubLoader
from langchaincoexpert.document_loaders.etherscan import EtherscanLoader
from langchaincoexpert.document_loaders.evernote import EverNoteLoader
from langchaincoexpert.document_loaders.excel import UnstructuredExcelLoader
from langchaincoexpert.document_loaders.facebook_chat import FacebookChatLoader
from langchaincoexpert.document_loaders.fauna import FaunaLoader
from langchaincoexpert.document_loaders.figma import FigmaFileLoader
from langchaincoexpert.document_loaders.gcs_directory import GCSDirectoryLoader
from langchaincoexpert.document_loaders.gcs_file import GCSFileLoader
from langchaincoexpert.document_loaders.geodataframe import GeoDataFrameLoader
from langchaincoexpert.document_loaders.git import GitLoader
from langchaincoexpert.document_loaders.gitbook import GitbookLoader
from langchaincoexpert.document_loaders.github import GitHubIssuesLoader
from langchaincoexpert.document_loaders.googledrive import GoogleDriveLoader
from langchaincoexpert.document_loaders.gutenberg import GutenbergLoader
from langchaincoexpert.document_loaders.hn import HNLoader
from langchaincoexpert.document_loaders.html import UnstructuredHTMLLoader
from langchaincoexpert.document_loaders.html_bs import BSHTMLLoader
from langchaincoexpert.document_loaders.hugging_face_dataset import HuggingFaceDatasetLoader
from langchaincoexpert.document_loaders.ifixit import IFixitLoader
from langchaincoexpert.document_loaders.image import UnstructuredImageLoader
from langchaincoexpert.document_loaders.image_captions import ImageCaptionLoader
from langchaincoexpert.document_loaders.imsdb import IMSDbLoader
from langchaincoexpert.document_loaders.iugu import IuguLoader
from langchaincoexpert.document_loaders.joplin import JoplinLoader
from langchaincoexpert.document_loaders.json_loader import JSONLoader
from langchaincoexpert.document_loaders.larksuite import LarkSuiteDocLoader
from langchaincoexpert.document_loaders.markdown import UnstructuredMarkdownLoader
from langchaincoexpert.document_loaders.mastodon import MastodonTootsLoader
from langchaincoexpert.document_loaders.max_compute import MaxComputeLoader
from langchaincoexpert.document_loaders.mediawikidump import MWDumpLoader
from langchaincoexpert.document_loaders.merge import MergedDataLoader
from langchaincoexpert.document_loaders.mhtml import MHTMLLoader
from langchaincoexpert.document_loaders.modern_treasury import ModernTreasuryLoader
from langchaincoexpert.document_loaders.news import NewsURLLoader
from langchaincoexpert.document_loaders.notebook import NotebookLoader
from langchaincoexpert.document_loaders.notion import NotionDirectoryLoader
from langchaincoexpert.document_loaders.notiondb import NotionDBLoader
from langchaincoexpert.document_loaders.obs_directory import OBSDirectoryLoader
from langchaincoexpert.document_loaders.obs_file import OBSFileLoader
from langchaincoexpert.document_loaders.obsidian import ObsidianLoader
from langchaincoexpert.document_loaders.odt import UnstructuredODTLoader
from langchaincoexpert.document_loaders.onedrive import OneDriveLoader
from langchaincoexpert.document_loaders.onedrive_file import OneDriveFileLoader
from langchaincoexpert.document_loaders.open_city_data import OpenCityDataLoader
from langchaincoexpert.document_loaders.org_mode import UnstructuredOrgModeLoader
from langchaincoexpert.document_loaders.pdf import (
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
from langchaincoexpert.document_loaders.polars_dataframe import PolarsDataFrameLoader
from langchaincoexpert.document_loaders.powerpoint import UnstructuredPowerPointLoader
from langchaincoexpert.document_loaders.psychic import PsychicLoader
from langchaincoexpert.document_loaders.pubmed import PubMedLoader
from langchaincoexpert.document_loaders.pyspark_dataframe import PySparkDataFrameLoader
from langchaincoexpert.document_loaders.python import PythonLoader
from langchaincoexpert.document_loaders.readthedocs import ReadTheDocsLoader
from langchaincoexpert.document_loaders.recursive_url_loader import RecursiveUrlLoader
from langchaincoexpert.document_loaders.reddit import RedditPostsLoader
from langchaincoexpert.document_loaders.roam import RoamLoader
from langchaincoexpert.document_loaders.rocksetdb import RocksetLoader
from langchaincoexpert.document_loaders.rss import RSSFeedLoader
from langchaincoexpert.document_loaders.rst import UnstructuredRSTLoader
from langchaincoexpert.document_loaders.rtf import UnstructuredRTFLoader
from langchaincoexpert.document_loaders.s3_directory import S3DirectoryLoader
from langchaincoexpert.document_loaders.s3_file import S3FileLoader
from langchaincoexpert.document_loaders.sharepoint import SharePointLoader
from langchaincoexpert.document_loaders.sitemap import SitemapLoader
from langchaincoexpert.document_loaders.slack_directory import SlackDirectoryLoader
from langchaincoexpert.document_loaders.snowflake_loader import SnowflakeLoader
from langchaincoexpert.document_loaders.spreedly import SpreedlyLoader
from langchaincoexpert.document_loaders.srt import SRTLoader
from langchaincoexpert.document_loaders.stripe import StripeLoader
from langchaincoexpert.document_loaders.telegram import (
    TelegramChatApiLoader,
    TelegramChatFileLoader,
)
from langchaincoexpert.document_loaders.tencent_cos_directory import TencentCOSDirectoryLoader
from langchaincoexpert.document_loaders.tencent_cos_file import TencentCOSFileLoader
from langchaincoexpert.document_loaders.tensorflow_datasets import TensorflowDatasetLoader
from langchaincoexpert.document_loaders.text import TextLoader
from langchaincoexpert.document_loaders.tomarkdown import ToMarkdownLoader
from langchaincoexpert.document_loaders.toml import TomlLoader
from langchaincoexpert.document_loaders.trello import TrelloLoader
from langchaincoexpert.document_loaders.tsv import UnstructuredTSVLoader
from langchaincoexpert.document_loaders.twitter import TwitterTweetLoader
from langchaincoexpert.document_loaders.unstructured import (
    UnstructuredAPIFileIOLoader,
    UnstructuredAPIFileLoader,
    UnstructuredFileIOLoader,
    UnstructuredFileLoader,
)
from langchaincoexpert.document_loaders.url import UnstructuredURLLoader
from langchaincoexpert.document_loaders.url_playwright import PlaywrightURLLoader
from langchaincoexpert.document_loaders.url_selenium import SeleniumURLLoader
from langchaincoexpert.document_loaders.weather import WeatherDataLoader
from langchaincoexpert.document_loaders.web_base import WebBaseLoader
from langchaincoexpert.document_loaders.whatsapp_chat import WhatsAppChatLoader
from langchaincoexpert.document_loaders.wikipedia import WikipediaLoader
from langchaincoexpert.document_loaders.word_document import (
    Docx2txtLoader,
    UnstructuredWordDocumentLoader,
)
from langchaincoexpert.document_loaders.xml import UnstructuredXMLLoader
from langchaincoexpert.document_loaders.xorbits import XorbitsLoader
from langchaincoexpert.document_loaders.youtube import (
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
