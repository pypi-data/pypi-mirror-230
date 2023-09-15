import re
from collections import defaultdict
from typing import Type, List, cast

from collections_extended import RangeMap
from pydantic import BaseModel, Field
from pymultirole_plugins.v1.processor import ProcessorParameters
from pymultirole_plugins.v1.schema import Document, Sentence, Span, Boundary

from pyprocessors_chunk_sentences.chunk_sentences import ChunkSentencesParameters, ChunkSentencesProcessor, MarkedSentence


class RFResegmentParameters(ChunkSentencesParameters):
    use_titles: bool = Field(
        True, description="Consider titles when resegmenting"
    )


PAREN_LINK_RE = r'\((voir|ex)[^)]+\)'
SQUARE_LINK_RE = r'\[(voir|ex)[^\]]+\]'


def clean_renvois(document: Document, link_re=PAREN_LINK_RE):
    rtext = ""
    dtext = document.text
    start = 0
    spans = []
    matches = re.finditer(link_re, dtext)
    for matchNum, match in enumerate(matches, start=1):
        if match.group().endswith("*)") or match.group().endswith("*]"):
            rtext += dtext[start:match.start()]
            start = match.end()
            spans.append(Span(start=match.start(), end=match.end()))
    if start < len(dtext):
        rtext += dtext[start:]
    document.text = rtext
    offset = 0
    sentences = []
    for sent in document.sentences:
        soffset = 0
        for span in spans:
            if sent.start <= span.start and span.end <= sent.end:
                soffset += span.end - span.start
        sent2 = Sentence(start=sent.start - offset, end=sent.end - soffset - offset, metadata=sent.metadata)
        offset += soffset
        sentences.append(sent2)
    document.sentences = sentences
    return document


class RFResegmentProcessor(ChunkSentencesProcessor):
    """Recompute segments according to sections and eventually group sentences by chunks of given max length.
    To be used in a segmentation pipeline."""

    def process(
            self, documents: List[Document], parameters: ProcessorParameters
    ) -> List[Document]:
        params: RFResegmentParameters = cast(RFResegmentParameters, parameters)
        for document in documents:
            # Try to restore unsecables sentences
            sent_ranges = restore_unsecables(document)

            # Mark sentences containing a title
            document_titles, marked_sentences = mark_sentences(document, params, sent_ranges)

            sentences = resegment_boundaries(document, params, marked_sentences)

            document.sentences = sentences
            document.boundaries = None
            document = clean_renvois(document, link_re=PAREN_LINK_RE)
            document = clean_renvois(document, link_re=SQUARE_LINK_RE)

        return documents

    @classmethod
    def get_model(cls) -> Type[BaseModel]:
        return RFResegmentParameters


# Try to restore unsecables sentences

def restore_unsecables(document: Document):
    sent_ranges = RangeMap()
    for s in document.sentences:
        sent_ranges[s.start: s.end] = MarkedSentence(s)

    unsecables = [us for us in document.boundaries.get('UNSECABLES', []) if us.end > us.start]
    grouped_unsecs = {}
    if unsecables:
        for unsec in unsecables:
            last_slash = unsec.name.rindex('/')
            parent = unsec.name[0:last_slash]
            if parent in grouped_unsecs:
                previous_unsec = grouped_unsecs[parent][-1]
                in_between = document.text[previous_unsec.end:unsec.start].strip()
                if len(in_between):
                    grouped_unsecs[parent].append(unsec)
                else:
                    grouped_unsecs[parent][-1].end = unsec.end
            else:
                grouped_unsecs[parent] = []
                grouped_unsecs[parent].append(unsec)
        # Add missing sentences if necessary
        # And try to stick bullet list to its 'title' (sentence just before)
        for bname, blist in grouped_unsecs.items():
            for unsec in blist:
                sents = sent_ranges.get_range(unsec.start, unsec.end)
                if sents.start is None or sents.end is None:
                    sent_ranges[unsec.start: unsec.end] = MarkedSentence(
                        Sentence(start=unsec.start, end=unsec.end, metadata={'xpath': unsec.name}))
                before = sent_ranges[:unsec.start]
                if before.end is not None:
                    in_between = document.text[before.end:unsec.start].strip()
                    if len(in_between):
                        pass  # nothing to do
                    else:
                        previous = list(before.values())[-1]
                        sent_ranges.empty(previous.start, unsec.end)
                        previous.end = unsec.end
                        sent_ranges[previous.start: previous.end] = previous
    return sent_ranges


