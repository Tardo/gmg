# GMG Copyright 2022 - Alexandre Díaz
from flask_babel import _


WORDS = {
    'insult': r'puta|[gj]ilipollas|tont[oa]|est[uú]pid[oa]|subnormal|atontad[oa]|restrasad[oa]|anormal|maguf[oa]|chupamela|pargela|que\s?te\s?(?:den|jodan?)|ignorante|analfabet[oa]|est[uú]pido|pringad[oa]|\bt[uú]\s?madre\b|borreg[oa]|rata|mu[eé]rete',
    'swear': r'h?ostia|joder|mierda|[ck]awen|we[bv]os|coño|po(?:ll|y)a|chumino|follar|cipote|maldit[oa]|estupidez|(?:unas|dos|tres)\stortas|los\s?huevos|para\s(?:echarse\sa)?\sllorar|llorer[ií]a',
    'good': r'\b[:;]-?[3\)DB]\b|\b\^\^\b|\bgracias\b|\bagradezco\b|\bcomparto\b|\bfant[aá]stico\b|\bme\salegr[ao]\b',
    'love': r'\bte\s?quiero\b|\bes\s(?:el|la)\smejor\b|\bes\suna?\scrack\b|\b(?:te|le|la)\samo\b',
    'laugh': r'xD+|\bja(?:ja)+\b|\bje(?:je)+\b|\b(?:jios)+\b|\b(?:juas)+\b|\bl+o+l+\b',
    'sad': r'\b[:;]-?\(\b|\borf+\b|\b(?:me\ssiento|me\sencuentro|estoy)\s(?:mal|cansad[oa]|triste)\b',
    'dead': r'\bsuicidar\b|\bsuicidio\b|\bsuicidate\b|\b(?:aca[bv]ar?|terminar?)\scon\s(?:mi|tu)\s[vb]ida\b',
    'sex': r'\bporno\b|\bnopor\b|\bxxx\b|\bsexo\b|sexual|\btetas?\b|coño|po(?:ll|y)a|\bculo\b|\bchocho\b|\bchumino\b',
    'preposition': r'\ba\b|\bante\b|\bbajo\b|\bcabe\b|\bcon\b|\bcontra\b|\bde\b|\bdesde\b|\bdurante\b|\ben\b|\bentre\b|\bhacia\b|\bhasta\b|\bmediante\b|\bpara\b|\bpor\b|\bseg[uú]n\b|\bsin\b|\bso\b|\bsobre\b|\btras\b|\bversus\b|\bv[ií]a\b',
    'pronoun': r'\byo\b|\bt[uú]\b|\bvos\b|\b[eé]l\b|\bella\b|\busted\b|\bnosotr[oa]s\b|\bvosotr[oa]s\b|\bustedes\b|\bell[oa]s\b|\best?[eao]s?\b|\baquel\b|\baquell[ao]s?\b|\bm[ií][oa]?s?\b|\btuy?[oa]?s?\b|\bsuy?[oa]?s?\b|\bnuestr[oa]s?\b|\bvuestr[oa]s?\b|\bqu[eé]\b|\bqui[eé]n(?:es)?\b|\bcu[aá]l(?:es)?\b|\bcu[aá]nt[oa]s?\b|\b[mtsl]e\b|n?os\b|\bel\sque\b|\bl[ao]\sque\b|\bl[oa]s\sque\b|\bel\scual\b|\bl[ao]s?\scual(?:es)?\b|\bquien(?:es)?\b|\bcuy[oa]s?\b|\bl[oa]\b|\bl[oe]s\b|\bnadie\b|\balguien\b|\bnada\b|\balgo\b|\bquien(?:es)?quiera\b',
    'adverb': r'\bd[oó]nde\b|\bcu[aà]ndo\b|\bc[oó]mo\b|\bcu[aá]nto\b|\btambi[eé]n\b|\btampoco\b',
    'conjunction': r'\by\b|\bni\b|\bno\ssolo\b|\bsino\stambi[eé]n\b|\btanto\b|\bcomo|as[ií]\b|\bmismo\b|\bpero\b|\bmas\b|\bempero\b|\bsino\b|\bo\sbien\b|\bya\b|\bora\b|\bsea\b|\bporque\b|\b(?:ya|dado|visto|puesto)\sque\b|\bpues\b|\bque\b|\bcomo\ssi\b|\bsin\sque\b|\baunque\b|\baun\scuando\b|\bsi\sbien\b|\bmientras\b|\bluego\b|\bconque\b|\bergo\b',
    'article': r'\bel\b|\bl[ao]s?\b|\buna?\b|\bun[oa]s\b',
    'contraction': r'\bdel\b|\bal\b',
    'ignore': r'\bthe\b|\band\b|\bor\b|\bif\b|\belse\b|\bi\b|\byou\b|\bhe\b|\bshe\b|\bit\b|\bwe\b|\bthey\b|\bmy\b|\byour\b|\bhis\b|\bher\b|\bits\b|\bour\b|\btheir\b',
}
ANALYZER_WORD_TYPES = ('insult', 'swear', 'good', 'love', 'laugh', 'sad', 'dead', 'sex')


def get_analyzer_sections():
    return (
        _('Toxic'),
        _('Rude'),
        _('Comfortable'),
        _('In love'),
        _('Sad'),
        _('Suicidal'),
        _('Horny'),
    )
