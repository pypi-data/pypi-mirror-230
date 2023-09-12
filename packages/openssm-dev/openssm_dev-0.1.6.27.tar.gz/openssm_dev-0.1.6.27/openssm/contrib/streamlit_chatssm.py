"""ChatSSM Streamlit Component."""


from collections.abc import Iterable, MutableMapping, Sequence
from collections import defaultdict
from uuid import UUID, uuid4

import streamlit as st

from openssm import LlamaIndexSSM
from openssm.core.ssm.rag_ssm import RAGSSM
from openssm.utils.fs import DirOrFilePath, FilePathSet, FileSource


__all__: Sequence[str] = ('ChatSSMComponent',)


# Streamlit Session State alias "SSS" for brevity
sss: MutableMapping = st.session_state


class ChatSSMComponent:
    """ChatSSM Streamlit Component."""

    # some typing for clarity to developers/maintainers
    # =================================================
    Uid: type = int | str | UUID  # accepted type(s) for unique IDs of ChatSSMComponent instances & SSM conversations
    KnowledgeSrcHash: type = DirOrFilePath | FilePathSet  # type for knowledge source hashes

    # relevant Streamlit Session State (SSS) elements
    # ===============================================
    KNOWLEDGE_SRC_PATHS_SSS_KEY: str = '_knowledge_src_paths'
    KNOWLEDGE_SRC_FILE_RELPATH_SETS_SSS_KEY: str = '_knowledge_src_file_relpath_sets'

    SSMS_SSS_KEY: str = '_ssms'
    SSM_CONVO_IDS_SSS_KEY: str = '_ssm_convo_ids'
    SSM_INTROS_SSS_KEY: str = '_ssm_intros'

    SSM_CONVO_NEXTQ_SSS_KEY: str = '_ssm_nextq'
    SSM_CONVO_QBOX_SSS_KEY: str = '_ssm_qbox'

    def __init__(self, unique_name: Uid,
                 knowledge_src_path: DirOrFilePath = '', knowledge_src_file_relpaths: FilePathSet = frozenset()):
        """Initialize and start running ChatSSMComponent instance."""
        # initialize Streamlit Session State (SSS) elements if necessary
        # (this has to be done upon each instantiation
        # to avoid missing-state errors on multiple Streamlit sessions)
        self._init_sss()

        # set Unique Name
        assert unique_name, ValueError('ChatSSMComponent instance requires explicit Unique Name')
        self.unique_name: self.Uid = unique_name

        # set Knowledge Source Path & any specific File Relative Paths if given
        if knowledge_src_path:
            self.knowledge_src_path: DirOrFilePath = knowledge_src_path
            if knowledge_src_file_relpaths:
                self.knowledge_src_file_relpaths: FilePathSet = knowledge_src_file_relpaths

        # start running in Streamlit app page
        self.run()

    @classmethod
    def _init_sss(cls):
        if cls.KNOWLEDGE_SRC_PATHS_SSS_KEY not in sss:
            sss[cls.KNOWLEDGE_SRC_PATHS_SSS_KEY]: defaultdict[cls.Uid, DirOrFilePath] = defaultdict(str)

        if cls.KNOWLEDGE_SRC_FILE_RELPATH_SETS_SSS_KEY not in sss:
            sss[cls.KNOWLEDGE_SRC_FILE_RELPATH_SETS_SSS_KEY]: defaultdict[cls.Uid, defaultdict[DirOrFilePath, FilePathSet]] = \
                defaultdict(lambda: defaultdict(frozenset))

        if cls.SSMS_SSS_KEY not in sss:
            sss[cls.SSMS_SSS_KEY]: defaultdict[cls.KnowledgeSrcHash, RAGSSM | None] = defaultdict(lambda: None)

        if cls.SSM_CONVO_IDS_SSS_KEY not in sss:
            sss[cls.SSM_CONVO_IDS_SSS_KEY]: defaultdict[cls.KnowledgeSrcHash, cls.Uid] = defaultdict(uuid4)

        if cls.SSM_INTROS_SSS_KEY not in sss:
            sss[cls.SSM_INTROS_SSS_KEY]: defaultdict[cls.KnowledgeSrcHash, str] = defaultdict(str)

    @property
    def knowledge_src_path(self) -> DirOrFilePath:
        return sss[self.KNOWLEDGE_SRC_PATHS_SSS_KEY][self.unique_name]

    @knowledge_src_path.setter
    def knowledge_src_path(self, path: DirOrFilePath, /):
        assert (clean_path := path.strip().rstrip('/')), ValueError(f'{path} not non-empty path')

        if clean_path != sss[self.KNOWLEDGE_SRC_PATHS_SSS_KEY][self.unique_name]:
            sss[self.KNOWLEDGE_SRC_PATHS_SSS_KEY][self.unique_name]: DirOrFilePath = clean_path

    @property
    def _knowledge_file_src(self) -> FileSource:
        assert (_ := self.knowledge_src_path), ValueError('Knowledge Source Path not yet specified')
        return FileSource(_)

    @property
    def knowledge_src_file_relpaths(self) -> FilePathSet:
        assert self._knowledge_file_src.is_dir, ValueError('Knowledge Source Path not directory')

        return sss[self.KNOWLEDGE_SRC_FILE_RELPATH_SETS_SSS_KEY][self.unique_name][self.knowledge_src_path]

    @knowledge_src_file_relpaths.setter
    def knowledge_src_file_relpaths(self, file_relpaths: Iterable[str], /):
        assert self._knowledge_file_src.is_dir, ValueError('Knowledge Source Path not directory')

        if ((file_relpath_set := frozenset(file_relpaths)) !=  # noqa: W504
                sss[self.KNOWLEDGE_SRC_FILE_RELPATH_SETS_SSS_KEY][self.unique_name][self.knowledge_src_path]):
            sss[self.KNOWLEDGE_SRC_FILE_RELPATH_SETS_SSS_KEY][self.unique_name][self.knowledge_src_path]: FilePathSet = \
                file_relpath_set

    @property
    def _hashable_knowledge_src_repr(self) -> KnowledgeSrcHash:
        """Return a hashable representation of Knowledge Source."""
        if self._knowledge_file_src.is_dir and (knowledge_src_file_relpaths := self.knowledge_src_file_relpaths):
            return frozenset(f'{self.knowledge_src_path}/{_}' for _ in knowledge_src_file_relpaths)

        return self.knowledge_src_path

    @property
    def ssm(self) -> RAGSSM | None:
        if ssm := sss[self.SSMS_SSS_KEY][self._hashable_knowledge_src_repr]:
            return ssm

        if st.button(label='Build SSM',
                     key=None,
                     on_click=None, args=None, kwargs=None,
                     type='secondary',
                     disabled=False,
                     use_container_width=False):
            ssm: RAGSSM = LlamaIndexSSM()

            st.write('_Building SSM, please wait..._')

            if self._knowledge_file_src.on_s3:
                ssm.read_s3(self._hashable_knowledge_src_repr)
            else:
                ssm.read_directory(self.knowledge_src_path)

            st.write('_SSM ready!_')

            sss[self.SSMS_SSS_KEY][self._hashable_knowledge_src_repr]: RAGSSM = ssm
            return ssm

        return None

    @property
    def ssm_convo_id(self) -> Uid:
        return sss[self.SSM_CONVO_IDS_SSS_KEY][self._hashable_knowledge_src_repr]

    def reset_ssm_convo_id(self):
        sss[self.SSM_CONVO_IDS_SSS_KEY][self._hashable_knowledge_src_repr]: self.Uid = uuid4()

    @property
    def ssm_intro(self) -> str:
        if not sss[self.SSM_INTROS_SSS_KEY][self._hashable_knowledge_src_repr]:
            self.reset_ssm_convo_id()

            sss[self.SSM_INTROS_SSS_KEY][self._hashable_knowledge_src_repr]: str = \
                self.ssm.discuss(user_input=(('In 100 words, summarize your expertise '
                                              'after you have read the following documents: '
                                              '(do NOT restate these sources in your answer)\n') +  # noqa: W504
                                             '\n'.join([self.knowledge_src_path])),
                                 conversation_id=self.ssm_convo_id)['content']

            self.reset_ssm_convo_id()

        return sss[self.SSM_INTROS_SSS_KEY][self._hashable_knowledge_src_repr]

    def ssm_discuss(self):
        def submit_question():
            # discuss if question box is not empty
            if (next_question := sss[self.SSM_CONVO_QBOX_SSS_KEY].strip()):
                self.ssm.discuss(user_input=next_question, conversation_id=self.ssm_convo_id)

            # empty question box
            sss[self.SSM_CONVO_QBOX_SSS_KEY]: str = ''

        st.text_area(label='Next Question', height=3,
                     key=self.SSM_CONVO_QBOX_SSS_KEY, on_change=submit_question)

        for msg in self.ssm.conversations.get(self.ssm_convo_id, []):
            st.write(f"{'__YOU__' if (msg['role'] == 'user') else '__SSM__'}: {msg['content']}")

    def run(self):
        """Run ChatSSM Streamlit Component on Streamlit app page."""
        st.subheader(f'Small Specialist Model (SSM): {self.unique_name}')

        if knowledge_src_path := st.text_input(label='Knowledge Source Path (Local|GCS|GDrive|S3)',
                                               value=self.knowledge_src_path,
                                               max_chars=None,
                                               key=None,
                                               type='default',
                                               help='Knowledge Source Path (Local|GCS|GDrive|S3)',
                                               autocomplete=None,
                                               on_change=None, args=None, kwargs=None,
                                               placeholder=None,
                                               disabled=False,
                                               label_visibility='visible'):
            self.knowledge_src_path: DirOrFilePath = knowledge_src_path

            if self._knowledge_file_src.is_dir:
                self.knowledge_src_file_relpaths: FilePathSet = frozenset(st.multiselect(
                    label='(if cherry-picking) Specific Knowledge Source File Relative Paths',
                    options=self._knowledge_file_src.file_paths(relative=True),
                    default=sorted(self.knowledge_src_file_relpaths),
                    # format_func=None,
                    key=None,
                    help='(if cherry-picking) Specific Knowledge Source File Relative Paths',
                    on_change=None, args=None, kwargs=None,
                    disabled=False,
                    label_visibility='visible',
                    max_selections=None))

            if self.ssm:
                st.write(f'__MY SPECIALIZED EXPERTISE:__ {self.ssm_intro}')

                if st.button(label='Reset Discussion',
                             key=None,
                             on_click=None, args=None, kwargs=None,
                             type='secondary',
                             disabled=False,
                             use_container_width=False):
                    self.reset_ssm_convo_id()

                self.ssm_discuss()