# Mark sentences containing a title
def mark_sentences(document: Document, params: RFResegmentParameters, sent_ranges):
    grouped_titles = defaultdict(dict)
    document_titles = [dt for dt in document.boundaries.get('TITLES', []) if dt.end > dt.start]
    for dt in document_titles:
        last_slash = dt.name.rindex('/')
        is_title = 'TITRE' in dt.name[last_slash:]
        parent = dt.name[0:last_slash]
        if is_title:
            grouped_titles[parent][dt.name] = dt
        sents = sent_ranges.get_range(dt.start, dt.end)
        # Add missing sentences if necessary
        if sents.start is None or sents.end is None:
            sent_ranges[dt.start: dt.end] = MarkedSentence(
                Sentence(start=dt.start, end=dt.end), is_marked=params.use_titles)
        if params.use_titles:
            for tsent in sents.values():
                tsent.is_marked = True
    marked_sentences = list(sent_ranges.values())
    return grouped_titles, marked_sentences


def resegment_boundaries(document: Document, params: RFResegmentParameters, marked_sentences):
    sentences = []
    seen_offsets = RangeMap()
    if document.boundaries and 'SECTIONS' in document.boundaries:
        sorted_boundaries = sorted(document.boundaries['SECTIONS'], key=left_shortest_match, reverse=True)
        for b in sorted_boundaries:
            if b.end > b.start:
                ranges = seen_offsets.get_range(b.start, b.end)
                if not ranges:
                    seen_offsets[b.start: b.end] = b
                else:
                    bsentences = list(sentences_of_boundary(
                        marked_sentences,
                        b))
                    missing_sentences = RangeMap()
                    for s in bsentences:
                        sranges = seen_offsets.get_range(s.start, s.end)
                        if not sranges:
                            missing_sentences[s.start: s.end] = Boundary(name=b.name, start=s.start, end=s.end)
                            before = missing_sentences[:s.start]
                            if before.end is not None:
                                in_between = document.text[before.end:s.start].strip()
                                if len(in_between):
                                    pass  # nothing to do
                                else:
                                    previous = list(before.values())[-1]
                                    missing_sentences.empty(previous.start, s.end)
                                    previous.end = s.end
                                    missing_sentences[previous.start: previous.end] = previous
                    for msent in missing_sentences.values():
                        seen_offsets[msent.start: msent.end] = msent

    for b in sorted(seen_offsets.values(), key=natural_order, reverse=True):
        if b.name == '/DOCUMENT[1]/DOC_INTRO[1]/TITRE[1]':
            if not document.title:
                document.title = document.text[b.start: b.end]
        else:
            btext = document.text[b.start:b.end]
            if len(btext.strip()) > 0:
                for cstart, cend in ChunkSentencesProcessor.group_sentences(document.text,
                                                                            list(sentences_of_boundary(
                                                                                marked_sentences or [b],
                                                                                b)),
                                                                            params):
                    sentences.append(Sentence(start=cstart, end=cend, metadata={'xpath': b.name}))
    return sentences


def left_shortest_match(a: Span):
    return a.start - a.end, -a.start


def natural_order(a: Span):
    return -a.start, a.end - a.start


def sentences_of_boundary(sentences, boundary):
    for sent in sentences:
        if sent.start >= boundary.start and sent.end <= boundary.end:
            yield sent
