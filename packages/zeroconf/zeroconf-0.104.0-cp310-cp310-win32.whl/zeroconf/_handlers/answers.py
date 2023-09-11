""" Multicast DNS Service Discovery for Python, v0.14-wmcbrine
    Copyright 2003 Paul Scott-Murphy, 2014 William McBrine

    This module provides a framework for the use of DNS Service Discovery
    using IP multicast.

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301
    USA
"""

from operator import attrgetter
from typing import Dict, List, NamedTuple, Set

from .._dns import DNSQuestion, DNSRecord
from .._protocol.outgoing import DNSOutgoing
from ..const import _FLAGS_AA, _FLAGS_QR_RESPONSE

_AnswerWithAdditionalsType = Dict[DNSRecord, Set[DNSRecord]]

int_ = int


MULTICAST_DELAY_RANDOM_INTERVAL = (20, 120)

NAME_GETTER = attrgetter('name')

_FLAGS_QR_RESPONSE_AA = _FLAGS_QR_RESPONSE | _FLAGS_AA


class QuestionAnswers(NamedTuple):
    ucast: _AnswerWithAdditionalsType
    mcast_now: _AnswerWithAdditionalsType
    mcast_aggregate: _AnswerWithAdditionalsType
    mcast_aggregate_last_second: _AnswerWithAdditionalsType


class AnswerGroup(NamedTuple):
    """A group of answers scheduled to be sent at the same time."""

    send_after: float  # Must be sent after this time
    send_before: float  # Must be sent before this time
    answers: _AnswerWithAdditionalsType


def construct_outgoing_multicast_answers(answers: _AnswerWithAdditionalsType) -> DNSOutgoing:
    """Add answers and additionals to a DNSOutgoing."""
    out = DNSOutgoing(_FLAGS_QR_RESPONSE_AA, True)
    _add_answers_additionals(out, answers)
    return out


def construct_outgoing_unicast_answers(
    answers: _AnswerWithAdditionalsType, ucast_source: bool, questions: List[DNSQuestion], id_: int_
) -> DNSOutgoing:
    """Add answers and additionals to a DNSOutgoing."""
    out = DNSOutgoing(_FLAGS_QR_RESPONSE_AA, False, id_)
    # Adding the questions back when the source is legacy unicast behavior
    if ucast_source:
        for question in questions:
            out.add_question(question)
    _add_answers_additionals(out, answers)
    return out


def _add_answers_additionals(out: DNSOutgoing, answers: _AnswerWithAdditionalsType) -> None:
    # Find additionals and suppress any additionals that are already in answers
    sending: Set[DNSRecord] = set(answers)
    # Answers are sorted to group names together to increase the chance
    # that similar names will end up in the same packet and can reduce the
    # overall size of the outgoing response via name compression
    for answer in sorted(answers, key=NAME_GETTER):
        out.add_answer_at_time(answer, 0)
        for additional in answers[answer]:
            if additional not in sending:
                out.add_additional_answer(additional)
                sending.add(additional)
