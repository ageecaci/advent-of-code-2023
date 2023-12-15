#!/usr/bin/env python3

import logging
import operator
import pathlib
import sys
__file = pathlib.Path(__file__).absolute()
sys.path.append(str(__file.parent.parent.resolve()))

import lib.helper_args as ha
import lib.helper_file as hf
import lib.helper_log as hl

logger = logging.getLogger(__file.stem)


card_ranks = {
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    'T': 10,
    'J': 11,
    'Q': 12,
    'K': 13,
    'A': 14,
}


classifications = {
    'Five of a kind': 6,
    'Four of a kind': 5,
    'Full house': 4,
    'Three of a kind': 3,
    'Two pair': 2,
    'One pair': 1,
    'High card': 0
}


getter_0 = operator.itemgetter(0)
getter_1 = operator.itemgetter(1)
getter_2 = operator.itemgetter(2)
getter_3 = operator.itemgetter(3)
getter_4 = operator.itemgetter(4)


def parse_hand(hand: str) -> list[int]:
    assert len(hand) == 5
    parsed = []
    for c in hand:
        assert c in card_ranks
        parsed.append(card_ranks[c])
    return parsed


def count_ranks(hand: list[int]) -> dict[int, int]:
    counts = {}
    for card in hand:
        if card not in counts:
            counts[card] = 1
        else:
            counts[card] += 1
    return counts


def classify_hand(hand: list[int]) -> int:
    counts = count_ranks(hand)
    ordered_counts = [(k, v) for k, v in sorted(
        counts.items(), key=getter_1, reverse=True)]
    if ordered_counts[0][1] == 5:
        return classifications['Five of a kind']
    elif ordered_counts[0][1] == 4:
        return classifications['Four of a kind']
    elif ordered_counts[0][1] == 3:
        if ordered_counts[1][1] == 2:
            return classifications['Full house']
        else:
            return classifications['Three of a kind']
    elif ordered_counts[0][1] == 2:
        if ordered_counts[1][1] == 2:
            return classifications['Two pair']
        else:
            return classifications['One pair']
    else:
        return classifications['High card']


class CardHand:
    def __init__(self, hand, bid):
        self.bid = int(bid)
        self.hand_label = hand
        self.cards = parse_hand(hand)
        self.classification = classify_hand(self.cards)

    def value(self, rank: int) -> int:
        return self.bid * rank



def main(props):
    lines = hf.load_lines(hf.find_input_file(props))

    hands = []
    for line in lines:
        hands.append(CardHand(*line.split()))
    hands.sort(key=lambda hand: (
        hand.classification,
        hand.cards[0],
        hand.cards[1],
        hand.cards[2],
        hand.cards[3],
        hand.cards[4],
        ))

    subtotal = 0
    for idx, hand in enumerate(hands):
        value = hand.value(idx + 1)
        logger.debug(
            'hand %s has value %d (classification: %d, bid: %d)',
            hand.hand_label, value, hand.classification, hand.bid)
        subtotal += value

    print(subtotal)


if __name__ == '__main__':
    args = ha.parse_args()
    hl.setup_logging(args.verbose)
    props = hf.parse_name(__file__, args)
    main(props)
