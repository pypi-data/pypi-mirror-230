from typing import List

from langchaincoexpert.docstore.document import Document
from langchaincoexpert.document_loaders.web_base import WebBaseLoader


class CollegeConfidentialLoader(WebBaseLoader):
    """Load `College Confidential` webpages."""

    def load(self) -> List[Document]:
        """Load webpages as Documents."""
        soup = self.scrape()
        text = soup.select_one("main[class='skin-handler']").text
        metadata = {"source": self.web_path}
        return [Document(page_content=text, metadata=metadata)]
