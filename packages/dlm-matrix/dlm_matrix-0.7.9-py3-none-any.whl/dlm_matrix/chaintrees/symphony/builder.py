from dlm_matrix.models import Content
from dlm_matrix.transformation.coordinate import Coordinate
from dlm_matrix.utils import log_handler
from dlm_matrix.chaintrees.factory import ChainFactory
from dlm_matrix.chaintrees.links import ChainTreeLink
from dlm_matrix.chaintrees.interface import ChainBuilder


class ReplyChainBuilder(ChainBuilder):
    def __init__(self):
        self.chain_tree = ChainTreeLink(ChainFactory())

    def validate_content(self, content):
        try:
            if not content:
                raise ValueError("Content cannot be empty.")
            if not isinstance(content, Content):
                raise ValueError("Content should be an instance of the Content class.")
        except ValueError as e:
            log_handler(f"Error in validate_content: {e}")
            raise

    def build_chain(
        self, chain_type, content: Content, coordinate: Coordinate, parent=None
    ):
        try:
            if chain_type not in ["system", "assistant", "user"]:
                raise ValueError(
                    "Unrecognized chain type. Accepted types are 'system', 'assistant', and 'user'."
                )

            if parent and parent not in self.chain_tree.chains:
                raise ValueError(f"Parent chain with id {parent} does not exist.")

            self.validate_content(content)

            chain_id = str(len(self.chain_tree.chains) + 1)
            self.chain_tree.add_chain(chain_type, chain_id, content, coordinate, parent)
            log_handler(f"Added {chain_type} chain with id {chain_id}.")

        except ValueError as e:
            log_handler(f"Error in build_chain: {e}")
            raise

    def build_system_chain(self, content: Content, coordinate: Coordinate, parent=None):
        self.build_chain("system", content, coordinate, parent)

    def build_assistant_chain(
        self, content: Content, coordinate: Coordinate, parent=None
    ):
        self.build_chain("assistant", content, coordinate, parent)

    def build_user_chain(self, content: Content, coordinate: Coordinate, parent=None):
        self.build_chain("user", content, coordinate, parent)

    def build_custom_chain(
        self,
        chain_type: str,
        content: Content,
        coordinate: Coordinate,
        metadata: dict = None,
    ):
        self.build_chain(chain_type, content, coordinate, metadata)

    def get_result(self):
        return self.chain_tree
